# Verðtrygging: CPI-Indexed Mortgages — Technical Reference (July 2026)

## Contents

1. Legal & mechanical basis
2. The index: VNV and the two-month lag
3. Amortization formulas (as banks implement them)
4. Dynamics: negative amortization, real vs nominal
5. Restrictions on verðtryggð loans (2021–2025)
6. Verðtryggt vs óverðtryggt trade-offs
7. Rate environment July 2026
8. Hagstofa PX-Web API (see also `scripts/cpi.py`)

## 1. Legal & mechanical basis

- **Lög um vexti og verðtryggingu nr. 38/2001, VI. kafli** (13.–16. gr.):
  indexation of ISK loans only against **vísitala neysluverðs** (Hagstofa);
  equity-index linkage banned for consumer mortgages (l. 36/2017).
- **The timing rule (14. gr., l. 51/2007)**: *"Vísitala sem reiknuð er og
  birt í tilteknum mánuði gildir um verðtryggingu … frá fyrsta degi þar
  næsta mánaðar"* — **CPI measured/published in month M governs indexation
  from the 1st of month M+2**. (June 2026 CPI 690.7 → applies August 2026.)
- **Seðlabanki rules nr. 218/2023** (carrying 877/2018 mechanics): indexed
  loans minimum term **5 years**; **höfuðstólsaðferð** — on each gjalddagi
  the principal is indexed up FIRST, then interest and afborgun are computed
  on the indexed balance; verðbætur itemized on payment receipts. Daily
  linear interpolation between monthly index values for mid-month gjalddagar.
- Grunnvísitala = the verðtrygging index effective at disbursement, written
  into the bond; each payment date uses `V(t)/V_base`.
- Höfuðstólsaðferð (banks) and greiðsluaðferð (index the payment; old ÍLS)
  are cash-flow-identical (confirmed in Alþingi answer 999/148) — model
  whichever is easier.

## 2. The index: two series, two keyings

Base May 1988 = 100. Measured mid-month, published end of month.

| Hagstofa table | Content | Keyed by |
|---|---|---|
| `VIS01000` | VNV (headline CPI) + MoM/YoY changes | **measurement month** |
| `VIS01004` | **VNV til verðtryggingar** (+ legacy lánskjaravísitala) | **month the value applies to indexation** (= measurement + 2) |

**Use VIS01004 for loan models** — it already encodes the M+2 lag.
`scripts/cpi.py` fetches both.

## 3. Amortization formulas (primary source: Alþingi þskj. 1393/148)

Notation: `H_t` = remaining base-price principal, `V_t/V_0` = cumulative
index ratio since disbursement, `R` = monthly real rate, `n_t` = months left.

**Jafngreiðslulán (annuity)**:
```
P_t = R × H_t × (V_t/V_0) / [1 − (1+R)^(−n_t)]      # payment
I_t = R × H_t × (V_t/V_0)                            # interest
A_t = P_t − I_t                                      # principal repaid
```
The loan is an ordinary annuity **in real terms**; the nominal payment grows
one-for-one with CPI. With breytilegir vextir the annuity is recomputed on
each rate change over the remaining term.

**Jafnar afborganir (equal principal)**:
```
A_t = (H_orig / n_total) × (V_t/V_0)    # constant in real terms
P_t = A_t + R × H_t × (V_t/V_0)         # declining in real terms
```

**Equivalent monthly recurrence** (what `scripts/verdtrygging.py` implements;
identical to the closed form when the rate is unchanged):
```
balance ×= (1 + monthly_inflation)      # verðbætur capitalize FIRST
interest = (r/12) × balance
payment  = PMT(balance, r/12, months_left)   # annuity case
balance −= (payment − interest)
```

## 4. Dynamics: negative amortization

- The balance grows nominally whenever monthly indexation exceeds the
  scheduled afborgun. On a fresh 40-year annuity the first afborgun is
  ~0.08–0.15%/mo of balance while 4–5% inflation adds 0.33–0.42%/mo — the
  balance **rises for years while the borrower pays faithfully**.
- Crossover (nominal balance peak): typically year 15–25 on a 40-year
  annuity at 3–5% inflation; year 8–14 on 25-year; much earlier for jafnar
  afborganir.
- **Correct interpretation**: a verðtryggt lán is a *real* contract — the
  real balance declines exactly on schedule from month one, and the contract
  rate is a real rate. Effective nominal cost ≈ `(1+r_real)(1+π) − 1`
  (4.9% real at 5.2% CPI ≈ 10.4% nominal).
- Practical bite of the nominal effects: LTV falls only if house prices
  outpace CPI (refinance thresholds can stay out of reach for years); equity
  builds slowly; the payment rises nominally forever. The annuity's low
  entry payment is borrowed from the future.
- Prepayment consequence: extra principal on a verðtryggt loan "earns"
  `r_real + π` risk-free and tax-free (~10.4% nominal at July 2026 levels) —
  compare against taxed deposit/fund returns.

## 5. Restrictions on verðtryggð loans (2021–2025)

- **Seðlabanki LTV rules**: general cap **80%**, first-time buyers **90%**
  (FSN 31 Oct 2025; was 85/85 since 2022).
- **DSTI rules (nr. 1130/2025 + 1300/2025)**: greiðslubyrði ≤ **35%** of
  ráðstöfunartekjur (**40%** first-time buyers). Test assumptions: verðtryggð
  loans stress-tested at **≥3% real rate and max 25-year amortization**;
  óverðtryggð at **≥5.5% and max 40 years** — regardless of actual contract.
  Lenders may exceed for 10% of quarterly volume.
- **Product restrictions (autumn 2024–2025)**: Landsbankinn — verðtryggð
  loans first-time-buyers-only, max 20 years, fixed only. Íslandsbanki —
  fixed 5-yr resets, max 30 years. Arion — still offers verðtryggð
  breytilegir, max 25 years. **40-year verðtryggð annuities effectively
  survive only for first-time buyers, mostly at pension funds** (e.g. LV up
  to 40 yr FTB at ≤70% LTV).
- **Vaxtamálið (2025 Supreme Court)**: Íslandsbanki's variable-rate terms
  ruled unlawful (Oct 14, 2025 — discretion too open-ended); Arion acquitted
  (Dec 10, 2025); Landsbankinn cases concluded Dec 2025. Aftermath: variable
  rates re-anchored to SÍ policy rate + fixed spread (Landsbankinn: policy
  + 2.50%); Gildi suspended variable lending entirely.

## 6. Verðtryggt vs óverðtryggt trade-offs

- **Breakeven inflation**: `π* = (1+i)/(1+r_real) − 1`. At July 2026 Arion
  rates (i=8.96% óvtr., r=4.90% vtr.): **π\* ≈ 3.9%**. Actual CPI 5.2% →
  verðtryggt currently ~1.4pp/yr more expensive in total accrual, but with
  far lower cash payments (the excess capitalizes).
- **Greiðslubyrði**: initial payment per 10M borrowed (annuity):
  óverðtryggt breytilegt 8.96%/40yr ≈ 76.8k; verðtryggt 4.90%/25yr ≈ 57.9k.
  Verðtryggt starts ~25% cheaper at a 15-year-shorter term — but grows with
  CPI while the óverðtryggt payment falls in real terms. Paths typically
  cross in 5–12 years.
- **Blönduð lán** (all banks): split balance; halves inflation pass-through
  while keeping the entry payment between the pure forms. Arion prices the
  indexed half of a blend cheaper (4.64%) than pure indexed (4.90%).
- Evaluate breakeven against *expected* rate paths, not spot: the spread
  `i − r_real` embeds market inflation expectations + a premium.

## 7. Rate environment (July 2026 — verify before relying)

- Meginvextir SÍ **7.75%** (raised Mar 2026, held May); CPI **5.2%** YoY;
  PM 2026/2 sees inflation declining toward target by ~2028.
- New verðtryggð mortgages: banks 4.6–4.9% real; pension funds 4.3–4.4%
  (LV 4.40%, Gildi 4.30%) at ≤70% LTV.
- New óverðtryggð: 9.0–10.9% variable, 8.3–9.7% fixed.
- Pension funds undercut banks by ~0.5–1pp on verðtryggð but cap LTV ~70%;
  bank share of mortgage stock 68.2% end-2025, pension funds 27.3% rising.
- Machine-readable rate source: Arion's public calculator API
  (`POST https://apps.arionbanki.is/einstaklinglan/api/loancalculation/calculate`,
  no auth, needs `Origin: https://www.arionbanki.is` header) returns current
  rates and payment schedules incl. `indexIncrement`.

## 8. Hagstofa PX-Web API

Run `python3 scripts/cpi.py` (fetches current values). Raw endpoints:

```
POST https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/1_vnv/VIS01004.px
  {"query":[{"code":"Vísitala","selection":{"filter":"item","values":["financial_indexation"]}},
            {"code":"Mánuður","selection":{"filter":"top","values":["24"]}}],
   "response":{"format":"json"}}
POST .../VIS01000.px   # headline CPI: values ["CPI"], Liður ["index","change_A"]
```

Gotchas: variable codes contain non-ASCII (`Mánuður`, `Vísitala`) — send
byte-exact UTF-8; month keys are `YYYYMMM` (`2026M06`); `"filter":"top"`
returns latest N. VIS01004 is keyed by *effective* month (M+2 already
applied). The þjóðhagsspá forecast API lags Peningamál — cross-check the PM
PDF at sedlabanki.is.

## Sources

- Lög 38/2001: althingi.is/lagas/nuna/2001038.html · SÍ rules 218/2023:
  sedlabanki.is/log-og-reglur/nr/4209 · 877/2018 text on island.is
- Formulas: Alþingi þskj. 1393/148 and 999/148
- DSTI: rules 1130/2025 + 1300/2025 (island.is/stjornartidindi); LTV: FSN
  statement 31 Oct 2025 (sedlabanki.is)
- Hagstofa: June 2026 CPI release; PX-Web tables VIS01000/VIS01004
- Vaxtamálið: RÚV 2025-10-14, mbl.is 2025-12-10 and 2025-12-22
- Rates: Arion calculator API (live 2026-07-03); landsbankinn.is/lanaframbod;
  live.is/lan; gildi.is/lan; Peningamál 2026/2
- Staleness flags: Íslandsbanki rates are Oct 2025 announcements (JS-rendered
  table, re-verify); whether their verðtryggð fixed lending pause has lifted.
