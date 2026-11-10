# Assumptions (keep this on a slide for Q&A)

| Assumption | Value | Source / reasoning | Sensitivity tested |
|---|---|---|---|
| Review rate (reviews per stay) | 50% | Inside Airbnb "San Francisco model" uses 50%; literature 30–70% | 30% / 70% |
| Average length of stay | 3 nights (floored at min nights) | Inside Airbnb model default; check against your data | |
| Occupancy cap | 70% | Prevents implausible estimates for high-review listings | |
| Management fee | 20% of gross | Typical Vancouver STR managers: 15–25% | |
| Platform fee (host side) | 3% | Airbnb split-fee host share | |
| Property tax | ~0.3% of price | City of Vancouver residential mill rate | |
| Strata fees | $500/mo condo | _cite a public source_ | |
| Purchase prices | see data/external/purchase_prices.csv | _public source, no login_ | |
| Financing | all cash, no leverage | Keeps return comparable across scenarios | |
| Regulation | Principal residence rule ignored (simulation); licences + provincial registration still required | Brief §1 | 2 months offline case |

## Outside datasets used (brief requires at least one)
- _e.g. City of Vancouver Open Data, Property Tax Report — assessed values by local area_
- _e.g. CMHC Rental Market Survey — vacancy by zone (for the opt-out / long-term-rental fallback story)_
