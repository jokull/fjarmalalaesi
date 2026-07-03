# Icelandic Mortgage Market & Regulation — Reference (July 2026)

All amounts ISK. Rates change frequently — re-verify against lender
vaxtatöflur before modeling. Macro anchor: meginvextir SÍ **7.75%**,
CPI ~5.2%, next MPC decision Aug 19 2026.

## Contents

1. Lender landscape
2. Rates snapshot (July 2026)
3. Seðlabanki macroprudential rules (LTV, DSTI)
4. Refinancing mechanics and costs
5. Fasteignamat
6. Extra principal payments
7. Iceland-specific paydown factors
8. Market context

## 1. Lender landscape

**Commercial banks** (~68% of mortgage stock, falling):
- **Arion**: óverðtryggt breytilegir/föst 3 ár up to 40 yr; verðtryggt up
  to 25–30 yr (sources disagree whether currently breytilegir or föst 3 ár
  í senn — verify on arionbanki.is or its calculator API before citing);
  blandað lán. 80% LTV purchase (85% FTB); 70–80% refi split into grunnlán
  + viðbótarlán (+~0.7pp). Public calculator API (no auth):
  `POST apps.arionbanki.is/einstaklinglan/api/loancalculation/calculate`.
- **Íslandsbanki**: verðtryggt föst 5 ár í senn max 30 yr (Oct 2025 info —
  new verðtryggð lending was paused then, verify); refi capped at
  **70% LTV**; FTB viðbótarlán to 90%.
- **Landsbankinn**: óverðtryggt breytilegir = **meginvextir + 2.50% fixed
  spread** (post-vaxtadómur repricing); verðtryggt restricted to first-time
  buyers, max 20 yr, fixed only.

**Pension funds** (~27% of stock, rising; cheapest verðtryggð rates,
sjóðfélagi requirement, LTV 60–75% usually **against fasteignamat**,
primary residence only): Birta (vtr. breytilegir 3.30% — market floor,
óvtr. = meginvextir + 1.10%), Gildi 4.30% fixed (variable suspended
post-vaxtadómur), Brú/Stapi 4.10%, Frjálsi 4.39%, LIVE 4.40%, LSR 4.50%.
Pension funds undercut banks ~0.5–1pp on verðtryggð; LV allows up to 40 yr
for first-time buyers.

**HMS hlutdeildarlán** (equity loans, first-time buyers under income
limits — 8.75M/yr single, 12.2M couples, +2.25M/child, 2026): HMS lends
**25%** of price (35% below lower thresholds), buyer 5% down, no interest
or installments; repaid as the same *percentage of property value* on sale
or at term (10 yr, extendable to 25). Approved new-builds under price caps
only.

**Others**: Auður (Kvika) óvtr. breytilegir 9.15%; sparisjóðir. Indó does
NOT offer mortgages (July 2026).

## 2. Rates snapshot (early July 2026)

**Óverðtryggð**: breytilegir 8.85% (Birta) – 10.25% (Landsbankinn);
föst 3–5 ár 8.35–9.73%.
**Verðtryggð (real)**: banks 4.35–5.0%; pension funds 3.30–4.50%.

Comparison rule: effective nominal cost of verðtryggt ≈ real rate +
expected inflation. At mid-2026 inflation, bank verðtryggð and óverðtryggð
price out similarly; pension-fund verðtryggð loans clearly cheapest if you
qualify and fit under ~65–70% LTV of fasteignamat.

**Vaxtadómur context**: Supreme Court (mál 24/2025, Oct 14 2025) ruled
discretionary variable-rate adjustment terms unlawful (Íslandsbanki lost;
Arion acquitted Dec 2025). Variable rates now anchor to the policy rate +
fixed contractual spread; several pension funds suspended variable lending.

## 3. Seðlabanki macroprudential rules

Legal basis: lög nr. 118/2016. Current:

- **LTV (veðsetningarhlutfall)**: general **80%**, first-time buyers **90%**
  (rules 217/2024 as amended by 1131/2025, effective Oct 31 2025).
- **DSTI (greiðslubyrðarhlutfall)**: mortgage service ≤ **35%** of net
  monthly income, **40%** FTB (rules 1130/2025, consolidated 1300/2025).
  **Standardized stress test — the binding constraint**: verðtryggð tested
  as 25-yr annuity at ≥3% real; óverðtryggð as 40-yr at ≥5.5% (actual rate
  if higher). A 40-year verðtryggt contract is *tested* as 25-year.
  Exemption quota: 10% of quarterly lending volume. Dec 2025 amendment
  counts payments to co-investing funds as debt service.
- Max terms are lender practice, not SÍ caps: óverðtryggt 40 yr; verðtryggt
  20–30 yr at banks, 40 yr FTB at some pension funds.

## 4. Refinancing mechanics and costs

- **No stimpilgjald on refinancing** — stamp duty (lög 138/2013) applies
  only to ownership transfers (0.8% individuals, halved FTB), not to
  veðskuldabréf.
- **Uppgreiðslugjald** (37. gr. laga 118/2016): only on fixed-rate loans
  during the fixed period, must reflect actual PV loss, ~0.2%/remaining
  fixed year, caps 1–2%. **Variable-rate loans: never.** All three big
  banks allow **1M kr/yr prepayment fee-free** even on fixed. Arion 3-yr
  verðtryggð resets: free exit in the last 90 days of each period. Fee is
  often 0 anyway when current market rates ≥ contract rate.
- **Cash friction to switch banks: ~80–100k** (lántökugjald ~60–65k,
  skjalagerð ~5–10k, greiðslumat ~7k/person, þinglýsing ~1.5–5k, misc).
  Trivial vs the stakes: 0.25pp on 80M = 200k/yr.
- **What actually decides a refi**: (1) weighted rate differential incl.
  viðbótarlán surcharges; (2) the LTV bracket — getting under 70% of
  fasteignamat unlocks pension funds and kills surcharges; (3) fixed-period
  exit timing; (4) passing greiðslumat under the §3 stress test; (5) beware
  the term-reset illusion (lower payment from restarting a 40-yr clock is
  not a saving).

## 5. Fasteignamat

HMS reassesses annually by statistical model (price level as of February);
**published June of year N, applies calendar year N+1**. Owners can appeal
until year-end. Fasteignamat 2027 (published June 2026): residential
**+1.2%** — a real-terms decline at ~5% inflation. Consequence: verðtryggð
balances grow with CPI while the LTV denominator stalls → LTV-driven refi
eligibility recedes in flat years. Fasteignagjöld: see
`tax-and-benefits.md` §7.

## 6. Extra principal payments (innborganir á höfuðstól)

- Self-service in netbanki/app at all banks; pension funds via mínar síður.
- Fees: none on variable; 1M kr/yr free on fixed (see §4); Birta exempts
  séreign-routed payments entirely.
- **Term vs payment**: borrower's choice — keep term (payment drops;
  usually the default) or keep payment (term shortens). A formal term
  change may cost a skilmálabreyting fee (~19–20k). Standing-order
  overpayment agreements available (umframgreiðslusamningur).
- Recalculation: an innborgun cuts the indexed balance króna-for-króna that
  day; all future indexation compounds off the smaller base — no catch-up.

## 7. Iceland-specific paydown factors

- Effective return on prepaying a verðtryggt loan = **real rate +
  inflation, risk-free and tax-free** (e.g. 5.99% real at 4.3% CPI ≈ 10.5%
  nominal) — currently dominates every retail savings product (taxed
  deposit at 7% nets ~5.5% after 22% fjármagnstekjuskattur).
- Prioritize the highest **real** rate; for mixed portfolios compare
  óverðtryggt nominal vs verðtryggt real + expected CPI over your horizon.
- **Séreignarsparnaður channel**: reinstated permanently June 2026 —
  applications from Oct 1 2026, retroactive to Jan 1 2026 (apply before
  Dec 1 2026 for the retroactive sweep). See `sereignarsparnadur.md`.
  (Note: some July-2026 sources still describe the bill as pending — the
  law passed June 18–19 2026, þskj. 1461/157.)

## 8. Market context (July 2026)

Prices ~flat nominally, falling in real terms (HMS vísitala íbúðaverðs
+2.15% y/y April 2026 vs 5.2% CPI). Volumes subdued. Íslandsbanki
forecast: +3.8% nominal 2026, +6.4% 2027, +7.2% 2028. High policy rate
pushes borrowers toward verðtryggð and pension-fund lending.

## Sources

- Seðlabanki: rules 217/2024, 1130/2025, 1131/2025, 1300/2025; FSN
  statement Oct 31 2025; policy-rate announcements (mbl.is, heimildin.is)
- Vaxtadómur: RÚV 2025-10-14; mbl.is 2025-12-10; ns.is/malaflokkar/vaxtamalid
- Lenders: aurbjorg.is/samanburdur/husnaedislan (comparison engine); Arion
  calculator API (live 2026-07-03); bank verðskrár (Arion May 2026,
  Íslandsbanki Mar 2026, Landsbankinn Apr 2026); birta.is, lsr.is,
  gildi.is, live.is, lifbru.is
- HMS: hlutdeildarlán (island.is/hlutdeildarlan, 2026 revision), fasteignamat
  2027 release, vísitala íbúðaverðs monthly reports
- Stimpilgjald: lög 138/2013; stjornarradid.is
- Data-quality flags: Aurbjörg table extraction partially garbled for Arion
  (cross-checked against Arion's own API — prefer the API); pension-fund
  rates as extracted, re-verify before hardcoding.
