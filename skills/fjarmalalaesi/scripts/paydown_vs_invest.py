#!/usr/bin/env python3
"""Compare paying down verðtryggð mortgages against keeping money invested
(e.g. in séreignarsparnaður), in real today's-money terms.

The comparison this implements, validated against a real Icelandic household's
Arion Banki loan data:

  Option A — deploy cash against the mortgage(s):
    A1 "passive":  lump sum lowers the balance; the required payment drops
                   and the freed cash is NOT reinvested.
    A2 "snowball": lump sum lowers the balance AND the household keeps paying
                   the original combined amount — every freed krona becomes
                   extra principal. Collapses the term dramatically.
    Value = PV of avoided future payments, discounted at inflation
    (strips currency debasement; result is in today's kronur).

  Option B — leave the money invested until retirement:
    pot grows at a nominal fund return; withdrawals stack on other retirement
    income and are taxed at the brackets they actually reach (see tax.py);
    net proceeds discounted at inflation back to today.

Key insights this encodes (learned the hard way):
  * Never compare undiscounted nominal sums across decades of inflation.
  * A withdrawal's tax rate is a STACKING question, not a flat rate — on top
    of a salary it's the top bracket; spread thin in retirement with no other
    income it can be under 20%; on top of a full career pension ~38%.
  * The passive paydown PV is nearly inflation-insensitive (higher inflation
    → more indexation avoided but a higher discount rate; they roughly cancel).
  * The snowball vs passive distinction usually decides the verdict, and it
    is a behavioral assumption, not a financial one.

Stdlib only. Requires verdtrygging.py and tax.py in the same directory.

CLI example (30M séreign, two loans, 20y to retirement):
    python3 paydown_vs_invest.py \
        --loans 76000000:4.49:276,8800000:5.99:276 \
        --pot 30000000 --tax-rate-now 0.4629 \
        --inflation 4.3 --fund-return 7.0 --horizon-years 20 \
        --retirement-other-income 300000 --drawdown-years 15
"""

from __future__ import annotations

import argparse
import json

from tax import stacked_effective_rate
from verdtrygging import (
    LoanSpec,
    combined_baseline,
    monthly_inflation_rate,
    pv_of_stream_difference,
    simulate_loan,
    simulate_snowball,
)


def passive_paydown_pv(loans: list[LoanSpec], lump: float, inflation: float) -> float:
    """PV of a lump sum applied greedily by APR, freed payments NOT recycled."""
    remaining = lump
    pv = 0.0
    for l in sorted(loans, key=lambda l: -l.apr_pct):
        applied = min(remaining, l.balance)
        remaining -= applied
        base = simulate_loan(l.balance, l.apr_pct, l.months_remaining, inflation, fee=l.fee)
        scen = simulate_loan(l.balance, l.apr_pct, l.months_remaining, inflation, fee=l.fee, lump_sum=applied)
        pv += pv_of_stream_difference(
            [r.payment for r in base.rows], [r.payment for r in scen.rows], inflation
        )
    return pv


def snowball_paydown_pv(loans: list[LoanSpec], lump: float, inflation: float) -> tuple[float, int, int]:
    res = simulate_snowball(loans, inflation, lump_sum=lump)
    pv = pv_of_stream_difference(res["baseline_stream"], res["snowball_stream"], inflation)
    return pv, res["payoff_months"], res["baseline_months"]


def invested_pv(
    pot_gross: float,
    fund_return_pct: float,
    horizon_years: float,
    inflation: float,
    retirement_other_income: float,
    drawdown_years: float,
) -> dict:
    """Today's-money value of leaving the pot invested until retirement.

    Grows at nominal fund return, withdrawn over `drawdown_years` in equal
    monthly amounts stacked on `retirement_other_income`, taxed at the
    brackets actually reached, discounted at inflation back to today.
    (Simplification: taxes the whole pot at the effective rate of the monthly
    withdrawal at horizon; growth during drawdown is ignored — conservative.)
    """
    gross_at_horizon = pot_gross * (1.0 + fund_return_pct / 100.0) ** horizon_years
    monthly_withdrawal = gross_at_horizon / (drawdown_years * 12.0)
    eff_rate = stacked_effective_rate(monthly_withdrawal, retirement_other_income)
    net = gross_at_horizon * (1.0 - eff_rate)
    pv = net / (1.0 + inflation / 100.0) ** horizon_years
    return {
        "gross_at_horizon": gross_at_horizon,
        "monthly_withdrawal": monthly_withdrawal,
        "effective_tax_rate": eff_rate,
        "net_at_horizon": net,
        "pv_today": pv,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--loans", required=True,
                   help="comma-separated balance:apr:months, e.g. 76000000:4.49:276,8800000:5.99:276")
    p.add_argument("--pot", type=float, required=True,
                   help="gross amount available (ISK), e.g. séreignarsparnaður balance")
    p.add_argument("--tax-rate-now", type=float, required=True,
                   help="effective tax rate if drawn down today (0..1). For a lump on top of a "
                        "top-bracket salary this is 0.4629; use tax.py stacked to compute exactly")
    p.add_argument("--inflation", type=float, required=True, help="assumed annual inflation %%")
    p.add_argument("--fund-return", type=float, required=True, help="assumed nominal annual fund return %%")
    p.add_argument("--horizon-years", type=float, required=True, help="years until retirement withdrawal begins")
    p.add_argument("--retirement-other-income", type=float, default=0.0,
                   help="other monthly retirement income the drawdown stacks on (TR + lífeyrissjóður)")
    p.add_argument("--drawdown-years", type=float, default=15.0, help="years the pot is spread over in retirement")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    loans = [LoanSpec.parse(s) for s in args.loans.split(",")]
    net_lump = args.pot * (1.0 - args.tax_rate_now)

    passive_pv = passive_paydown_pv(loans, net_lump, args.inflation)
    snowball_pv, payoff_months, baseline_months = snowball_paydown_pv(loans, net_lump, args.inflation)
    invest = invested_pv(
        args.pot, args.fund_return, args.horizon_years, args.inflation,
        args.retirement_other_income, args.drawdown_years,
    )

    def verdict(paydown: float) -> str:
        return "paydown wins" if paydown > invest["pv_today"] else "invest wins"

    out = {
        "inputs": vars(args) | {"net_lump_after_tax_now": net_lump},
        "paydown_passive_pv": round(passive_pv),
        "paydown_snowball_pv": round(snowball_pv),
        "snowball_payoff_months": payoff_months,
        "baseline_payoff_months": baseline_months,
        "invest": {k: round(v, 4 if k == "effective_tax_rate" else 0) for k, v in invest.items()},
        "verdict_vs_passive": verdict(passive_pv),
        "verdict_vs_snowball": verdict(snowball_pv),
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return

    f = lambda n: f"{n:,.0f}"
    print(f"Pot: {f(args.pot)} gross → {f(net_lump)} net if drawn now ({args.tax_rate_now:.2%})")
    print()
    print(f"A1 Passive paydown PV:   {f(passive_pv)}  (today's kronur)")
    print(f"A2 Snowball paydown PV:  {f(snowball_pv)}  — payoff {payoff_months} mo vs {baseline_months} baseline")
    print(f"B  Invest until retirement:")
    print(f"     grows to {f(invest['gross_at_horizon'])} in {args.horizon_years:.0f}y at {args.fund_return}%")
    print(f"     drawn {f(invest['monthly_withdrawal'])}/mo over {args.drawdown_years:.0f}y on top of "
          f"{f(args.retirement_other_income)}/mo → eff. tax {invest['effective_tax_rate']:.1%}")
    print(f"     PV today: {f(invest['pv_today'])}")
    print()
    print(f"Verdict vs passive paydown:  {out['verdict_vs_passive']} "
          f"(margin {f(abs(passive_pv - invest['pv_today']))})")
    print(f"Verdict vs snowball paydown: {out['verdict_vs_snowball']} "
          f"(margin {f(abs(snowball_pv - invest['pv_today']))})")
    print()
    print("Remember: snowball assumes years of unwavering discipline redirecting freed")
    print("payments into principal. If that's doubtful, weight the passive verdict.")


if __name__ == "__main__":
    main()
