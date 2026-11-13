# Vancouver Airbnb portfolio recommendation

**Prepared:** November 12, 2026  
**Project:** DataJam 2026, Data-Driven Developments (DDD)  
**Budget:** CAD 10 million, all-cash purchases  
**Scope:** Location, property type, and number of units, excluding Airbnb platform fees, management fees, and cleaning/supplies costs as requested.

## Recommendation

For the project simulation, allocate approximately **CAD 9.50 million to 14 condominiums across four neighbourhoods**. Use **12 one-bedroom units and two two-bedroom units**, leaving approximately CAD 499,000 unallocated.

| Neighbourhood | Property type | Units | Comparable listings in segment | Assumed purchase price per unit | Total cash required* |
| --- | --- | ---: | ---: | ---: | ---: |
| Downtown Eastside | One-bedroom condo | **6** | 152 | $539,835 | $3,518,570 |
| Downtown | One-bedroom condo | **5** | 374 | $638,690 | $3,446,188 |
| West End | Two-bedroom condo | **2** | 25 | $864,110 | $1,847,349 |
| Kitsilano | One-bedroom condo | **1** | 33 | $638,690 | $689,238 |
| **Total** | **12 one-bedroom + 2 two-bedroom condos** | **14** | — | — | **$9,501,345** |

*Cash required includes purchase price, assumed acquisition costs of 4%, and furnishing of $25,000 per unit. All amounts are CAD, rounded to the nearest dollar. Comparable listings are observations used to estimate performance, not properties confirmed available for purchase.*

This replaces the earlier eight-unit, downside-focused recommendation **for this revised scope**. The earlier recommendation included operating fees and used a different selection objective. Its figures should not be combined with this scenario.

## Why this allocation

### Downtown Eastside: six one-bedroom condos

This segment has the highest return on deployed cash among candidates with at least 20 comparables under the revised cost assumptions: **6.48% before the three excluded operating costs**. Its assumed purchase price is lower than the corresponding West-side one-bedroom price, while estimated annual revenue is $49,140 per unit.

Six units require approximately $3.52 million. A seventh would take neighbourhood spending to approximately $4.11 million, exceeding the $4 million neighbourhood limit.

The conclusion depends on the model's East/West benchmark pricing. It does not establish that suitable properties can actually be bought in this neighbourhood at that price.

### Downtown: five one-bedroom condos

Downtown one-bedroom condos rank next, at **5.86% before the excluded costs**, with 374 comparable listings and estimated annual revenue of $51,788 per unit. The larger sample makes this estimate less dependent on a handful of observations, although it does not remove estimation bias.

Five units require approximately $3.45 million. A sixth would exceed the neighbourhood limit. The selection method buys these higher-ranked one-bedroom units before considering Downtown two- or three-bedroom units; the remaining neighbourhood allowance cannot accommodate those larger units.

### West End: two two-bedroom condos

Once the two highest-ranked neighbourhood allocations are filled, West End two-bedroom condos are the next affordable eligible segment, at **5.18% before the excluded costs**. Estimated annual revenue is $59,953 per unit.

The segment has 25 comparables. The strict supply constraint allows at most `floor(25 × 10%) = 2` units. These units also add a second bedroom category to the portfolio, but the data does not establish that this reduces demand risk.

### Kitsilano: one one-bedroom condo

Kitsilano one-bedroom condos are the next eligible affordable segment, at **5.05% before the excluded costs**, with 33 comparables and estimated annual revenue of $46,221 per unit.

One unit fits the remaining budget. After this purchase, approximately $498,655 remains, which is insufficient for another eligible unit under the current assumptions. This is unallocated cash, not evidence that the amount is an adequate operating reserve.

## Financial implications of the revised scope

| Metric | Portfolio total |
| --- | ---: |
| Cash deployed, including acquisition and furnishing | $9,501,345 |
| Unallocated budget | $498,655 |
| Sum of segment-median estimated annual revenue × units | $719,907 |
| Annual fixed costs retained in the model | $159,398 |
| **Annual contribution after fixed costs, before excluded costs** | **$560,509** |
| Contribution / deployed cash | **5.90%** |
| Contribution / full $10 million budget | **5.61%** |

**The 5.90% figure is not a fully costed net yield.** It excludes the three operating-cost categories at the user's request. It also excludes income tax, financing, repair reserves, major capital expenditure, and resale gains or losses.

The annual fixed costs retained are:

- Property tax: assumed 0.3% of purchase price.
- Condo strata fees: assumed $500 per month per unit.
- Insurance: assumed $2,000 per unit per year.
- Licence and registration: assumed $1,500 per unit per year.

These are project assumptions, not property-specific quotes. Summing segment medians does not produce a statistically estimated portfolio median or expected value.

## Selection method

The analysis uses the current `outputs/tables/segments_underwritten.csv` and assumptions in `src/config.py`.

1. Start with the project's buyable categories: condos, townhouses, and houses. Standalone suites and other categories are excluded by the existing pricing pipeline.
2. Keep segments with **at least 20 comparable active entire-home listings**. Twenty is a screening assumption, not a statistically validated threshold.
3. Recalculate each segment with Airbnb fees, management fees, and cleaning/supplies costs set to zero **for this scenario only**. The saved `noi` and `net_yield` columns still include the pipeline's costs and are not the ranking values used here.
4. Rank segments by annual contribution after retained fixed costs, divided by total cash required.
5. Buy whole units in descending rank order, subject to:
   - Total cash deployed no greater than **$10 million**.
   - Cash deployed per neighbourhood no greater than **40% of the total budget**.
   - Units per segment no greater than **`floor(comparable listings × 10%)`**.
   - Positive annual contribution under the revised assumptions.
6. Stop when no further candidate can fit the remaining budget and constraints.

```text
Annual fixed costs per unit
  = purchase price × 0.003
    + monthly strata fee × 12
    + annual insurance
    + annual licence/registration

Annual contribution before the three excluded costs
  = segment-median estimated annual revenue − annual fixed costs

Cash required per unit
  = purchase price × 1.04 + 25,000

Ranking metric
  = annual contribution before excluded costs / cash required
```

This is a **yield-first greedy selection**, not a proven globally optimal allocation. A different objective, such as maximizing total annual contribution or protecting against low-revenue outcomes, can produce a different portfolio. The sample-size and supply constraints describe our selection discipline; observed Airbnb supply is not a count of buyable properties.

## Checks and limitations

The contribution and selection were independently recalculated from the current aggregate CSV using the formulas above. The selected holdings satisfy all three budget/supply constraints:

| Neighbourhood | Share of full $10 million budget | Units / segment comparables |
| --- | ---: | ---: |
| Downtown Eastside | 35.19% | 6 / 152 = 3.95% |
| Downtown | 34.46% | 5 / 374 = 1.34% |
| West End | 18.47% | 2 / 25 = 8.00% |
| Kitsilano | 6.89% | 1 / 33 = 3.03% |

The two largest neighbourhood allocations account for approximately **73.3% of deployed cash**, and all units are condos. Four neighbourhoods therefore do not imply broad diversification.

Other material limits:

- **Purchase prices are proxies.** Prices come from October 2026 GVR East/West benchmarks by property type, with assumed bedroom multipliers. Neighbourhood-specific purchase opportunities, condition, building quality, and strata restrictions are not represented.
- **Revenue is estimated.** The project uses Inside Airbnb's estimated revenue for the 12 months preceding June 15, 2026, rather than verified booking receipts. This is a historical-input scenario, not a calibrated 2027 forecast.
- **Current and earlier data differ.** Current configuration uses a minimum-stay filter below 90 nights. The current aggregates contain 374 Downtown one-bedroom comparables and 25 West End two-bedroom comparables; earlier deep-analysis outputs used 364 and 24. Those earlier files are not the source for this report.
- **Feasibility is a project assumption.** `docs/assumptions.md` relaxes the principal-residence requirement for the simulation. This report does not establish that a fund can legally operate the proposed units. Property-level eligibility, strata approval, and applicable rules remain to be checked.
- **The original pipeline is unchanged.** This report applies the revised exclusions and stricter screening separately. Running `run.py` or `scripts/deep_analysis.py` with their existing defaults will not reproduce this scenario without applying these changes.

## Recommended team position

> Under our revised scenario, we recommend 14 condos: six one-bedroom units in Downtown Eastside, five one-bedroom units in Downtown, two two-bedroom units in West End, and one one-bedroom unit in Kitsilano. This deploys approximately CAD 9.50 million. The allocation follows revenue-to-capital efficiency, a minimum comparable count, and neighbourhood and segment limits. Its estimated annual contribution is CAD 560,509 before platform, management, and cleaning/supplies costs, so it should not be presented as a fully costed investment return.

Before presenting, agree whether excluding the three costs is appropriate for the assignment. Before treating the allocation as actionable, validate property-specific acquisition prices and operating eligibility, then restore actual operating costs.

## Sources and provenance

- Current aggregate inputs: [`../outputs/tables/segments_underwritten.csv`](../outputs/tables/segments_underwritten.csv), 121 rows.
- Budget, cost assumptions, and bedroom multipliers: [`../src/config.py`](../src/config.py).
- Existing pricing and selection implementation: [`../src/portfolio.py`](../src/portfolio.py).
- Purchase benchmarks: [`../data/external/gvr_benchmark_2026-10.csv`](../data/external/gvr_benchmark_2026-10.csv), attributed by the project to the [GVR October 2026 statistics package](https://members.gvrealtors.ca/news/GVR-Stats-Package-October-2026.pdf).
- Project scope and simulation assumptions: [`../README.md`](../README.md) and [`assumptions.md`](assumptions.md).
- Source dataset attribution: Inside Airbnb, Vancouver, June 15, 2026, CC BY 4.0, as documented in the project README. This report uses saved aggregates rather than revalidating the raw dataset.

Aggregate input SHA-256 at preparation:

```text
71ed30f3ffc1ba25d6548e500ebacedebd72e1cb0d8a1ebead31e9e9ecd03f20
```

**AI assistance:** Codex helped recalculate the scenario and organize this report. The selection and totals were checked through a separate calculation from the aggregate CSV. The team should review the assumptions and conclusions before submission.
