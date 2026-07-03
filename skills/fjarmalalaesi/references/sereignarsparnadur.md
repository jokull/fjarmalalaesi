# Séreignarsparnaður & Housing Programs — Reference (July 2026)

Third-pillar private pension (viðbótarlífeyrissparnaður) and its tax-free
mortgage-redirect programs. All amounts ISK.

## Contents

1. Baseline séreignarsparnaður rules
2. Séreign → mortgage principal (permanent law, 2026)
3. Fyrsta íbúð (first home) program
4. Redirect mechanics
5. Modeling quantities
6. Retirement drawdown & TR interaction

## 1. Baseline rules

- Employee contributes **2–4%** of gross wages (4% = tax-deductible ceiling);
  employer mótframlag typically **2%** (triggered by ≥2% employee, standard
  in kjarasamningar).
- **EET tax model**: contributions pre-tax; returns accumulate free of
  fjármagnstekjuskattur; withdrawals taxed as ordinary wage income at the
  brackets then in force.
- Withdrawal from **age 60**, lump or paced (pacing keeps withdrawals in the
  low bracket and soaks persónuafsláttur).
- Fully heritable (passes to spouse/children — unlike skyldulífeyrir).

## 2. Séreign → mortgage principal (the redirect)

**History**: introduced 2014 (lög 40/2014, leiðréttingin era, leidretting.is),
repeatedly extended, **lapsed Dec 31 2025**, then made **permanent** by a new
law passed June 18–19 2026 (mál 564/157, þskj. 1461; frumvarp from
fjármálaráðherra Daði Már Kristófersson).

**New law provisions**:

- **Cap per person per 12 months: 500,000 kr** (own ≤4% max 333,000 +
  employer ≤2% max 167,000). ≈ 41,667 kr/month.
- **Couples: 500k each = 1,000,000 combined** — the old lower joint couple
  cap (750k) is abolished; the limit is per-individual in all cases.
- Caps **CPI-indexed each Jan 1 from 2027** — grow them with the same
  inflation series as the mortgage in projections.
- **120 months cumulative (samanlagt), not consecutive** — pause/resume
  allowed. Months used under the 2014–2025 scheme **count against** the 120.
  Skatturinn's portal is expected to show used/remaining months.
- Eligibility: loan secured by mortgage on íbúðarhúsnæði where the applicant
  has lögheimili; **≥30% ownership**; loan taken to acquire own-use housing.
- **Applications open Oct 1, 2026** at Skatturinn; **retroactive to Jan 1,
  2026** if the application is received **before Dec 1, 2026** (contributions
  accumulated since January swept to the mortgage in a lump). Later
  applications apply from the submission month.
- Voluntary; lenders cannot compel use.

## 3. Fyrsta íbúð (lög 111/2016) — never lapsed

- First home, or no residential property owned in past 5 years; ≥30% share;
  apply within 12 months of purchase contract.
- Two methods: (a) tax-free lump withdrawal of accumulated séreign toward
  the purchase (reach-back to July 2014), (b) ongoing monthly redirect.
- Same caps: 500,000/yr per person → max ~5,000,000 over the 10-year window.
- June 2026 law converts the window to cumulative-120-months and allows
  carrying the benefit to a replacement home.
- Óverðtryggð-loan special rule: contributions may cover installments
  (afborganir), 100% in year 1 declining 10pp/yr; verðtryggð → principal only.

## 4. Redirect mechanics

1. Apply at Skatturinn (from Oct 1 2026): choose custodian and **which
   loan(s)** — funds go "inn á höfuðstól valinna lána", so target the
   highest-APR loan.
2. Skatturinn verifies and instructs the vörsluaðili (pension fund), which
   **pays the lender directly** ≥4×/year. Money never touches the borrower.
3. Both verðtryggð and óverðtryggð loans qualify.
4. On a verðtryggt annuity loan, each redirected krona permanently removes
   indexed principal — effective risk-free return = real rate + indexation,
   tax-free.

## 5. Modeling quantities

- **Tax advantage of the redirect** = the marginal tax otherwise due at
  drawdown: **0–46.29% depending on what the withdrawal stacks on** —
  compute it with `scripts/tax.py stacked`, never assume a floor. With a
  full career pension underneath it's typically 31.49–37.99%; with little
  other income and a long drawdown, persónuafsláttur can push the
  effective rate below 20%. Redirected kronur land at 100%.
- **To hit the 500k/yr cap** requires gross wages ≥ ~694k/mo (500k = 6% of
  8.33M/yr); below that, redirect = 6% of gross.
- Amounts above the cap (employer >2%, contributions >4%, or 6% of higher
  salaries) stay in the fund as normal pension savings — not forfeited.
- **Non-cash**: the redirect never passes through take-home pay. In household
  cash-flow models it reduces loan principal without touching the budget.
- The redirect competes with keeping séreign to retirement, which grows
  untaxed AND is TR-clawback-free (§6) — the comparison is genuinely close;
  model both.

## 6. Retirement drawdown & TR (almannatryggingar)

- Séreign drawdown is wage-taxed (stack it on other retirement income to get
  the true rate — see `scripts/tax.py stacked`).
- **Frjáls séreign withdrawals are fully exempt from TR ellilífeyrir
  means-testing** (since 2017; disability benefits differ). Skyldulífeyrir,
  wages, and capital income are clawed back at **45%** above the frítekjumark
  (43,658/mo almennt, 2026); frjáls séreign is the only retirement asset
  with a 0% TR clawback. **Caution: tilgreind séreign (the 3.5% carved from
  the mandatory 15.5%) DOES count against TR since Jan 2023** — see
  `pension-system.md`. "Séreign" without a qualifier is ambiguous; the
  exemption covers the 2–4%+2% viðbót only.
- Consequence for paydown-vs-keep models: liquidating séreign early to hold
  taxable savings instead is doubly penalized later (22% fjármagnstekjuskattur
  on returns + 45% TR clawback on that capital income), while redirecting to
  the mortgage converts it to home equity (no clawback, but illiquid).

## Open items (verify when relevant)

- Stjórnartíðindi law number for the 2026 act wasn't yet indexed at research
  time — cite mál 564/157, þskj. 1461.
- Skatturinn's public pages were not yet updated for the new law in early
  July 2026; expect updates near Oct 1, 2026.

## Sources

- Alþingi 157. löggjafarþing mál 564: frumvarp þskj. 953, nefndarálit þskj.
  1280, lög í heild þskj. 1461 — althingi.is/altext/157/s/{0953,1280,1461}.html
- stjornarradid.is 2026-01-06 (bill announced), 2026-02-09 (made permanent)
- skatturinn.is/einstaklingar/skattamal/nyting-sereignarsparnadar/ (overview,
  almenn ráðstöfun, fyrsta íbúð); leidretting.rsk.is (legacy portal)
- Stapi lífeyrissjóður "Séreign inn á lán — ný lög samþykkt"; Vísir 2026-07-02
- Íslandsbanki "Skattgreiðslur og skerðingar" (séreign TR exemption);
  lifeyrismal.is Q&A
