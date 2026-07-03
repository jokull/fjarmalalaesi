---
name: fjarmalalaesi
description: Icelandic personal-finance literacy (fjármálalæsi) — payslips and wage rights, union benefits, the three-pillar pension system, verðtryggð (CPI-indexed) mortgages and prepayment strategies, séreignarsparnaður trade-offs, savings and investment options, staðgreiðsla tax stacking, and safety nets (fæðingarorlof, atvinnuleysisbætur, námslán). Use for any Icelandic personal-finance question — reading a launaseðill, negotiating salary, choosing pension funds, analyzing húsnæðislán and verðtrygging, comparing savings accounts, or navigating benefits and life events.
license: MIT
compatibility: Requires Python 3.10+ (stdlib only, no packages to install)
metadata:
  author: jokull
allowed-tools: Bash(python3:*)
---

# Fjármálalæsi — Icelandic Personal Finance

Iceland's personal-finance system is idiosyncratic: mortgage principals grow
with CPI (verðtrygging), ~90% of workers are unionized with wage floors and
benefit funds set by kjarasamningar, pensions come in three layers with very
different tax and means-testing treatment, and tax on any extra income
depends entirely on what it stacks on. Generic financial intuition — and
generic calculators — get all of this wrong. This skill provides correct
mechanics, validated modeling scripts, and the decision frameworks that
actually matter.

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

6. **The payslip is verifiable arithmetic — verify it.** Deduction order:
   lífeyrir 4% and séreign (pre-tax) → staðgreiðsla → stéttarfélagsgjald
   (post-tax). The **2% séreign employer match is a 100% instant return**
   on the matched money — always ask whether it's being captured. The
   employer's true cost is ~120.8% of gross from `scripts/payslip.py`
   (pension + tryggingagjald + VIRK), ~122.4% including the union sjóðir
   (see `unions-and-wages.md` §2) — the "know your worth" number for
   negotiation and contractor comparisons.

7. **Kjarasamningar set floors for everyone** (lög 55/1980 — member or
   not), so wage tables are floors, never benchmarks. Benchmark against
   Hagstofa's launarannsókn medians/percentiles (`scripts/wages.py`) using
   the right wage concept: regluleg laun for a plain monthly offer,
   heildarlaun for total-comp claims.

8. **Pension pillars have wildly different treatment.** Frjáls séreign:
   TR-clawback-free, heritable, free from 60. Tilgreind séreign: counts
   against TR (since 2023), forced spread 62–67. Samtrygging: lifelong
   annuity + invisible disability insurance, but pays your estate nothing.
   Never say just "séreign" in a recommendation — qualify which.

9. **Kill expensive credit before saving.** Overdraft/credit-card
   revolving runs ~15.5%, BNPL effectively 17–40%+; savings earn ~7%
   before tax. And the 300k/yr frítekjumark shelters interest on roughly
   the first ~4M kr per person — plan account ownership around it.

## Scripts

All scripts are Python 3 stdlib-only, in `scripts/`. Each has `--help` and
`--json` for machine-readable output. Run them; don't re-derive the math by
hand — the mortgage formulas were validated against real Arion Banki loan
data during development, and the payslip math verifies live against
payday.is (`payslip.py verify`).

| Script | Purpose |
|---|---|
| `verdtrygging.py schedule` | Full amortization of one verðtryggt loan (annuity/jafngreiðslur or equal-principal/jafnar afborganir), with optional lump sum or fixed extra monthly principal |
| `verdtrygging.py lumpsum` | Real (PV) value of a one-time prepayment, passive assumption |
| `verdtrygging.py snowball` | Multi-loan: lump applied by APR priority + freed payments recycled into principal; PV and payoff acceleration |
| `tax.py monthly` | Staðgreiðsla on a month's income (2026 brackets, persónuafsláttur) |
| `tax.py stacked` | Effective marginal rate of extra income stacked on existing income — **the** tool for séreign withdrawal modeling |
| `paydown_vs_invest.py` | Full comparison: draw down a pot now (taxed, stacked) and pay down mortgages (passive AND snowball) vs leaving it invested until retirement (growth, stacked drawdown tax, discounted to today) |
| `cpi.py` | Live CPI from Hagstofa's PX-Web API — `latest` gives the current VNV til verðtryggingar value and YoY inflation; use the *indexation* series (M+2 lag already applied) for loan models |
| `payslip.py gross` | Full launaseðill from gross salary: lífeyrir, séreign, staðgreiðsla, stéttarfélagsgjald → take-home, PLUS the employer side (mótframlag, tryggingagjald → total cost, the "know your worth" number). Verified field-for-field against the payday.is calculator |
| `payslip.py total-cost` | Inverse: employer total cost → gross → payslip (for contractor-vs-employee and salary-negotiation framing) |
| `payslip.py verify` | Diff the local math against the live payday.is calculator across a salary list — run after each January bracket update |
| `wages.py groups/percentiles/occupation` | Live salary benchmarks from Hagstofa's launarannsókn (medians by occupation group, P10–P90 distributions, fine-grained ÍSTARF95 lookup). Data lags ~5 months — uprate by the Jan 1 contractual raise |

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
(TR + lífeyrissjóður — Lífeyrisgáttin or the fund's estimator), and current
inflation forecast (see below).

Two modeling notes: (1) **óverðtryggt loans** are the same engine with
`--inflation 0` and the nominal rate — use that for verðtryggt-vs-óverðtryggt
payment-path comparisons; (2) **TR skerðing is not inside
`paydown_vs_invest.py`** — frjáls séreign is exempt, but for any other
retirement income stream apply `tax.py tr-clawback` on top (45% above the
frítekjumark; see `tax-and-benefits.md` §9).

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
- `references/unions-and-wages.md` — the union system (what membership
  buys, sjúkrasjóðir, starfsmenntasjóðir), exact payslip mechanics and
  employer-side costs, employee rights (veikindaréttur, uppsagnarfrestur,
  yfirvinna, jafnaðarkaup pitfalls, gerviverktaka), salary benchmarking
  sources, negotiation practicals incl. skattmat hlunnindi values
- `references/pension-system.md` — the three pillars, age-priced accrual,
  tilgreind vs frjáls séreign (TR treatment differs!), fund/provider
  comparison incl. fees, Lífeyrisgáttin, abroad/gaps/divorce/death rules
- `references/financial-institutions.md` — banks vs indó/Auður, deposit
  insurance (TVF), savings rates and the frítekjumark real-return math,
  government bonds, funds and the cheap index options, investing abroad,
  crypto tax, expensive-credit traps and complaint routes
- `references/safety-nets-and-life-events.md` — fæðingarorlof math and
  pitfalls, atvinnuleysisbætur, the illness income ladder, Menntasjóður,
  barnabætur/meðlag/childcare costs, framfærsluviðmið (what greiðslumat
  uses), debt trouble (UMS, greiðsluaðlögun, Creditinfo), renting rights
- `references/tax-law-navigation.md` — **which statute governs what and
  how to verify any tax number**: the lög 90/2003 article map, the annual
  fjárlög/bandormur cycle, yskn.is/bindandi álit escalation, the 3-step
  verification workflow and its traps. Load when citing or verifying tax
  rules rather than just values
- `references/icelandic-data.md` — **where to get reliable numbers**: APIs
  and official sources for CPI, forecasts, policy rates, lender rates,
  fasteignamat, tax figures, and legislation, with each source's lag traps.
  Load this before fetching any external data or citing current values
- `references/practical-moves.md` — verified, quantified money moves
  (FX-cheap cards, the séreign match, unclaimed union grants, frítekjumark
  account-splitting, fee-free prepayment windows, time-sensitive
  deadlines). Comes with presentation rules: always relay the number, the
  condition, and the verify-by source, and compute the value for the
  user's own situation — never present as generic "hacks"
- `references/glossary.md` — Icelandic ⇄ English term glossary with usage
  gotchas (gjalddagi vs eindagi, afborgun vs innborgun, ráðstöfun vs úttekt).
  Load whenever writing Icelandic or translating financial terms

## Guardrails

- **Always run sensitivity** on inflation, fund return, and horizon before
  giving a verdict. Single-scenario answers on 20-year questions mislead.
- **State the behavioral assumption** (passive vs snowball) any paydown
  verdict rests on.
- **Bracket table staleness**: `tax.py` embeds 2026 values; verify against
  skatturinn.is each January (the script's `--year` flag fails loudly), then
  run `payslip.py verify` as a regression check.
- **Legal availability ≠ modeling**: séreignarsparnaður cannot normally be
  drawn before retirement age outside the housing-redirect programs. Flag
  hypotheticals as hypothetical.
- **Official pages lag new laws** — a Skatturinn info page is never proof a
  scheme doesn't exist (see the verification workflow in
  `tax-law-navigation.md`).
- **Point users to their union's kjaramál desk** for payslip disputes and
  wage claims — it's free and it's what dues pay for.
- This is decision-support modeling, not financial advice; recommend users
  verify big moves with their bank, union, or a licensed advisor.
