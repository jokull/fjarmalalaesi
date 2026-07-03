# Icelandic Taxes & Benefits Around Homeownership — 2026 Reference

All amounts ISK. "Álagning 2026" = assessment published mid-2026 on income year
2025. Verify current-year values at skatturinn.is each January.

## Contents

1. Income tax (staðgreiðsla) 2026
2. Álagning vs staðgreiðsla — why tax bills land in June
3. Vaxtabætur — abolished after 2026
4. Húsnæðisbætur (renters)
5. Capital gains on residential property
6. Rental income (long-term and Airbnb/heimagisting)
7. Fasteignagjöld (Reykjavík 2026)
8. Inheritance/gifts toward down payments
9. TR ellilífeyrir skerðingar — critical for retirement drawdown modeling

## 1. Income tax 2026 (staðgreiðsla)

| Bracket | Monthly income | Rate | of which state | of which útsvar (avg) |
|---|---|---|---|---|
| 1 | 0 – 498,122 | **31.49%** | 16.55% | 14.94% |
| 2 | 498,123 – 1,398,450 | **37.99%** | 23.05% | 14.94% |
| 3 | above 1,398,450 | **46.29%** | 31.35% | 14.94% |

- **Persónuafsláttur: 72,492/mo = 869,898/yr**, fully transferable between
  spouses. From 2026 it can no longer offset fjármagnstekjur.
- Annual thresholds: 5,977,470 (1→2) and 16,781,397 (2→3). Indexed annually
  (2026: +5.5% = inflation + 1% productivity).
- Withholding embeds meðalútsvar 14.94%; Reykjavík charges the max 14.97% —
  the 0.03pp difference settles at álagning.
- Fjármagnstekjuskattur (capital income): **22%**.

## 2. Álagning vs staðgreiðsla

Framtal filed ~March; álagning published late May (2026: May 21); refunds
June 1, amounts owed collected from June onward. Everything not withheld
monthly lands here: capital income tax on rent/interest/gains, útsvar
difference, benefit determinations. **This is why Airbnb or capital-gains tax
on year N income becomes a cash outflow in June of year N+1** — model it as
a one-off in June.

## 3. Vaxtabætur — abolished

Paid for the **last time in 2026** (on 2025 interest). Replaced by targeted
measures (húsnæðisbætur for renters, hlutdeildarlán, first-home séreign).
**Model zero mortgage-interest benefit from 2027 onward.** It was already
dead for middle incomes: 8.5% income phase-out killed the couple's max
630,000 benefit at ~7.4M combined annual income, and net assets (incl. home
equity) above 19.2M (couple) → zero. The 2024 sérstakur vaxtastuðningur was
a one-off, never repeated.

## 4. Húsnæðisbætur (renters only)

HMS-administered. 2026: max benefit 50,792/mo (1 person) up to 99,552 (6+);
reduction 11% of household income above limits (6.37M/yr for 1 person …
12.48M for 6+); asset phase-out 13.9M→22.24M; capped at 75% of rent.

## 5. Capital gains on residential property

Basis: 17. gr. laga nr. 90/2003.

- **2-year rule**: gain tax-free if owned 2 full years, provided total
  residential property owned ≤ 600 m³ (individual) / 1,200 m³ (couple) —
  cubic meters, ~230/460 m² floor area. Own-use property exempt from the
  size cap.
- **Under 2 years**: taxable as fjármagnstekjur 22%, BUT deferral (frestun)
  available for 2 years; buying replacement housing within that window rolls
  the gain into the new home's cost basis instead. No replacement → taxed
  retroactively with surcharge.

## 6. Rental income

### Long-term (húsaleigulög residential lease)

- Fjármagnstekjuskattur 22% on **75% of gross rent from income year 2026**
  → effective **16.5%**. (Was 50% taxable / 11% effective through 2025 —
  check which year's rule applies to the income being modeled.)
- Conditions: residential use under húsaleigulög, max 2 properties. Gross
  basis, no expense deductions. Otherwise → business income.
- Special offset: renting out your home while renting elsewhere — rent paid
  is deductible against rent received.

### Heimagisting (Airbnb-style)

- Register with sýslumaður annually (9,200 kr, display registration number);
  covers lögheimili + one personal-use property; max 5 rooms/10 guests.
- Stay within **90 rental days AND 2,000,000 kr gross per calendar year**
  (combined across properties): taxed as fjármagnstekjur **22% on 100% of
  gross** — no discount, no expense deductions (not even platform fees).
- **Exceed either limit → the entire year reclassifies as business income**
  (marginal wage-rate tax + tryggingagjald, possible VAT, rekstrarleyfi).
  Fines up to 1M for unregistered operation.
- Gistináttaskattur: zero for 2026; scheduled to return 400 kr/guest-night
  2027, 600 kr 2028 (verify — committee figures).

## 7. Fasteignagjöld (Reykjavík 2026)

- Residential fasteignaskattur: **0.18% of fasteignamat**; lóðarleiga 0.20%
  of lóðarmat (city-leased lots). Sorphirðugjald flat per bin.
- 11 equal installments Jan–Dec (≤25,000 total: single Jan 31 due date).
- Levied on fasteignamat as of Dec 31 prior year. Other municipalities:
  same structure, own rates (statutory max 0.5% residential) — fetch the
  municipality's álagningarforsendur when modeling outside Reykjavík.

## 8. Inheritance & gifts toward down payments

- Erfðafjárskattur **10%**; estate exemption 6,789,790 (2026, indexed).
- **Fyrirframgreiddur arfur** (advance inheritance): 10% from the first
  króna (no exemption), via erfðafjárskýrsla at sýslumaður.
- **No gift allowance exists**: beyond ordinary tækifærisgjafir, cash gifts
  are taxable income to the recipient at marginal wage rates (up to 46.29%).
  For down-payment-sized parental help, formal fyrirframgreiddur arfur at
  10% is almost always the right structure.

## 9. TR ellilífeyrir skerðingar — retirement drawdown modeling

2026 parameters (island.is/TR):

- Full ellilífeyrir **365,592/mo**; heimilisuppbót (living alone) 92,384/mo.
- Almennt frítekjumark **43,658/mo** (523,896/yr); additional atvinnutekju-
  frítekjumark 210,400/mo for employment income only.
- **Skerðing: 45%** of income above frítekjumark; full phase-out at other
  income ≈ 856,085/mo.

What counts against TR:

| Income type | Counts? |
|---|---|
| Lífeyrissjóður (occupational pension) drawdown | **Yes, in full** — the dominant clawback driver |
| Employment income | Yes, but with the extra 210,400/mo frítekjumark |
| Capital income (interest, dividends, **rent**, gains) | Yes, in full; **always split 50/50 between spouses** |
| **Séreignarsparnaður withdrawals** | **NO — exempt since 2017** |

**The modeling consequence**: séreign is TR-clawback-free retirement income,
while each extra króna of occupational pension or capital income above
~44k/mo destroys 0.45 kr of TR benefit *on top of* income tax. Combined
marginal wedges on occupational pension can reach ~65–70%. This makes
séreignarsparnaður structurally the best-treated retirement asset in the
system — a strong argument *against* liquidating it early, and it also means
long-term rental income (taxed 16.5%) still loses 45% to TR clawback for
pensioners. Model each income stream's TR interaction separately.

## Sources

- skatturinn.is — brackets: /einstaklingar/stadgreidsla/skattthrep/2026/ ·
  key figures: /einstaklingar/helstutolur/2026/ · söluhagnaður:
  /einstaklingar/fjarmagnstekjur/soluhagnadur/ · leigutekjur:
  /einstaklingar/fjarmagnstekjur/leigutekjur/
- stjornarradid.is 2025-12-23 "Skattabreytingar á árinu 2026" (indexation,
  rental share change, vaxtabætur sunset)
- island.is — vaxtabætur, húsnæðisbætur, heimagisting, erfðafjárskattur,
  fyrirframgreiddur arfur, ellilífeyrir fjárhæðir
- reykjavik.is/fasteignagjold; ASÍ municipal comparison vinnan.is
- islandsbanki.is "Úttekt séreignar hefur ekki áhrif á ellilífeyrisgreiðslur";
  TR guidance on capital income (45% clawback, spousal split)
