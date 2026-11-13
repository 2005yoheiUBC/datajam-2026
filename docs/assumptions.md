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
| Purchase prices | GVR benchmark Oct 2026, by type × Vancouver East/West (`data/external/gvr_benchmark_2026-10.csv`) | Greater Vancouver REALTORS MLS HPI stats package, public PDF | |
| Condo bedroom multiplier | 1-bed 0.85×, 2-bed 1.15×, 3+ 1.5× of benchmark | Benchmark = a typical unit; our assumption | _test ±_ |
| Buyable types | condo, townhouse, house; suites/other excluded | A suite can't be bought without the house | |
| Financing | all cash, no leverage | Keeps return comparable across scenarios | |
| Regulation | Principal residence rule ignored (simulation); licences + provincial registration still required | Brief §1 | 2 months offline case |

## Outside datasets used (brief requires at least one)
- Greater Vancouver REALTORS, MLS Home Price Index, October 2026 (benchmark purchase prices)
- _e.g. CMHC Rental Market Survey — vacancy by zone (for the opt-out / long-term-rental fallback story)_

## AI assistance disclosure (brief requires this in the pitch)

| What AI helped with | How we checked it |
|---|---|
| Pipeline code (Claude) | Read every function; re-derived key numbers by hand in the notebook |
| _add as you go_ | |
