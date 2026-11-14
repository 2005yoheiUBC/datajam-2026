# Discussion note: 12 Nov 2026 — condos vs houses

## 1. What "gross yield" means
Gross yield = yearly revenue ÷ purchase price. It's a ratio, not dollars: 0.07 = **7% a year**.

## 2. Why Downtown looked "too cheap"
The neighbourhood ranking (notebook 02, Step 2) mixes property types. Downtown listings are almost all **condos**; most other areas are mostly **houses**. Each listing gets the price of its own type, so Downtown shows a condo price and Kitsilano shows a house price.

| Median assessed value | Condo | House |
|---|---|---|
| Downtown | $758K | $5.8M |
| Downtown Eastside | $618K | $1.6M |
| Kitsilano | $989K | $2.76M |

So the old top 5 partly just said "condos beat houses".

## 3. Fair comparison: each type ranked on its own
New **Step 2b** in `notebooks/02_where_and_what.ipynb` (≥50 listings of that type).

| Type | Area | Gross yield | Net yield (after costs) |
|---|---|---|---|
| Condo | Downtown | 7.4% | 2.5% |
| Condo | Downtown Eastside | 7.6% | 2.2% |
| Condo | West End | 5.8% | 1.5% |
| Condo | Kitsilano | 3.6% | 0.9% |
| Condo | Mount Pleasant | 4.6% | 0.8% |
| House | Kensington-Cedar Cottage (best house) | 2.3% | 0.7% |
| House | Dunbar Southlands (worst house) | 1.0% | — |

Houses earn similar revenue ($28–47K/yr) but cost 2–3× more, so every condo area on the list beats every house area. This still holds after strata fees (~$500/month for condos).

## 4. Proposal: 100% condos
- **Already what the model picks:** `analysis/current/holdings.csv` is all condos (Downtown Eastside 7, Downtown 4, West End 2).
- **Keep the 40% cap** per neighbourhood so the money doesn't all go into Downtown and Downtown Eastside.
- **Risk to state on the slide:** many strata buildings ban short-term rentals in their bylaws. We would only buy in buildings that allow them.
- Good candidate for a **Decision Log** entry (what / why / impact).

## Open questions for the team
1. Do we add "condos only" as a Decision Log entry, or keep the current three?
2. Do we have any data on how many strata buildings allow short-term rentals?

---

# For the slides (added 13 Nov)

## A. Allocation options: revenue and price by neighbourhood × bedrooms
Source: `outputs/tables/segments_underwritten.csv` (≥20 comparable listings; threshold now 30, which drops West End 2-bed).

Ranked by **gross yield = revenue ÷ price** (operating costs unknown, so left out).

| Condo | Bedrooms | Listings | Revenue/yr | Price | Gross yield |
|---|---|---|---|---|---|
| Downtown Eastside | 1 | 146 | $49,140 | $525K | **9.4%** |
| Downtown | 1 | 365 | $50,760 | $644K | 7.9% |
| Downtown | 2 | 288 | $63,092 | $872K | 7.2% |
| Downtown | 3+ | 116 | $75,922 | $1.14M | 6.7% |
| Downtown Eastside | 2 | 79 | $43,456 | $710K | 6.1% |
| West End | 2 | 23 | $53,466 | $897K | 6.0% |
| Kitsilano | 1 | 31 | $47,511 | $841K | 5.7% |
| Mount Pleasant | 1 | 51 | $32,483 | $635K | 5.1% |
| West End | 1 | 44 | $30,147 | $663K | 4.5% |

- Smaller condos win: in Downtown, 1-bed 7.9% > 2-bed 7.2% > 3+ 6.7%. Revenue doesn't grow as fast as price.
- Best house option is ~3.0% (3+ bed, Hastings-Sunrise), below every condo option.
- Caveat: gross yield ignores condo strata fees (~$500/month assumed), which houses don't pay.
- Note: the official model (`src/analysis.py`) and sections B–C below still use net yield (after modelled costs).

## B. Geographic risk: cap on the downtown core (Downtown + Downtown Eastside + West End)
Exploratory run, not in the official model yet. "None" matches the official result.

| Core cap | Units | Income/yr | Change |
|---|---|---|---|
| None (current) | 13 | $246,987 | — (96% of money in the core) |
| 70% | 13 | $231,885 | −$15K (−6%); 3 Kitsilano 1-beds come in |
| 50% | 12 | $205,253 | −$42K (−17%); starts buying a house |

- A 70% cap is cheap insurance against a downtown-only slump. It doesn't help with citywide risks (opt-out, new rules).
- **Team decision needed:** adopt 70%? Possible Decision Log entry.

## C. Bedroom pricing assumption (likely judge question)
- Tax data has **no bedroom count or floor area**.
- Condo price = neighbourhood median condo value × multiplier: studio 0.70, 1-bed 0.85, 2-bed 1.15, 3+ 1.50 (`src/config.py:46`). These are a **team judgment**, not from a source.
- Houses get no scaling, so every house in a neighbourhood has the same price.
- Tested ±10% on all multipliers: yield on deployed cash 2.76% / **2.56%** / 2.29% (15 / 13 / 12 units). Direction holds; exact income depends on it.
- To strengthen: check multipliers against a public 1-bed vs 2-bed price source.

## D. Housekeeping
- Fixed 13 Nov: old folder name `analsis/` → `analysis/` in all code and docs.
- **Threshold raised 20 → 30 listings (13 Nov).** New portfolio: 7 Downtown Eastside 1-bed, 4 Downtown 2-bed, 2 Kitsilano 1-bed; $240,594/yr (was $246,987), 2.53% on deployed cash.
- `scripts/prepare_materials.py` still has hardcoded "20" text and overwrites `docs/qa_notes.md`; don't run it until updated. Deck and speaker notes are stale (still say 20 / West End).
