# Presentation recommendation and analysis

Updated November 13, 2026. CAD throughout. **This report supersedes the November 12 allocation.**

## Decision

For the investment-committee pitch, recommend **13 condos in 3 Vancouver neighbourhoods**, deploying **$9,638,208** and leaving **$361,792** unallocated. Modelled 2027 operating income is **$246,987**, equivalent to **2.56% on deployed cash**, or **2.47% on the full mandate**. This is a historical-revenue run-rate scenario, not a calibrated 2027 forecast or guaranteed return.

| Neighbourhood | Condo bedrooms | Units | Comparables | Cash deployed | Modelled annual income |
| --- | --- | --- | --- | --- | --- |
| Downtown Eastside | 1 | 7 | 146 | $3,996,090 | $116,826 |
| Downtown | 2 | 4 | 288 | $3,727,229 | $94,124 |
| West End | 2 | 2 | 23 | $1,914,889 | $36,037 |

All units are condos. The two largest neighbourhood allocations represent 80.13% of deployed cash. Geographical limits do not diversify citywide rules or property-type risk. Unallocated cash is a buffer to size explicitly, not a demonstrated adequate reserve.

## Preserve the requested fee-excluded allocation study

The user requested ignoring platform, management, and cleaning/supplies costs when selecting locations. That analysis is retained in [current/fee_excluded_holdings.csv](current/fee_excluded_holdings.csv): **14 units**, with 7 one-bedroom units in Downtown Eastside, 5 one-bedroom units in Downtown, and 2 two-bedroom units in West End. It deploys $9,387,223.

Evaluating those same holdings with modelled operating costs gives $239,093 income and 2.55% return. Cost-aware selection instead uses four two-bedroom units in Downtown, producing $7,894 more annual modelled income while committing $250,985 more capital. The final pitch uses this cost-aware alternative because its mandate is investment value. The requested allocation study remains a separately labelled comparison.

## Calculation and meaning of the return

```text
Total cash = purchase price × 1.04 + furnishing of 25,000 per unit
Operating income = estimated annual revenue × (1 − 15.5% − 20% − 8%) − fixed costs
Fixed costs = purchase price × 0.3% + strata + insurance + licence/registration
Return on deployed cash = operating income / total cash
```

Strata is 500/month for condos, insurance 2,000/year, and licence/registration 1,500/year per unit. These, management at 20%, cleaning/supplies at 8%, closing at 4%, and furnishing at 25,000 are modelling assumptions, not property quotes. Platform 15.5% is a single-fee scenario supported by [Airbnb's official explanation](https://www.airbnb.com/help/article/1857), checked November 13, 2026. The historical revenue input is held fixed when changing fees; repricing and guest-demand responses are not estimated.

| Annual bridge | CAD |
| --- | ---: |
| Sum of selected segment-median revenues | $703,278 |
| Modelled variable operating costs, 43.5% | ($305,926) |
| Modelled fixed operating costs | ($150,365) |
| Operating income before income tax/capital repairs | $246,987 |
| After an additional assumed 5% of revenue for repairs reserve | $211,823 |

No debt, income tax, resale gain/loss, or major capital expenditure is included. A repairs reserve is shown separately. The return is not IRR. Summed segment medians are neither an estimated portfolio expectation nor its statistical median.

## Selection and alternatives

Active entire-home listings are grouped by neighbourhood, property bucket, and bedrooms. Eligible segments have at least 20 listing comparables. Rank by modelled operating income / purchase-plus-setup cash, then buy integer units while respecting the 10 million budget, 40% of budget per neighbourhood, and floor(10% of segment comparables) capacity. Skip nonpositive operating income. This is yield-first greedy selection, not proven global optimisation or an exhaustive maximisation of annual income. The limits and minimum sample are team assumptions, not brief requirements.

The price split for few-high-value versus many-modest uses the median price across eligible buyable **segments** ($1,791,000), not a transaction-weighted market median. Under identical selection rules:

| Alternative | Units | Cash deployed | Annual operating income | Return on full budget |
| --- | --- | --- | --- | --- |
| modelled_cost_base | 13 | $9,638,208 | $246,987 | 2.47% |
| few_high_value | 4 | $8,893,668 | $83,517 | 0.84% |
| many_modest | 13 | $9,638,208 | $246,987 | 2.47% |

Uninvested cash earns zero in this comparison. Property-count-specific overhead has not been estimated. The low-cost portfolio is more efficient under the model; this is not a causal statement about smaller properties generally.

## 2027 scenarios and validation

Properties are assumed operational January 1, 2027 for a full year. Base revenue equals historical estimated revenue, with no assumed trend or World Cup uplift. Revenue −20% / +10% gives a conditional operating-income range of $167,517 to $286,722. This is a chosen planning range, not a prediction interval. Two months offline assumes uniformly distributed revenue; seasonal closure could be worse.

| Case, same selected holdings | Annual operating income | Return on deployed cash |
| --- | --- | --- |
| modelled_cost_base | $246,987 | 2.56% |
| revenue_plus10 | $286,722 | 2.97% |
| revenue_minus10 | $207,252 | 2.15% |
| revenue_minus20 | $167,517 | 1.74% |
| revenue_minus30 | $127,781 | 1.33% |
| two_months_offline | $180,762 | 1.88% |
| revenue_minus20_reserve5 | $139,386 | 1.45% |
| repairs_reserve5 | $211,823 | 2.20% |
| platform_fee3 | $334,897 | 3.47% |
| cross_section_p25 | $-560 | -0.01% |
| cross_section_p75 | $462,116 | 4.79% |

p25/p75 are cross-sectional differences between listings, simultaneously applied to holdings; they are not future confidence bounds. The p25 case is near break-even, so the portfolio is not robust to every stress. Revenue −20% plus an extra 5% repairs reserve gives $139,386. Revenue shocks keep holdings fixed. Purchase-price shocks reselect within budget; +20% purchase prices gives 11 units and 1.95%. Condo bedroom-price multipliers are also tested ±10%.

Raw listings were downloaded from the public Inside Airbnb snapshot URL and rebuilt: 6,509 listings, 4,447 after price/stay filters, 3,137 active entire-home listings, 186 segments. There are 132 review dates after the nominal snapshot date; these are excluded from active status. The file's scrape dates are mixed: {"2026-06-16": 3058, "2026-07-06": 2156, "2026-06-15": 1295}. Later scrape observations can still influence prices and trailing estimates, so this is not a reconstructed clean June 15 information set.

External property prices were rebuilt from public tax and parcel data: 229,095 matched rows and 191,840 selected residential-proxy rows. Tax coordinate joins, parcel centroids, zoning, legal type and value bounds are proxies, not verified acquisition opportunities. Polygon holes are respected. Assessment values are not transaction prices. Townhouses use strata/condo assessment proxies; they are not selected in this recommendation. See [property-value provenance](../data/external/property_values_provenance.json).

Missing bedrooms remain imputed to one in the base pipeline, but excluding them is tested. Including inactive listings reduces the selected strategy's modelled income; active-only selection may be optimistic. Outlier filters and the 30-versus-90-night threshold are tested, with all results in [current/raw_filter_sensitivity.csv](current/raw_filter_sensitivity.csv). A listing's minimum stay classifies its advertised policy, not every realised booking.

## Three decisions to defend

| Decision | What | Why | Measured effect | Evidence |
| --- | --- | --- | --- | --- |
| Pricing | Use neighbourhood assessed values instead of two-region GVR benchmarks. | More local price variation; both are acquisition proxies. Same matched listing universe in both cases. | GVR: 14 units, 2.51%; assessments: 13 units, 2.56%. | pricing_method_comparison.csv |
| Sample size | Require at least 20 comparables per segment. | Avoid choosing segments supported by only a handful of listings; test 5/10/20/30, not a claim of statistical sufficiency. | At 5: 12 units and $243,111 income. At 20: 13 units and $246,987. | sample_size_sensitivity.csv |
| Concentration | Limit one neighbourhood to 40% of the full budget. | Accept a measured income cost to limit a single-neighbourhood exposure. Shared citywide and condo risks remain. | No cap: 16 units, $280,714, largest exposure 79.92% of budget. At 40%: 13 units, $246,987, 39.96% largest exposure. | concentration_sensitivity.csv |

## Risks and actions

1. Acquisition-price proxy: obtain property-level price, condition and strata checks, and rerun +10%/+20% cases before offers.
2. Demand and estimated revenue: track actual booked revenue and costs against these assumptions monthly; investigate a sustained shortfall rather than treating reviews as bookings.
3. Concentration: keep the explicit cap and report the income sacrificed; recognise common condo/city shocks remain.
4. Data dates and sample selection: disclose mixed scrape dates, exclude known post-snapshot reviews, and use an earlier independent snapshot for a future out-of-time validation. That validation is not yet performed.
5. Operational permissions: the brief explicitly waives principal-residence requirements for the simulation. Licences, registration, safety and strata approvals still need checking. Do not pitch a solution to the waived restriction.

## Reproduction and traceability

From the repository root, `python3 run.py` recreates current numbers using committed, privacy-safe aggregates and the standard library. For the raw route, create a virtual environment, install requirements, run `bash scripts/download_data.sh`, optionally rebuild assessed prices using `python scripts/build_property_values.py`, then run `python run.py --source raw`. Both routes were checked. To refresh this report and the presentation content, run `python3 scripts/prepare_materials.py` after the analysis.

Source of truth: [current/results.json](current/results.json). Exact holdings, each experiment, and raw-source hashes are adjacent. Calculation code: [src/analysis.py](../src/analysis.py). Tests: [scripts/test_deep_analysis.py](../scripts/test_deep_analysis.py). Sources: Inside Airbnb (snapshot labelled June 15, 2026, CC BY 4.0), City of Vancouver property tax and parcel datasets, GVR October 2026 for the controlled pricing counterfactual, and the local business-case PDF.

AI assistance: code, analysis and presentation drafting. Checked by public raw-data reconstruction, assessed-value reconstruction, independent arithmetic, capacity/budget tests, and slide-data reconciliation. The team must understand and defend assumptions. No individual hosts or licence identifiers appear in these outputs.
