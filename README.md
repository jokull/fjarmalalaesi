# fjármálalæsi

Agent skills for navigating Icelandic household finances — verðtryggð
(CPI-indexed) mortgages, séreignarsparnaður, and the tax system around them.
Built so anyone can point an AI agent at their own numbers and get correct,
Iceland-specific modeling instead of generic mortgage-calculator answers.

**Fjármálalæsi** ("financial literacy") is what Icelanders call the skill of
understanding money. Iceland's housing finance is genuinely unusual — mortgage
principals grow with inflation, pension redirects pay down loans tax-free, and
tax on extra income depends entirely on what it stacks on — and generic tools
get all of it wrong.

## Skills

### `icelandic-home-finances`

- **Correct verðtrygging mechanics**: monthly CPI indexation of principal,
  jafngreiðslur (annuity) recalculated on the indexed balance — the actual
  bank formula, validated against real Arion Banki loan data
- **Prepayment valuation**: lump sums and snowball strategies, valued as the
  present value of avoided payments in today's kronur (never nominal sums
  across decades)
- **Tax stacking**: staðgreiðsla brackets applied marginally on top of
  existing income — the number that decides séreign drawdown questions
- **Paydown vs invest**: the full decision framework with sensitivity across
  inflation, fund returns, horizons, and retirement income
- **Reference docs**: verðtrygging law and mechanics, séreignarsparnaður
  programs (including the June 2026 reinstatement of the mortgage redirect),
  the mortgage market and its regulation, taxes and benefits

Scripts are Python 3 stdlib-only — nothing to install.

## Install

**Claude Code (plugin marketplace):**

```
/plugin marketplace add jokull/fjarmalalaesi
/plugin install icelandic-home-finances@fjarmalalaesi
```

**Any agent supporting the [Agent Skills](https://agentskills.io) standard:**

```
npx skills add jokull/fjarmalalaesi
```

**Manual copy:**

```
git clone https://github.com/jokull/fjarmalalaesi
cp -r fjarmalalaesi/skills/icelandic-home-finances ~/.claude/skills/
```

## Try it standalone

The scripts work without any agent:

```bash
cd skills/icelandic-home-finances/scripts

# What does a 5M prepayment on a verðtryggt loan actually buy, in today's kronur?
python3 verdtrygging.py lumpsum --balance 76000000 --apr 4.49 --months 276 \
    --inflation 4.3 --amount 5000000

# Effective tax on a séreign withdrawal stacked on a 600k/mo pension
python3 tax.py stacked --withdrawal 480000 --other-income 600000

# The whole paydown-vs-invest decision in one command
python3 paydown_vs_invest.py --loans 76000000:4.49:276,8800000:5.99:276 \
    --pot 30000000 --tax-rate-now 0.4629 --inflation 4.3 --fund-return 7.0 \
    --horizon-years 20 --retirement-other-income 300000 --drawdown-years 15
```

## Caveats

Decision-support modeling, not financial advice. Tax brackets and program
rules are point-in-time (2026) — the scripts and references say where to
verify current values (skatturinn.is, sedlabanki.is, hms.is). Verify big
moves with your bank or a licensed advisor.

## License

MIT
