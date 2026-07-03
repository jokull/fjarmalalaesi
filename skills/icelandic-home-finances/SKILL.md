---
name: icelandic-home-finances
description: Model Icelandic household finance decisions — verðtryggð (CPI-indexed) mortgages, prepayment strategies, séreignarsparnaður (third-pillar pension) trade-offs, and staðgreiðsla tax stacking. Use when analyzing Icelandic mortgages, comparing verðtryggt vs óverðtryggt loans, valuing lump-sum paydowns or snowball strategies, modeling séreign-to-mortgage redirects, or any "fjármálalæsi" question about Icelandic housing finance (húsnæðislán, verðtrygging, höfuðstóll, uppgreiðsla, aukaafborganir).
license: MIT
compatibility: Requires Python 3.10+ (stdlib only, no packages to install)
metadata:
  author: jokull
allowed-tools: Bash(python3 *)
---

# Icelandic Home Finances (fjármálalæsi)

Iceland's housing-finance system is unusual: most mortgages are **verðtryggð** —
the principal itself is indexed to CPI monthly, so the balance *grows* in nominal
terms even while you pay. Standard mortgage intuition (and generic amortization
calculators) produce wrong answers here. This skill provides correct mechanics,
validated modeling scripts, and the decision frameworks that actually matter.

## Core mental models (read before modeling anything)

1. **Verðtryggð loans fight you with indexation.** Each month:
   `indexed_balance = balance × (1 + monthly_inflation)`, then the annuity
   payment is recalculated on the indexed balance over the remaining term.
   Early in a long loan, indexation typically exceeds scheduled principal
   repayment → the nominal balance rises for years ("höfuðstóllinn hækkar").
   At ~4% inflation a fresh 40-year verðtryggt loan grows nominally for over
   a decade. This is not a bug in your model; it is the product.

2. **Never compare undiscounted nominal sums across decades.** A "you save
   47M over the loan's life!" figure mixes kronur from 2026 and 2049.
   Discount avoided-payment streams at the inflation assumption to get real,
   today's-money value. Rule of thumb from validated modeling: the *passive*
   value of a prepayment is nearly inflation-insensitive (higher inflation →
   more indexation avoided but a higher discount rate; they roughly cancel).

3. **Tax on extra income is a stacking question, never a flat rate.**
   Staðgreiðsla is progressive per month. A séreignarsparnaður lump drawn on
   top of a top-bracket salary is taxed ~46%; the same pot spread over 15–25
   retirement years stacks on pension income instead — anywhere from <20%
   (no other income, long drawdown) to ~38% (full career pension underneath).
   Always compute the stacked marginal rate with `scripts/tax.py stacked`.

4. **Passive vs snowball paydown is usually the deciding assumption.**
   A lump-sum prepayment where the freed monthly payment is spent (passive)
   is worth far less than one where freed payments are recycled into extra
   principal every month (snowball) — in a validated real-household case,
   28M vs 42M in today's kronur for the same 16M lump. The difference is
   behavioral discipline over ~16 years, not finance. Model both; present
   both; say which assumption the verdict rests on.

5. **Prioritize the highest-APR loan.** Icelandic households often carry two
   mortgages (base loan + viðbótarlán at a higher rate). Lump sums and
   snowball extra go to the highest APR first. The scripts do this
   automatically.

## Scripts

All scripts are Python 3 stdlib-only, in `scripts/`. Each has `--help` and
`--json` for machine-readable output. Run them; don't re-derive the math by
hand — the formulas here are validated against real Arion Banki loan data and
a byte-identical dual-language (Python/TypeScript) implementation check.

| Script | Purpose |
|---|---|
| `verdtrygging.py schedule` | Full amortization of one verðtryggt loan (annuity/jafngreiðslur or equal-principal/jafnar afborganir), with optional lump sum or fixed extra monthly principal |
| `verdtrygging.py lumpsum` | Real (PV) value of a one-time prepayment, passive assumption |
| `verdtrygging.py snowball` | Multi-loan: lump applied by APR priority + freed payments recycled into principal; PV and payoff acceleration |
| `tax.py monthly` | Staðgreiðsla on a month's income (2026 brackets, persónuafsláttur) |
| `tax.py stacked` | Effective marginal rate of extra income stacked on existing income — **the** tool for séreign withdrawal modeling |
| `paydown_vs_invest.py` | Full comparison: draw down a pot now (taxed, stacked) and pay down mortgages (passive AND snowball) vs leaving it invested until retirement (growth, stacked drawdown tax, discounted to today) |
| `cpi.py` | Live CPI from Hagstofa's PX-Web API — `latest` gives the current VNV til verðtryggingar value and YoY inflation; use the *indexation* series (M+2 lag already applied) for loan models |

Typical session for "should I use savings/pension to pay down my mortgage?":

```bash
# 1. What's the tax hit if drawn now? (stacks on current salary!)
python3 scripts/tax.py stacked --withdrawal <pot> --other-income <monthly_salary>

# 2. Full comparison across both paydown styles and the invest alternative
python3 scripts/paydown_vs_invest.py \
    --loans <bal:apr:months>,<bal:apr:months> \
    --pot <gross_pot> --tax-rate-now <from step 1> \
    --inflation 4.3 --fund-return 7.0 --horizon-years <years_to_retirement> \
    --retirement-other-income <expected_pension_per_month> --drawdown-years 15

# 3. Sensitivity: rerun step 2 varying horizon (5/10/15/20), fund return
#    (4.5–8.5%), and retirement income (0/300k/600k). Present as a table.
```

Interview the user for: loan balances/APRs/remaining months (from their bank's
netbanki), gross monthly salary, years to retirement, expected pension income
(TR + lífeyrissjóður — island.is or the fund's estimator), and current
inflation forecast (see below).

## Inflation assumptions

For *current* inflation and the live indexation series, run
`python3 scripts/cpi.py latest`. For *forward* assumptions use Seðlabanki's
**Peningamál** forecast (published Feb/May/Aug/Nov), Tafla 4 (annual
averages) — not stale third-party numbers. The Hagstofa þjóðhagsspá API can
lag the latest Peningamál by weeks or months; cross-check against the PM PDF
at sedlabanki.is. For long horizons beyond the forecast window, 2.5% (the
inflation target) is the standard terminal assumption; run sensitivity at
±1.5pp regardless.

## Reference documents

Load these only when the question requires depth in that area:

- `references/verdtrygging.md` — legal basis (lög 38/2001), index mechanics,
  vísitala publication schedule, verðtryggt vs óverðtryggt trade-offs,
  40-year-loan restrictions, current rate environment, Hagstofa CPI API
- `references/sereignarsparnadur.md` — third-pillar pension rules, the
  séreign-to-mortgage tax-free redirect program (reinstated June 2026;
  applications from Oct 1 2026, retroactive to Jan 1 2026; 120-month
  cumulative cap), fyrsta íbúð program, withdrawal taxation, TR interactions
- `references/mortgage-market.md` — lender landscape (banks, lífeyrissjóðir,
  HMS hlutdeildarlán), current rates, Seðlabanki LTV/DSTI rules, refinancing
  costs and mechanics, fasteignamat, prepayment mechanics
- `references/tax-and-benefits.md` — staðgreiðsla brackets, álagning cycle,
  vaxtabætur status, rental income (incl. Airbnb/heimagisting), capital gains
  on housing, fasteignagjöld, gifts/arv toward down payments, TR skerðingar
- `references/icelandic-data.md` — **where to get reliable numbers**: APIs
  and official sources for CPI, forecasts, policy rates, lender rates,
  fasteignamat, tax figures, and legislation, with each source's lag traps.
  Load this before fetching any external data or citing current values

## Guardrails

- **Always run sensitivity** on inflation, fund return, and horizon before
  giving a verdict. Single-scenario answers on 20-year questions mislead.
- **State the behavioral assumption** (passive vs snowball) any paydown
  verdict rests on.
- **Bracket table staleness**: `tax.py` embeds 2026 values; verify against
  skatturinn.is each January (the script's `--year` flag fails loudly).
- **Legal availability ≠ modeling**: séreignarsparnaður cannot normally be
  drawn before retirement age outside the housing-redirect programs. Flag
  hypotheticals as hypothetical.
- This is decision-support modeling, not financial advice; recommend users
  verify big moves with their bank or a licensed advisor.
