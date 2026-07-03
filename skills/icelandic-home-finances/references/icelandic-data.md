# Reliable Icelandic Data Sources for Financial Decisions

Where to get trustworthy numbers, how fresh each source is, and which to
prefer when they disagree. Machine-readable sources first. Verified July
2026 — URL structures occasionally change; the institutions don't.

## Principles

1. **Primary over secondary**: Hagstofa/Seðlabanki/Skatturinn/HMS over news
   articles or bank blog posts. News is useful for *discovering* changes
   (new laws, rate decisions), primary sources for the numbers themselves.
2. **Know each source's lag** — several official APIs lag their own PDF
   publications (noted per source below).
3. **Rates and thresholds are point-in-time**: anything you hardcode
   (tax brackets, lender rates, benefit amounts) needs a "verify at source"
   note and a refresh cadence.

## 1. Inflation & CPI — Hagstofa Íslands

**PX-Web API** (no auth, POST JSON): base
`https://px.hagstofa.is/pxis/api/v1/is/` (swap `/is/`→`/en/` for English).
GET a folder to list tables; POST a query for data.

- `Efnahagur/visitolur/1_vnv/1_vnv/VIS01000.px` — headline CPI by
  **measurement month** (items: `index`, `change_A` = YoY inflation).
- `.../VIS01004.px` — **VNV til verðtryggingar**, keyed by the month the
  value *applies to loan indexation* (measurement + 2 months, per 14. gr.
  laga 38/2001). **Use this for mortgage models.**
- Gotchas: variable codes are non-ASCII (`Mánuður`, `Vísitala`) — send
  byte-exact UTF-8; month keys `YYYYMMM` (`2026M06`); `"filter":"top"`
  returns latest N.
- `scripts/cpi.py` in this skill wraps both tables.

Publication schedule: measured mid-month, published end of month (~second-
to-last working day, 09:00), applies to indexation from M+2. Release
articles at hagstofa.is → Talnaefni → Efnahagur → Verðlag.

## 2. Inflation forecasts — Seðlabanki Peningamál

- **Peningamál** (quarterly: Feb/May/Aug/Nov) is the authoritative forecast.
  Tafla 4 = annual CPI averages; Tafla 5 = quarterly path. PDF + spátöflur
  appendix at sedlabanki.is → Ritið Peningamál.
- **The Hagstofa þjóðhagsspá PX-Web API
  (`Efnahagur/Efnahagur__thjodhagsspa/`) lags Peningamál by weeks or
  months** — convenient but cross-check the latest PM PDF before using.
- For horizons beyond the forecast window: 2.5% (the target) is the
  standard terminal assumption; always run ±1.5pp sensitivity.

## 3. Policy rate & official rates — Seðlabanki

- Current meginvextir: sedlabanki.is front page; time series at
  sedlabanki.is/gagnatorg (data portal, CSV/Excel exports).
- MPC decision calendar published yearly (≈8 meetings; none in June/July).
- Statutory rates per lög 38/2001 (dráttarvextir etc.): SÍ publishes
  monthly under "Vextir samkvæmt lögum".

## 4. Mortgage rates — lenders

- **Arion calculator API** (verified working, no auth):
  `POST https://apps.arionbanki.is/einstaklinglan/api/loancalculation/calculate`
  with `Origin: https://www.arionbanki.is` header — returns current rates
  and full payment schedules incl. `indexIncrement` (verðbætur). The
  cleanest machine-readable bank-rate source.
- **Aurbjörg** (aurbjorg.is/samanburdur/husnaedislan) — independent
  comparison engine across banks + pension funds. Good discovery tool;
  re-verify extracted numbers on the lender's own vaxtatafla.
- **Bank rate pages** (JS-rendered — fetch may need a browser):
  arionbanki.is, islandsbanki.is, landsbankinn.is; each also publishes a
  **verðskrá PDF** (fee schedules: lántökugjald, skjalagerð, uppgreiðsla).
- **Pension funds** (usually static HTML, easy to fetch): birta.is/lan,
  lsr.is/lan, gildi.is/lan, live.is/lan, lifbru.is/lan, frjalsi.is —
  typically the cheapest verðtryggð rates, LTV vs fasteignamat.

## 5. Housing market & property values — HMS & Fasteignaskrá

- **Fasteignamat**: reassessed annually, **published early June of year N,
  in force for calendar year N+1**. Individual property lookup at
  fasteignaskra.is / island.is (public: matsverð, size, lot).
- **Vísitala íbúðaverðs** (monthly price index) + **mánaðarskýrslur**
  (market reports: volumes, rates, lender shares): hms.is/skyrslur. Note
  hms.is sometimes bot-challenges scrapers.
- Purchase agreements (kaupsamningar) data: HMS publishes counts/volumes
  monthly; raw registry data via Fasteignaskrá.
- Fasteignagjöld by municipality: each municipality's álagningarforsendur;
  Byggðastofnun publishes an annual all-municipality comparison PDF; ASÍ
  (vinnan.is) does an annual survey.

## 6. Taxes & benefits — Skatturinn, island.is, TR

- **skatturinn.is/einstaklingar/helstutolur/{YEAR}/** — one page with the
  year's key numbers: brackets, persónuafsláttur, fjármagnstekjuskattur,
  rental taxable share, erfðafjárskattur threshold. **Refresh hardcoded
  values from here each January.**
- skatturinn.is/einstaklingar/stadgreidsla/skattthrep/{YEAR}/ — brackets.
- **island.is** — authoritative program pages (vaxtabætur, húsnæðisbætur,
  hlutdeildarlán incl. income limits, heimagisting, erfðafjárskattur) and
  the Stjórnartíðindi (legal gazette) archive for regulations.
- **TR (Tryggingastofnun)**: island.is/s/tryggingastofnun/fjarhaedir —
  ellilífeyrir amounts, frítekjumörk, skerðing parameters.
- Caveat: Skatturinn's program pages can lag new legislation by months
  (e.g. the June 2026 séreign law) — for brand-new law, go to Alþingi.

## 7. Legislation — Alþingi

- **Consolidated current law**: althingi.is/lagas/nuna/{YEAR}{NUMBER}.html
  (e.g. `2001038.html` = lög 38/2001).
- **Bills and passed texts**: track a mál via
  althingi.is/thingstorf/…/ferill/{þing}/{málsnr}; the final passed text is
  the last þingskjal ("lög í heild"). Parliamentary answers (svör) often
  contain authoritative formulas — e.g. þskj. 1393/148 documents the exact
  verðtryggð annuity formula.
- Regulations (reglugerðir): island.is/reglugerdir/nr/{NNNN-YYYY}.

## 8. Personal data (the user's own numbers)

- **Netbanki/app** of each lender: exact loan balances, APR, remaining
  term, grunnvísitala — always prefer these over estimates.
- **island.is mínar síður**: tax returns, fasteignir owned, vehicle/property
  registrations.
- **skatturinn.is þjónustusíða**: framtal history, staðgreiðsla records;
  the séreign-to-mortgage application portal (from Oct 2026).
- **Lífeyrisgáttin** (lifeyrisgattin.is): consolidated view of accrued
  pension rights across all funds — the source for "expected retirement
  income", which drives drawdown-tax modeling.
- Meniga or bank exports for spending data.

## Freshness summary

| Data | Cadence | Lag trap |
|---|---|---|
| CPI | monthly, end of month | applies to loans at M+2 (VIS01004 handles it) |
| Inflation forecast | quarterly PM | Hagstofa API lags the PM PDF |
| Policy rate | ~8 decisions/yr | none — front page |
| Lender rates | ad hoc | comparison sites lag lender pages |
| Fasteignamat | annual (June, for next year) | frozen 12 months regardless of market |
| Tax brackets/credits | annual (January) | hardcoded values go stale every Jan 1 |
| Benefit amounts (TR, húsnæðisbætur) | annual, sometimes mid-year | program pages lag new laws |
