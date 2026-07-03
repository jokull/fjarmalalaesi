# fjármálalæsi

An agent skill for Icelandic personal-finance literacy — payslips and wage
rights, the three-pillar pension system, verðtryggð (CPI-indexed) mortgages,
savings and investments, taxes, and safety nets. Built so anyone can point an
AI agent at their own numbers and get correct, Iceland-specific answers
instead of generic financial-calculator output.

**Fjármálalæsi** ("financial literacy") is what Icelanders call the skill of
understanding money. Iceland's system is genuinely idiosyncratic — mortgage
principals grow with inflation, ~90% of workers are covered by kjarasamningar
that set wage floors and benefit funds, pensions come in three layers with
wildly different tax and means-testing treatment, and tax on extra income
depends entirely on what it stacks on. Generic tools get all of it wrong.

## What the skill covers

- **Payslips & wages**: launaseðill line-by-line math, union benefits and
  rights (kjarasamningar), salary benchmarking for negotiation
- **Pensions**: the three pillars, séreignarsparnaður trade-offs (including
  the tax-free mortgage redirect reinstated June 2026), fund/provider choice
- **Housing**: correct verðtrygging mechanics validated against real bank
  data, prepayment and snowball valuation in today's kronur, the mortgage
  market and its regulation
- **Taxes**: staðgreiðsla bracket stacking — the number that decides most
  "should I take the money now or later" questions
- **Institutions & savings**: banks vs neobanks, deposit insurance, funds,
  government bonds, investment taxation
- **Safety nets & life events**: fæðingarorlof, atvinnuleysisbætur, námslán,
  barnabætur, debt help, renting
- **Data sources**: verified APIs (Hagstofa PX-Web, Arion calculator) and
  official sources with their lag traps documented

Scripts are Python 3 stdlib-only — nothing to install.

## Install

**Claude Code (plugin marketplace):**

```
/plugin marketplace add jokull/fjarmalalaesi
/plugin install fjarmalalaesi@fjarmalalaesi
```

**Any agent supporting the [Agent Skills](https://agentskills.io) standard:**

```
npx skills add jokull/fjarmalalaesi
```

**Manual copy:**

```
git clone https://github.com/jokull/fjarmalalaesi
cp -r fjarmalalaesi/skills/fjarmalalaesi ~/.claude/skills/
```

## Try it standalone

The scripts work without any agent:

```bash
cd skills/fjarmalalaesi/scripts

# What does a 5M prepayment on a verðtryggt loan actually buy, in today's kronur?
python3 verdtrygging.py lumpsum --balance 76000000 --apr 4.49 --months 276 \
    --inflation 4.3 --amount 5000000

# Effective tax on a séreign withdrawal stacked on a 600k/mo pension
python3 tax.py stacked --withdrawal 480000 --other-income 600000

# Live CPI and the current verðtrygging index from Hagstofa
python3 cpi.py latest

# The whole paydown-vs-invest decision in one command
python3 paydown_vs_invest.py --loans 76000000:4.49:276,8800000:5.99:276 \
    --pot 30000000 --tax-rate-now 0.4629 --inflation 4.3 --fund-return 7.0 \
    --horizon-years 20 --retirement-other-income 300000 --drawdown-years 15
```

## Caveats

Decision-support modeling, not financial advice. Tax brackets, benefit
amounts, and program rules are point-in-time (2026) — the scripts and
references say where to verify current values (skatturinn.is, sedlabanki.is,
hms.is, island.is). Verify big moves with your bank, union, or a licensed
advisor.

## License

MIT
