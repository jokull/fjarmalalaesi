#!/usr/bin/env python3
"""Icelandic staðgreiðsla (withholding tax) math for financial modeling.

Implements the progressive monthly bracket calculation with persónuafsláttur,
and — critically for pension/séreignarsparnaður modeling — the *stacked
marginal rate* of an extra income stream on top of existing income. A lump
séreign withdrawal on top of a salary is taxed at the brackets the combined
income reaches, not at some average rate; the same withdrawal spread over
retirement years stacks on (usually much lower) pension income instead.

Bracket values are for 2026 and must be updated annually from
https://www.skatturinn.is/einstaklingar/stadgreidsla/skattthrep/
(pass --year to fail loudly if the table here is stale).

Stdlib only. Amounts in ISK.

CLI examples:
    # Tax on a monthly salary
    python3 tax.py monthly --income 1606000

    # Effective rate on a séreign withdrawal stacked on other income
    python3 tax.py stacked --withdrawal 480000 --other-income 600000

    # Effective rate on a huge single-month lump on top of salary
    python3 tax.py stacked --withdrawal 30000000 --other-income 1606000
"""

from __future__ import annotations

import argparse
import json

# 2026 staðgreiðsla — update annually from skatturinn.is
TAX_YEAR = 2026
BRACKETS: list[tuple[float, float]] = [
    # (upper bound of band, rate) — monthly gross ISK
    (498_122, 0.3149),
    (1_398_450, 0.3799),
    (float("inf"), 0.4629),
]
PERSONAL_CREDIT_MONTHLY = 72_492  # persónuafsláttur per month (869,898/yr)


def monthly_tax(gross_monthly: float, *, credit: float = PERSONAL_CREDIT_MONTHLY) -> float:
    """Withholding tax for one month's gross income, after persónuafsláttur."""
    tax = 0.0
    prev_cap = 0.0
    for cap, rate in BRACKETS:
        if gross_monthly <= prev_cap:
            break
        tax += (min(gross_monthly, cap) - prev_cap) * rate
        prev_cap = cap
    return max(0.0, tax - credit)


def stacked_effective_rate(extra_monthly: float, other_monthly_income: float) -> float:
    """Effective tax rate on `extra_monthly` when stacked on top of
    `other_monthly_income` — the marginal tax the extra income actually causes.

    This is THE number for séreign drawdown modeling: with no other income,
    persónuafsláttur and the low bracket absorb much of a modest withdrawal;
    with a full salary or career pension underneath, the withdrawal lands in
    the upper brackets.
    """
    if extra_monthly <= 0:
        return 0.0
    return (
        monthly_tax(other_monthly_income + extra_monthly)
        - monthly_tax(other_monthly_income)
    ) / extra_monthly


def net_of_stacked_tax(extra_monthly: float, other_monthly_income: float) -> float:
    """Post-tax value of `extra_monthly` stacked on `other_monthly_income`."""
    return extra_monthly * (1.0 - stacked_effective_rate(extra_monthly, other_monthly_income))


# ── CLI ──────────────────────────────────────────────────────────────────


def _check_year(args: argparse.Namespace) -> None:
    if args.year and args.year != TAX_YEAR:
        raise SystemExit(
            f"Bracket table in this script is for {TAX_YEAR}, you asked for {args.year}. "
            f"Update BRACKETS/PERSONAL_CREDIT_MONTHLY from skatturinn.is first."
        )


def cmd_monthly(args: argparse.Namespace) -> None:
    _check_year(args)
    tax = monthly_tax(args.income)
    out = {
        "gross_monthly": args.income,
        "tax": round(tax),
        "net_monthly": round(args.income - tax),
        "average_rate": round(tax / args.income, 4) if args.income else 0,
        "tax_year": TAX_YEAR,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Gross {args.income:,.0f} → tax {tax:,.0f} → net {out['net_monthly']:,} "
              f"(avg rate {out['average_rate']:.1%}) [{TAX_YEAR}]")


def cmd_stacked(args: argparse.Namespace) -> None:
    _check_year(args)
    rate = stacked_effective_rate(args.withdrawal, args.other_income)
    out = {
        "withdrawal_monthly": args.withdrawal,
        "other_income_monthly": args.other_income,
        "effective_rate_on_withdrawal": round(rate, 4),
        "net_withdrawal": round(args.withdrawal * (1 - rate)),
        "tax_year": TAX_YEAR,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Withdrawal {args.withdrawal:,.0f}/mo on top of {args.other_income:,.0f}/mo other income:")
        print(f"  effective rate {rate:.1%} → net {out['net_withdrawal']:,}/mo [{TAX_YEAR}]")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("monthly", help="tax on one month's gross income")
    sp.add_argument("--income", type=float, required=True, help="gross monthly income ISK")
    sp.add_argument("--year", type=int, help="assert bracket table year matches")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_monthly)

    sp = sub.add_parser("stacked", help="effective marginal rate of extra income stacked on existing income")
    sp.add_argument("--withdrawal", type=float, required=True, help="extra monthly income ISK (e.g. séreign drawdown)")
    sp.add_argument("--other-income", type=float, default=0.0, help="existing monthly income it stacks on")
    sp.add_argument("--year", type=int, help="assert bracket table year matches")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_stacked)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
