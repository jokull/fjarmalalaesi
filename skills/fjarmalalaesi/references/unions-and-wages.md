# Unions, Wages & Payslips — Reference (July 2026)

The union system, exact payslip mechanics, employee rights, and salary
benchmarking. Values are 2026 / stöðugleikasamningar (2024–2028) era.

## Contents

1. The union system
2. Payslip mechanics (see also `scripts/payslip.py`)
3. Rights every employee should know
4. Salary benchmarking (see also `scripts/wages.py`)
5. Negotiation practicals

## 1. The union system

- **Density ~90%** — highest in the OECD; coverage effectively universal
  because of **lög 55/1980, 1. gr.**: kjarasamningar terms are *minimum
  terms for everyone in the occupation and area, member or not* — contract
  terms below them are void. Non-members still pay the dues-equivalent.
- Federations: ASÍ (private, ~140k; SGS and VR/LÍV within it), BSRB
  (public), BHM (university-educated), KÍ (teachers). Biggest unions:
  VR (~40k), Efling (~27k).
- **What membership buys beyond the floor**: the kjaramál service desk
  (payslip checks, wage-claim enforcement incl. employer insolvency, legal
  aid) — *tell users to bring payslip disputes there first, it's free*;
  **sjúkrasjóður** (VR: 80% of 6-mo average wages for ~120–180 days;
  Efling: 80% rising to 100% after 5 yrs, cap ~1M/mo); orlofssjóður
  (summer houses); **starfsmenntasjóður** (VR/Efling: 90% of course cost,
  max 180k/yr, accumulates 3 yrs to 540k — chronically underused free
  money); VR additionally has **varasjóður** (a personal account, ~4% of
  one month's salary/yr, spendable on health/glasses/gym).
- **Dues: VR 0.7%, Efling 0.7%** of heildarlaun — the widely assumed "1%"
  is the employer's sjúkrasjóður premium, not member dues. Range 0.7–1%
  across unions. Deducted **post-tax** (pre-tax deductibility is a myth).

## 2. Payslip mechanics

Deduction order (verified against skatturinn.is; implemented in
`scripts/payslip.py`, which is verified field-for-field against payday.is):

1. Skyldulífeyrir 4% — pre-tax; fund dictated by kjarasamningur (VR→LIVE,
   Efling→Gildi, iðnaðarmenn→Birta, public→LSR/Brú)
2. Séreign 2–4% — pre-tax; triggers the 2% employer match (≥2% required)
3. Staðgreiðsla on (gross − pension) via brackets − persónuafsláttur
4. Stéttarfélagsgjald 0.7–1% of gross — post-tax

**Employer side — "what you're actually worth"** (per 100 kr salary):
11.5 mótframlag + 2 séreign match + ~7.2 tryggingagjald (6.35% on salary
+ employer pension) + 1.0 sjúkrasjóður + 0.25 orlofssjóður + ~0.3
starfsmenntasjóður + 0.1 VIRK ≈ **122.4 kr total cost** — before orlof
accrual (≥10.17%) and uppbætur. This is the number to use in
contractor-vs-employee and negotiation framing (`payslip.py total-cost`
covers the pension+tryggingagjald core ≈ 120.8; the sjóðir add ~1.6).

**Fixed annual bonuses** (SA agreements, pro-rated by worked weeks):
desemberuppbót **114,000** (2026), orlofsuppbót **62,000** (2026). Fixed
amounts — they don't scale with salary.

**Contractual raises** (stöðugleikasamningar, to Jan 2028): +3.5% (min
23,750 kr) each Jan 1 2025/2026/2027; taxtar additionally get a
kauptaxtaauki each Apr 1 (2026: +0.06%). Forsenduákvæði: the Sept 2026
inflation test (≤4.7% in August) can void the agreements — watch it.

**Orlof**: statutory 24 days = 10.17% of ALL wages incl. overtime
(formula: days/(260−days)); ladders to 30 days/13.04% with tenure.

## 3. Rights every employee should know

- **Uppsagnarfrestur** (VR): 1 week (first 3 mo) → 1 month → **3 months**
  after 6 months; extends to 4/5/6 months at ages 55/60/63 after 10 years
  with the company (employer side only). SGS/Efling similar but 2 months
  only after 2 years, 3 after 3.
- **Veikindaréttur**: 2 days per worked month in year 1 → 2 months after
  1 year → 4 after 5 → 6 after 10 (rolling 12 months), at ~full pay;
  +3 months for work accidents. Child illness: 12 days/yr (under 13).
- **Yfirvinna**: 1.0385% of monthly salary per hour (≈80% premium) at
  VR/SGS; iðnfólk two-tier 1.00/1.15%. Vaktaálag 33.3% evenings / 45%
  nights+weekends.
- **Jafnaðarkaup** (flat blended hourly rate) appears in NO kjarasamningur
  — it's only lawful if, each pay period, it beats the correct
  taxti+overtime split for the actual hours. Classic abuse target: young
  workers rostered evenings/weekends. The union back-computes and claims
  the difference.
- **Launaviðtal**: VR contract gr. 1.2.2 — right to a salary interview
  once a year, granted within 2 months of request, decision within 1
  month. (SGS/Efling contracts lack this clause.)
- **Gerviverktaka red flags**: one client, employer controls hours/place/
  tools, no financial risk, personal work duty. Real contractor status
  costs both pension halves, tryggingagjald, orlof, sick pay, notice, and
  uppbætur — equivalence requires a **38–70% markup** over the employee
  wage (union calculators: BHM "reiknivél fyrir útselda vinnu").
- **Pay secrecy is banned** (lög 150/2020, 6. gr. — you may always
  disclose your own pay). Jafnlaunavottun is abolished as of **Sept 1
  2026** (lög 53/2026), replaced by gender-pay-gap reporting at 50+
  employee firms — at those firms a job-grading and pay analysis must
  exist: ask "hvernig er starfið mitt flokkað og hvar ligg ég innan
  launabils flokksins?"

## 4. Salary benchmarking — "know your worth"

**Concepts first** (Hagstofa definitions — comparing the wrong one skews
20%+): **grunnlaun** (base only) < **regluleg laun** (contracted hours
incl. fixed overtime/vaktaálag — compare plain monthly offers against
this) < **heildarlaun** (everything — compare "total comp" claims).

**Live data — run `scripts/wages.py`** (Hagstofa launarannsókn PX-Web,
tables VIN02001–VIN02005, data through 2025, updated each May):
- 2025 medians (heildarlaun, full-time): all employees **948k**;
  stjórnendur 1,439k; sérfræðingar 1,040k (P10 803 / P75 1,258 / P90
  1,539); iðnaðarmenn 1,030k; skrifstofufólk 789k; ósérhæft 731k.
- Fine-grained by ÍSTARF95 code (VIN02001): tölvusérfræðingar (213)
  median heildarlaun 1,193k; verkfræði (214) 1,244k.
- Data lags ~5 months: uprate by the Jan 1 contractual raise (+3.5% for
  2026) or launavísitala.

**Other sources**: VR launarannsókn (public PDF, by job title — use
miðgildi, employers dispute the averages) + Launaspá VR (member ML tool);
kjarasamningar launatöflur are FLOORS (~476–540k) far below market
medians — never present a taxti as a benchmark; tekjublöð (August) are
útsvar-derived — include severance/benefits, exclude capital income; use
for named-role anecdotes only; ktn.is (kjaratölfræðinefnd) for neutral
wage-development stats; tekjusagan.is for long-run income by decile.

## 5. Negotiation practicals

- Private offers are all-in **heildarlaun** packages. The VR contract
  requires the employer to state the assumed overtime hours behind the
  package and, on request, demonstrate it beats the kjarasamningur.
  **Get the assumed hours in the written ráðningarsamningur** — hours
  beyond them are separately billable at 1.0385%/hour.
- Kjarasamningar raises are floors with no anti-absorption rule — a
  personal raise agreed near year-end may quietly "include" the January
  bump. Negotiate raises explicitly **"til viðbótar við
  kjarasamningsbundnar hækkanir"** and time launaviðtöl for autumn.
- **Hlunnindi math (skattmat 2026)**: company car = 28%/yr of purchase
  price taxable (EV 20%; price depreciates 10%/yr, max −50%) — a 10M
  petrol car in year 2 ≈ 2.52M taxable ≈ 1.17M/yr real tax cost at the
  top bracket. A "fríbíll" is a large taxable benefit, not a freebie.
  **The genuinely tax-free asks**: íþróttastyrkur ≤85,000/yr,
  samgöngustyrkur ≤138,000/yr (green commute), dagpeningar per RSK
  schedule, work phone for work use.
- Pension is levied on ALL wages (not just grunnlaun — folk claim), and
  uppbætur are fixed: negotiation value rides entirely on the monthly
  number and tax-free fringes.

## Caveats

Efling contract figures cited via the identical SGS–SA edition (Efling
PDF 403s). VR sjúkradagpeningar duration: live rules say 120+60 days,
older material 210. Starfsmenntasjóður employer premium ~0.2–0.3%
approximate. Member counts are best-available, not audited. EU
pay-transparency directive (2023/970) not yet in the EEA agreement —
no salary-range disclosure duty in Iceland yet.

## Sources

lög 55/1980, 80/1938, 30/1987 (orlof), 19/1979, 150/2020, 53/2026 ·
VR–SA and SGS–SA kjarasamningar 2024–2028 + published launatöflur (Jan
2026 PDFs) · SA vinnumarkaðsvefur (uppbætur, orlofsstigar, kauptaxtaauki,
forsenduákvæði) · skatturinn.is (helstutolur, skattmat reglur RSK
0601/2026, dagpeningar, iðgjald í lífeyrissjóði, tryggingagjald) ·
vr.is (félagsgjald, sjúkrasjóður reglugerð, varasjóður,
starfsmenntastyrkir, launaviðtal, launarannsókn sept 2025) · efling.is
(iðgjöld, sjúkradagpeningar) · starfsafl.is · ASÍ vinnuréttarvefur
(félagsgjöld, forgangsréttur, launamaður eða verktaki) · OECD/AIAS
ICTWSS Iceland country note · Hagstofa PX-Web launarannsókn
VIN02001–VIN02005 (queries verified July 2026) · ktn.is · tekjusagan.is ·
BHM/VM verktaka guidance · stjornarradid.is (jafnlaunavottun replacement,
June 2026)
