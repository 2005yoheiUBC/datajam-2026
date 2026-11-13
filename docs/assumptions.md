# Assumptions (keep this on a slide for Q&A)

| Assumption | Value | Source / reasoning | Sensitivity tested |
|---|---|---|---|
| Occupancy & revenue | Inside Airbnb `estimated_occupancy_l365d` / `estimated_revenue_l365d` | Their estimate from reviews, 12 months to 15 Jun 2026; not reported figures | |
| Management fee | 20% of gross | Typical Vancouver STR managers: 15–25% | |
| Platform fee (host side) | 3% | Airbnb split-fee host share | |
| Property tax | ~0.3% of price | City of Vancouver residential mill rate | |
| Strata fees | $500/mo condo | _cite a public source_ | |
| Purchase prices | Median 2026 assessed value per neighbourhood × condo/house (`data/external/property_values_2026.csv`) | City of Vancouver Open Data property tax report (BC Assessment); assessed ≈ market value mid-2025 | |
| Condo bedroom multiplier | 1-bed 0.85×, 2-bed 1.15×, 3+ 1.5× of benchmark | Benchmark = a typical unit; our assumption | _test ±_ |
| Buyable types | condo, townhouse, house; suites/other excluded | A suite can't be bought without the house | |
| Financing | all cash, no leverage | Keeps return comparable across scenarios | |
| Regulation | Principal residence rule ignored (simulation); licences + provincial registration still required | Brief §1 | 2 months offline case |

## Outside datasets used (brief requires at least one)
- City of Vancouver Open Data: property tax report 2026 + property parcel polygons (purchase prices per neighbourhood)
- _e.g. CMHC Rental Market Survey — vacancy by zone (for the opt-out / long-term-rental fallback story)_

## AI assistance disclosure (brief requires this in the pitch)

| What AI helped with | How we checked it |
|---|---|
| Pipeline code (Claude) | Read every function; re-derived key numbers by hand in the notebook |
| _add as you go_ | |
