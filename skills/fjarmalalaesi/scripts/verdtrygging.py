#!/usr/bin/env python3
"""Verðtryggð (CPI-indexed) Icelandic mortgage engine.

Models the mechanics Icelandic banks actually use for verðtryggð húsnæðislán:

  1. Each month the remaining principal is indexed:
         indexed = balance × (1 + monthly_inflation)
     where monthly_inflation = (1 + annual_inflation)^(1/12) − 1
     (in reality the ratio of vísitala neysluverðs between months; a constant
     annual assumption is the standard modeling simplification).
  2. For jafngreiðslur (annuity) loans the payment is recalculated every month
     on the indexed balance over the remaining term:
         payment = PMT(indexed, APR/12, months_left) + fee
  3. interest = indexed × APR/12
     principal_repaid = payment − fee − interest
     new_balance = indexed − principal_repaid − extra_principal

This is why verðtryggð loans exhibit negative real amortization in early
years: indexation adds more to the balance than the scheduled principal
repayment removes whenever inflation is high relative to progress through
the term ("höfuðstóllinn hækkar").

Also supports jafnar afborganir (equal-principal) loans, one-time lump-sum
prepayments (innborgun á höfuðstól), fixed extra monthly principal, and
snowball strategies across multiple loans.

Stdlib only. Amounts in ISK.

CLI examples:
    # Full schedule for one loan
    python3 verdtrygging.py schedule --balance 76000000 --apr 4.49 \
        --months 276 --inflation 4.3

    # Effect of a one-time 5M prepayment
    python3 verdtrygging.py lumpsum --balance 76000000 --apr 4.49 \
        --months 276 --inflation 4.3 --amount 5000000

    # Two loans, 16.1M lump, freed payments snowballed into principal
    python3 verdtrygging.py snowball --loans 76000000:4.49:276,8800000:5.99:276 \
        --inflation 4.3 --lump 16100000

Every subcommand accepts --json for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict

DEFAULT_MONTHLY_FEE = 130  # typical greiðslugjald/tilkynningargjald per payment


# ── Core math ────────────────────────────────────────────────────────────


def monthly_inflation_rate(annual_pct: float) -> float:
    """Compound-equivalent monthly rate for an annual inflation percentage."""
    return (1.0 + annual_pct / 100.0) ** (1.0 / 12.0) - 1.0


def annuity_payment(balance: float, monthly_rate: float, months_left: int) -> float:
    """Jafngreiðslur payment (excluding fees) on `balance` over `months_left`."""
    if months_left <= 0:
        return balance
    if monthly_rate == 0:
        return balance / months_left
    pow_ = (1.0 + monthly_rate) ** months_left
    return balance * (monthly_rate * pow_) / (pow_ - 1.0)


@dataclass
class MonthRow:
    month: int  # 1-based month number from simulation start
    payment: float  # total cash out this month (incl. fee and any extra principal)
    interest: float
    indexation: float
    principal_repaid: float  # scheduled principal component (excl. extra)
    extra_principal: float
    balance: float  # remaining indexed principal after this month


@dataclass
class LoanResult:
    months: int
    total_paid: float
    total_interest: float
    total_indexation: float
    final_balance: float
    rows: list[MonthRow]

    def summary(self) -> dict:
        d = asdict(self)
        d.pop("rows")
        return d


def simulate_loan(
    balance: float,
    apr_pct: float,
    months_remaining: int,
    inflation_pct: float,
    *,
    method: str = "annuity",  # "annuity" (jafngreiðslur) | "equal_principal" (jafnar afborganir)
    fee: float = DEFAULT_MONTHLY_FEE,
    lump_sum: float = 0.0,
    extra_monthly: float = 0.0,
    max_months: int | None = None,
) -> LoanResult:
    """Simulate a verðtryggt loan to payoff (or `max_months`).

    `lump_sum` is applied against the balance before month 1.
    `extra_monthly` is additional principal paid every month on top of the
    scheduled payment (banks apply it directly to höfuðstóll).
    """
    r = apr_pct / 100.0 / 12.0
    mi = monthly_inflation_rate(inflation_pct)
    bal = max(0.0, balance - lump_sum)
    months_left = months_remaining
    rows: list[MonthRow] = []
    total_paid = total_interest = total_indexation = 0.0
    m = 0

    while bal > 1000 and months_left > 0 and (max_months is None or m < max_months):
        indexation = bal * mi
        indexed = bal + indexation
        interest = indexed * r

        if method == "annuity":
            gross = annuity_payment(indexed, r, months_left)
            principal_repaid = gross - interest
        elif method == "equal_principal":
            principal_repaid = indexed / months_left
            gross = principal_repaid + interest
        else:
            raise ValueError(f"unknown method: {method}")

        extra = min(extra_monthly, max(0.0, indexed - principal_repaid))
        bal = max(0.0, indexed - principal_repaid - extra)
        payment = gross + fee + extra

        months_left -= 1
        m += 1
        total_paid += payment
        total_interest += interest
        total_indexation += indexation
        rows.append(
            MonthRow(m, payment, interest, indexation, principal_repaid, extra, bal)
        )

    return LoanResult(m, total_paid, total_interest, total_indexation, bal, rows)


# ── Multi-loan snowball ──────────────────────────────────────────────────


@dataclass
class LoanSpec:
    balance: float
    apr_pct: float
    months_remaining: int
    fee: float = DEFAULT_MONTHLY_FEE

    @classmethod
    def parse(cls, text: str) -> "LoanSpec":
        """Parse 'balance:apr:months' e.g. '76000000:4.49:276'."""
        parts = text.split(":")
        if len(parts) != 3:
            raise ValueError(f"loan spec must be balance:apr:months, got {text!r}")
        return cls(float(parts[0]), float(parts[1]), int(parts[2]))


def combined_baseline(loans: list[LoanSpec], inflation_pct: float, method: str = "annuity") -> list[float]:
    """Per-month combined required payment if nothing extra is ever paid."""
    streams = [
        [row.payment for row in simulate_loan(
            l.balance, l.apr_pct, l.months_remaining, inflation_pct, fee=l.fee, method=method
        ).rows]
        for l in loans
    ]
    n = max(len(s) for s in streams)
    return [sum(s[t] if t < len(s) else 0.0 for s in streams) for t in range(n)]


def simulate_snowball(
    loans: list[LoanSpec],
    inflation_pct: float,
    *,
    lump_sum: float = 0.0,
    method: str = "annuity",
) -> dict:
    """Apply `lump_sum` to loans greedily by APR (highest first), then keep
    total household outflow pinned to the original combined baseline: every
    krona freed (a loan disappearing, or lower required payments) becomes
    extra principal on the highest-APR surviving loan, every month.

    Returns combined payment streams for baseline and snowball scenarios,
    plus totals. This is the disciplined-paydown model — the realistic upper
    bound on what a prepayment can achieve.
    """
    baseline = combined_baseline(loans, inflation_pct, method)

    # Apply lump greedily by APR descending
    remaining_lump = lump_sum
    states = []
    for l in sorted(loans, key=lambda l: -l.apr_pct):
        applied = min(remaining_lump, l.balance)
        remaining_lump -= applied
        states.append({
            "spec": l,
            "balance": l.balance - applied,
            "months_left": l.months_remaining,
            "lump_applied": applied,
        })

    mi = monthly_inflation_rate(inflation_pct)
    stream: list[float] = []
    totals = {"interest": 0.0, "indexation": 0.0, "paid": 0.0}
    t = 0

    while any(s["balance"] > 1000 and s["months_left"] > 0 for s in states):
        # Required payments first
        month_required = 0.0
        for s in states:
            if s["balance"] <= 1000 or s["months_left"] <= 0:
                s["months_left"] = max(0, s["months_left"] - 1)
                continue
            r = s["spec"].apr_pct / 100.0 / 12.0
            indexation = s["balance"] * mi
            indexed = s["balance"] + indexation
            interest = indexed * r
            if method == "annuity":
                gross = annuity_payment(indexed, r, s["months_left"])
                principal_repaid = gross - interest
            else:
                principal_repaid = indexed / s["months_left"]
                gross = principal_repaid + interest
            s["balance"] = max(0.0, indexed - principal_repaid)
            s["months_left"] -= 1
            month_required += gross + s["spec"].fee
            totals["interest"] += interest
            totals["indexation"] += indexation

        # Freed cash → extra principal on highest-APR surviving loan
        target = baseline[t] if t < len(baseline) else month_required
        extra_budget = max(0.0, target - month_required)
        for s in states:  # states already sorted by APR desc
            if extra_budget <= 0:
                break
            if s["balance"] > 1000:
                extra = min(extra_budget, s["balance"])
                s["balance"] -= extra
                extra_budget -= extra

        month_total = month_required + (max(0.0, target - month_required) - extra_budget)
        stream.append(month_total)
        totals["paid"] += month_total
        t += 1

    return {
        "baseline_stream": baseline,
        "snowball_stream": stream,
        "payoff_months": len(stream),
        "baseline_months": len(baseline),
        "lump_allocation": [
            {"apr": s["spec"].apr_pct, "lump_applied": s["lump_applied"]} for s in states
        ],
        "totals": totals,
    }


# ── Present value ────────────────────────────────────────────────────────


def pv_of_stream_difference(
    baseline: list[float], scenario: list[float], discount_annual_pct: float
) -> float:
    """PV of (baseline − scenario) payments, discounted monthly.

    Discounting at the inflation rate strips out pure currency debasement and
    yields the real, today's-money value of a prepayment strategy — the
    apples-to-apples number to compare against the cash deployed today.
    """
    mi = monthly_inflation_rate(discount_annual_pct)
    n = max(len(baseline), len(scenario))
    pv = 0.0
    for t in range(n):
        b = baseline[t] if t < len(baseline) else 0.0
        s = scenario[t] if t < len(scenario) else 0.0
        pv += (b - s) / (1.0 + mi) ** (t + 1)
    return pv


# ── CLI ──────────────────────────────────────────────────────────────────


def _fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def cmd_schedule(args: argparse.Namespace) -> None:
    res = simulate_loan(
        args.balance, args.apr, args.months, args.inflation,
        method=args.method, extra_monthly=args.extra_monthly, lump_sum=args.lump,
    )
    if args.json:
        out = res.summary()
        if args.rows:
            out["rows"] = [asdict(r) for r in res.rows]
        print(json.dumps(out, indent=2))
        return
    print(f"Payoff: {res.months} months ({res.months / 12:.1f} years)")
    print(f"Total paid:       {_fmt(res.total_paid)}")
    print(f"Total interest:   {_fmt(res.total_interest)}")
    print(f"Total indexation: {_fmt(res.total_indexation)}")
    if args.rows:
        print(f"\n{'mo':>4} {'payment':>12} {'interest':>12} {'indexation':>12} {'balance':>15}")
        for r in res.rows[: args.rows if args.rows > 0 else None]:
            print(f"{r.month:>4} {_fmt(r.payment):>12} {_fmt(r.interest):>12} {_fmt(r.indexation):>12} {_fmt(r.balance):>15}")


def cmd_lumpsum(args: argparse.Namespace) -> None:
    base = simulate_loan(args.balance, args.apr, args.months, args.inflation, method=args.method)
    scen = simulate_loan(args.balance, args.apr, args.months, args.inflation, method=args.method, lump_sum=args.amount)
    pv = pv_of_stream_difference(
        [r.payment for r in base.rows], [r.payment for r in scen.rows], args.inflation
    )
    out = {
        "lump_sum": args.amount,
        "baseline": base.summary(),
        "scenario": scen.summary(),
        "nominal_payments_avoided": base.total_paid - scen.total_paid,
        "pv_of_avoided_payments_today": pv,
        "pv_per_krona_deployed": pv / args.amount if args.amount else None,
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return
    print(f"Lump sum:                      {_fmt(args.amount)}")
    print(f"Nominal payments avoided:      {_fmt(out['nominal_payments_avoided'])}  (future kronur — misleading alone)")
    print(f"PV of avoided payments today:  {_fmt(pv)}  (discounted at inflation {args.inflation}%)")
    print(f"Real value per krona deployed: {out['pv_per_krona_deployed']:.2f}")


def cmd_snowball(args: argparse.Namespace) -> None:
    loans = [LoanSpec.parse(s) for s in args.loans.split(",")]
    res = simulate_snowball(loans, args.inflation, lump_sum=args.lump, method=args.method)
    pv = pv_of_stream_difference(res["baseline_stream"], res["snowball_stream"], args.inflation)
    out = {
        "lump_sum": args.lump,
        "lump_allocation": res["lump_allocation"],
        "payoff_months": res["payoff_months"],
        "baseline_months": res["baseline_months"],
        "pv_of_avoided_payments_today": pv,
        "pv_per_krona_deployed": pv / args.lump if args.lump else None,
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return
    print(f"Lump sum: {_fmt(args.lump)}, allocated by APR (highest first):")
    for a in res["lump_allocation"]:
        print(f"  {a['apr']}% loan ← {_fmt(a['lump_applied'])}")
    print(f"Payoff: {out['payoff_months']} months vs {out['baseline_months']} baseline "
          f"({(out['baseline_months'] - out['payoff_months']) / 12:.1f} years earlier)")
    print(f"PV of avoided payments today: {_fmt(pv)} (discounted at inflation {args.inflation}%)")
    if args.lump:
        print(f"Real value per krona deployed: {out['pv_per_krona_deployed']:.2f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp: argparse.ArgumentParser, single_loan: bool = True) -> None:
        if single_loan:
            sp.add_argument("--balance", type=float, required=True, help="remaining principal (ISK)")
            sp.add_argument("--apr", type=float, required=True, help="annual interest rate %% (e.g. 4.49)")
            sp.add_argument("--months", type=int, required=True, help="months remaining on term")
            sp.add_argument("--method", choices=["annuity", "equal_principal"], default="annuity",
                            help="jafngreiðslur (default) or jafnar afborganir")
        sp.add_argument("--inflation", type=float, required=True, help="assumed annual inflation %% (e.g. 4.3)")
        sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("schedule", help="full amortization schedule for one loan")
    common(sp)
    sp.add_argument("--extra-monthly", type=float, default=0.0, help="extra principal every month")
    sp.add_argument("--lump", type=float, default=0.0, help="one-time prepayment before month 1")
    sp.add_argument("--rows", type=int, default=0, help="print first N schedule rows (0 = summary only)")
    sp.set_defaults(func=cmd_schedule)

    sp = sub.add_parser("lumpsum", help="value of a one-time prepayment (passive: payment just drops)")
    common(sp)
    sp.add_argument("--amount", type=float, required=True, help="lump sum ISK")
    sp.set_defaults(func=cmd_lumpsum)

    sp = sub.add_parser("snowball", help="lump sum + freed payments recycled into principal, multi-loan")
    common(sp, single_loan=False)
    sp.add_argument("--loans", required=True, help="comma-separated balance:apr:months, e.g. 76000000:4.49:276,8800000:5.99:276")
    sp.add_argument("--lump", type=float, default=0.0, help="one-time prepayment before month 1")
    sp.add_argument("--method", choices=["annuity", "equal_principal"], default="annuity",
                    help="applies to ALL loans: jafngreiðslur (default) or jafnar afborganir")
    sp.set_defaults(func=cmd_snowball)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
