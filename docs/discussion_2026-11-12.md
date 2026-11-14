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
