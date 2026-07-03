#!/usr/bin/env python3
"""Icelandic payslip (launaseðill) calculator — gross ⇄ take-home ⇄ employer cost.

Computes the full monthly payslip decomposition locally, matching the
payday.is calculator semantics field-for-field (verified via the `verify`
subcommand, which calls payday.is and diffs every field):

  Employee side:
    skyldulífeyrir 4% of gross (pre-tax)
    séreign (viðbótarlífeyrissparnaður) 0–4% of gross (pre-tax)
    staðgreiðsla on (gross − pension) via 2026 brackets − persónuafsláttur
    stéttarfélagsgjald (union fee) % of gross, deducted POST-tax
    → payoutAmountSalary (take-home)

  Employer side (the "know your total worth" view):
    mótframlag 11.5% + séreign match 2% + VIRK endurhæfingarsjóður 0.1%
    tryggingagjald 6.35% on (gross + employer pension contributions,
    excluding the VIRK fund)
    → totalCost

Rounding: half-up per line item (matches payday.is).
Stdlib only. Reuses the bracket table from tax.py (same directory).

CLI:
    python3 payslip.py gross 1000000 --union 0.7 --extra-pension 4
    python3 payslip.py total-cost 1208073 --union 0.7 --extra-pension 4
    python3 payslip.py verify --salaries 400000,1000000,2500000 --union 0.7
"""

from __future__ import annotations

import argparse
import json
import math
import urllib.error
import urllib.request

from tax import BRACKETS, PERSONAL_CREDIT_MONTHLY, TAX_YEAR

# Standard rates — override via CLI flags where they differ
PENSION_EMPLOYEE_PCT = 4.0     # skyldulífeyrir, launþegahluti
PENSION_EMPLOYER_PCT = 11.5    # mótframlag
REHAB_FUND_PCT = 0.1           # VIRK endurhæfingarsjóður (employer)
INSURANCE_FEE_PCT = 6.35       # tryggingagjald (employer payroll tax)

PAYDAY_API = "https://payday.is/is/ajax/calculator/calculateSalary/"


def _round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def compute(
    gross: float,
    *,
    union_pct: float = 0.0,
    extra_pension_employee_pct: float = 0.0,
    extra_pension_employer_pct: float = 0.0,
    allowance_pct: float = 100.0,
    pension_employee_pct: float = PENSION_EMPLOYEE_PCT,
    pension_employer_pct: float = PENSION_EMPLOYER_PCT,
    insurance_fee_pct: float = INSURANCE_FEE_PCT,
    rehab_fund_pct: float = REHAB_FUND_PCT,
) -> dict:
    """Full payslip decomposition for one month's gross salary.

    Returns payday.is-compatible field names (camelCase) so results can be
    diffed against the live calculator.
    """
    pension_employee = _round_half_up(gross * pension_employee_pct / 100)
    extra_pension_employee = _round_half_up(gross * extra_pension_employee_pct / 100)
    employee_pension_total = pension_employee + extra_pension_employee

    # Staðgreiðsla on gross minus pre-tax pension, per bracket, half-up per step
    taxable = gross - employee_pension_total
    step_amounts = []
    prev_cap = 0.0
    for cap, rate in BRACKETS:
        band = max(0.0, min(taxable, cap) - prev_cap)
        step_amounts.append(_round_half_up(band * rate))
        prev_cap = cap
    allowance = _round_half_up(PERSONAL_CREDIT_MONTHLY * allowance_pct / 100)
    income_tax = max(0, sum(step_amounts) - allowance)

    union_fee = _round_half_up(gross * union_pct / 100)  # post-tax deduction

    take_home = int(gross) - employee_pension_total - income_tax - union_fee

    # Employer side
    pension_employer = _round_half_up(gross * pension_employer_pct / 100)
    extra_pension_employer = _round_half_up(gross * extra_pension_employer_pct / 100)
    rehab_fund = _round_half_up(gross * rehab_fund_pct / 100)
    employer_pension_total = pension_employer + extra_pension_employer + rehab_fund
    # tryggingagjald base: gross + employer pension contributions, EXCLUDING the VIRK fund
    insurance_fee = _round_half_up(
        (gross + pension_employer + extra_pension_employer) * insurance_fee_pct / 100
    )
    total_cost = int(gross) + employer_pension_total + insurance_fee

    return {
        "salary": int(gross),
        "totalCost": total_cost,
        "payoutAmountSalary": take_home,
        "pensionContributionEmployeeAmount": pension_employee,
        "additionalPensionContributionEmployeeAmount": extra_pension_employee,
        "pensionContributionEmployeeTotalAmount": employee_pension_total,
        "incomeTaxStep1Amount": step_amounts[0],
        "incomeTaxStep2Amount": step_amounts[1] if len(step_amounts) > 1 else 0,
        "incomeTaxStep3Amount": step_amounts[2] if len(step_amounts) > 2 else 0,
        "personalTaxAllowanceAmount": allowance,
        "incomeTaxEmployeeTotalAmount": income_tax,
        "unionFeeAmount": union_fee,
        "pensionContributionEmployerAmount": pension_employer,
        "additionalPensionContributionEmployerAmount": extra_pension_employer,
        "rehabilitationFundAmount": rehab_fund,
        "pensionContributionEmployerTotalAmount": employer_pension_total,
        "insuranceFeeAmount": insurance_fee,
        "taxYear": TAX_YEAR,
    }


def gross_from_total_cost(total_cost: float, **kwargs) -> float:
    """Invert totalCost → gross. All employer costs are linear in gross:
    totalCost = g·(1 + p_er + p_extra_er + rehab) + g·(1 + p_er + p_extra_er)·fee
    """
    p_er = kwargs.get("pension_employer_pct", PENSION_EMPLOYER_PCT) / 100
    p_x = kwargs.get("extra_pension_employer_pct", 0.0) / 100
    rehab = kwargs.get("rehab_fund_pct", REHAB_FUND_PCT) / 100
    fee = kwargs.get("insurance_fee_pct", INSURANCE_FEE_PCT) / 100
    factor = (1 + p_er + p_x + rehab) + (1 + p_er + p_x) * fee
    return total_cost / factor


def payday_call(gross: float, *, union_pct: float, extra_pension_employee_pct: float,
                extra_pension_employer_pct: float, allowance_pct: float) -> dict:
    payload = {
        "PensionContributionEmployeePercentage": f"{PENSION_EMPLOYEE_PCT:.2f}",
        "PensionContributionEmployerPercentage": f"{PENSION_EMPLOYER_PCT:.2f}",
        "RehabilitationFundPercentage": f"{REHAB_FUND_PCT:.2f}",
        "AdditionalPensionContributionEmployeePercentage": f"{extra_pension_employee_pct:.2f}",
        "AdditionalPensionContributionEmployerPercentage": f"{extra_pension_employer_pct:.2f}",
        "IncomeTaxStep1Percentage": f"{BRACKETS[0][1] * 100:.2f}",
        "IncomeTaxStep2Percentage": f"{BRACKETS[1][1] * 100:.2f}",
        "IncomeTaxStep3Percentage": f"{BRACKETS[2][1] * 100:.2f}",
        "InsuranceFeePercentage": f"{INSURANCE_FEE_PCT:.2f}",
        "PersonalTaxAllowancePercentage": f"{allowance_pct:.0f}",
        "SpouseTaxAllowancePercentage": "0",
        "UnionFeePercentage": f"{union_pct:.2f}",
        "PrivateSectorReliefFundPercentage": "0.00",
        "VacationFundPercentage": "0.00",
        "EducationFundPercentage": "0.00",
        "Salary": str(int(gross)),
        "TotalCost": None,
    }
    req = urllib.request.Request(
        PAYDAY_API,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            # payday.is 403s the default Python-urllib UA
            "User-Agent": "fjarmalalaesi-skill/1.0 (payslip verification)",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    if not result.get("success"):
        raise RuntimeError(f"payday.is error: {result}")
    return result["data"]


def _fmt(n: float) -> str:
    return f"{int(n):,} kr.".replace(",", ".")


def _print_summary(d: dict) -> None:
    print(f"Gross salary:          {_fmt(d['salary'])}")
    print()
    print("Employee deductions:")
    print(f"  Lífeyrir (4%):       {_fmt(d['pensionContributionEmployeeAmount'])}")
    if d["additionalPensionContributionEmployeeAmount"]:
        print(f"  Séreign:             {_fmt(d['additionalPensionContributionEmployeeAmount'])}")
    print(f"  Staðgreiðsla:        {_fmt(d['incomeTaxEmployeeTotalAmount'])}  (after {_fmt(d['personalTaxAllowanceAmount'])} persónuafsláttur)")
    if d["unionFeeAmount"]:
        print(f"  Stéttarfélag:        {_fmt(d['unionFeeAmount'])}")
    print()
    print(f"TAKE-HOME:             {_fmt(d['payoutAmountSalary'])}  ({d['payoutAmountSalary'] / d['salary'] * 100:.1f}% of gross)")
    print()
    print("Employer side (your full cost/worth):")
    print(f"  Mótframlag (11.5%):  {_fmt(d['pensionContributionEmployerAmount'])}")
    if d["additionalPensionContributionEmployerAmount"]:
        print(f"  Séreign match:       {_fmt(d['additionalPensionContributionEmployerAmount'])}")
    print(f"  VIRK (0.1%):         {_fmt(d['rehabilitationFundAmount'])}")
    print(f"  Tryggingagjald:      {_fmt(d['insuranceFeeAmount'])}")
    print(f"TOTAL EMPLOYER COST:   {_fmt(d['totalCost'])}  ({d['totalCost'] / d['salary'] * 100:.1f}% of gross)")


def cmd_gross(args: argparse.Namespace) -> None:
    d = compute(args.amount, union_pct=args.union,
                extra_pension_employee_pct=args.extra_pension,
                extra_pension_employer_pct=args.extra_pension_employer,
                allowance_pct=args.allowance)
    if args.json:
        print(json.dumps(d, indent=2))
    else:
        _print_summary(d)


def cmd_total_cost(args: argparse.Namespace) -> None:
    gross = gross_from_total_cost(args.amount, extra_pension_employer_pct=args.extra_pension_employer)
    d = compute(round(gross), union_pct=args.union,
                extra_pension_employee_pct=args.extra_pension,
                extra_pension_employer_pct=args.extra_pension_employer,
                allowance_pct=args.allowance)
    if args.json:
        print(json.dumps(d, indent=2))
    else:
        print(f"Employer total cost {_fmt(args.amount)} → gross ≈ {_fmt(round(gross))}\n")
        _print_summary(d)


def cmd_verify(args: argparse.Namespace) -> None:
    salaries = [int(s) for s in args.salaries.split(",")]
    fields = [
        "salary", "totalCost", "payoutAmountSalary",
        "pensionContributionEmployeeAmount", "additionalPensionContributionEmployeeAmount",
        "incomeTaxStep1Amount", "incomeTaxStep2Amount", "incomeTaxStep3Amount",
        "personalTaxAllowanceAmount", "incomeTaxEmployeeTotalAmount", "unionFeeAmount",
        "pensionContributionEmployerAmount", "additionalPensionContributionEmployerAmount",
        "rehabilitationFundAmount", "insuranceFeeAmount",
    ]
    failed = False
    for gross in salaries:
        local = compute(gross, union_pct=args.union,
                        extra_pension_employee_pct=args.extra_pension,
                        extra_pension_employer_pct=args.extra_pension_employer,
                        allowance_pct=args.allowance)
        try:
            remote = payday_call(gross, union_pct=args.union,
                                 extra_pension_employee_pct=args.extra_pension,
                                 extra_pension_employer_pct=args.extra_pension_employer,
                                 allowance_pct=args.allowance)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise SystemExit(f"payday.is unreachable or changed ({e}) — verify manually at payday.is")
        # remote.get(f) is None when payday.is renames a field — that IS a finding
        diffs = {f: (local[f], remote.get(f)) for f in fields if local[f] != remote.get(f)}
        status = "OK — all fields match" if not diffs else f"MISMATCH: {diffs}"
        failed = failed or bool(diffs)
        print(f"gross {gross:>12,}: take-home local {local['payoutAmountSalary']:,} "
              f"vs payday {remote.get('payoutAmountSalary', 0):,} → {status}")
    if failed:
        raise SystemExit("Verification FAILED — update the constants (or investigate a payday.is schema change).")
    print("\nAll salaries verified against payday.is ✓")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--union", type=float, default=0.0,
                        help="stéttarfélagsgjald %% of gross (VR 0.7, Efling 0.7 — most unions 0.7–1.0; "
                             "the '1%% Efling' figure is the employer's sjúkrasjóður premium, not dues)")
        sp.add_argument("--extra-pension", type=float, default=0.0, help="séreign employee %% (0, 2 or 4)")
        sp.add_argument("--extra-pension-employer", type=float, default=0.0, help="séreign employer match %% (usually 2 when employee ≥2)")
        sp.add_argument("--allowance", type=float, default=100.0, help="persónuafsláttur utilization %% (0–200 with spouse transfer)")
        sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("gross", help="gross salary → full payslip + employer cost")
    sp.add_argument("amount", type=float, help="gross monthly salary ISK")
    common(sp)
    sp.set_defaults(func=cmd_gross)

    sp = sub.add_parser("total-cost", help="employer total cost → gross → payslip")
    sp.add_argument("amount", type=float, help="employer total monthly cost ISK")
    common(sp)
    sp.set_defaults(func=cmd_total_cost)

    sp = sub.add_parser("verify", help="diff local math against the live payday.is calculator")
    sp.add_argument("--salaries", default="400000,700000,1000000,1600000,2500000",
                    help="comma-separated gross salaries to test")
    common(sp)
    sp.set_defaults(func=cmd_verify)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
