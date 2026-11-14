## 1. Recommend 13 condos across three Vancouver areas

TARGET 0:45. We recommend seven one-bedroom condos in Downtown Eastside, four two-bedroom condos in Downtown, and two two-bedroom condos in West End. The plan deploys $9.64m and leaves $362k unallocated. At historical estimated revenue carried forward into a full 2027 operating year, the model produces $247k of operating income, a 2.56% return on deployed cash. This is a scenario, not a forecast guarantee. It includes modelled platform, management and cleaning costs but excludes income tax and major capital repairs. We will explain both the allocation and what could change it.

## 2. Public data, with explicit limits

TARGET 0:45. We use the supplied Inside Airbnb Vancouver file, labelled June 15, 2026, and public Vancouver tax and parcel data. We rebuilt both sources. Of 6,509 listings, 4,447 pass the price and minimum-stay filters, and 3,137 active entire-home observations enter segment analysis. Revenue and occupancy are estimates, not receipts. We found mixed June and July scrape dates and 132 review dates after the nominal snapshot. We exclude those reviews from active status and disclose residual date uncertainty. Purchase prices are neighbourhood assessed-value proxies adjusted by bedroom assumptions. They require validation against actual acquisition opportunities.

## 3. Returns and constraints determine the mix

TARGET 1:30. Our metric divides modelled annual operating income by purchase, closing and furnishing cash. We rank neighbourhood/type/bedroom segments, then buy whole units within the budget. At least 20 comparables are required, no segment can exceed ten percent of its listing sample, and a neighbourhood cannot consume more than forty percent of the full budget. These are team assumptions, not requirements from the brief. Downtown Eastside reaches its regional limit at seven units. Downtown adds four two-bedroom units. West End adds two, its segment supply limit. We tested the threshold and cap instead of asserting they are correct. Without the cap, annual income rises, but almost eighty percent of the budget enters one neighbourhood. This is a feasible greedy allocation, not a mathematical proof of the best possible portfolio.

## 4. Modest properties outperform the high-value alternative

TARGET 1:00. The brief asks us to compare a few expensive properties with many modest ones. We split buyable segments at their median assumed purchase price, then apply the same budget, sample and concentration rules. The modest-property strategy selects 13 units and produces $247k, versus 4 high-value properties and $84k. We compare income against the full ten-million mandate, so unused cash does not artificially improve the result. Unused cash earns zero here. This comparison supports the modest-property choice under our price and cost assumptions. It does not establish a general causal relationship between smaller properties and better returns.

## 5. 2027 income depends on revenue and acquisition prices

TARGET 1:30. Our base assumes a full year of operations at historical estimated revenue. Revenue of $703k less modelled variable costs and fixed costs gives $247k of operating income. We do not claim that historical listing estimates predict 2027. The planning range uses a revenue decrease of twenty percent and an increase of ten percent. Adding a repairs reserve reduces base income to $212k. Combining twenty-percent lower revenue with that reserve leaves $139k. The listing twenty-fifth percentile case is near break-even; it is a cross-sectional stress, not a forecast confidence bound. Acquisition-price shocks reselect the portfolio within the same budget. These cases tell us which assumptions to verify before committing capital, not the probability of success.

## 6. Validation before offers, monitoring after launch

TARGET 1:00. The largest practical uncertainty is whether assessed values represent properties we can actually buy. Before offers, obtain property-level prices, condition reports and strata approvals, then rerun the allocation. Validate costs with operators and size the repairs and working-capital reserve. Confirm licensing and registration under the simulation rules: the brief explicitly waives principal residence, but other rules remain. After launch, compare monthly booked revenue and costs with the plan and investigate persistent variance. Our data-date and active-listing assumptions remain limitations. AI assisted code, analysis and slide drafting. We checked important outputs by rebuilding public source data, independent arithmetic and selection constraints. Our recommendation is a shortlist to validate, not a claim that these specific units are already available.

## 7. Three decisions with measured consequences

APPENDIX. Each decision records what, why and its measured effect. Pricing counterfactual holds the matched segment universe fixed. Minimum sample tests hold costs and caps fixed. Cap tests hold pricing, costs and minimum sample fixed. Sources: current/pricing_method_comparison.csv, sample_size_sensitivity.csv, concentration_sensitivity.csv.

## 8. One-unit calculation: Downtown Eastside

APPENDIX. One-bedroom purchase proxy is $524,875. Closing costs are four percent, plus furnishing of twenty-five thousand. Total setup cash is $570,870. Revenue is the segment median $49,140, not verified receipts. Platform, management and cleaning assumptions total forty-three point five percent. Fixed costs include property tax, strata, insurance and licensing. All numbers are calculated before displayed rounding. Seven units cost $3,996,090; an eighth would exceed four million.

## 9. Sensitivity to prices, samples and concentration

APPENDIX. All rows reselect units under the stated changed assumption; all other assumptions are held fixed. Price shocks include both closing costs and property tax. Condo bedroom multipliers also have a separate ±10 percent sensitivity in current/bedroom_multiplier_sensitivity.csv. Do not confuse reselection cases with fixed-holdings revenue stresses.

## 10. Fee-excluded allocation and investment recommendation

APPENDIX. The requested allocation study deliberately excludes platform, management and cleaning costs in selection. It selects fourteen condos. Evaluated with costs restored it produces $239,093. Cost-aware selection changes Downtown's bedroom mix and produces $246,987, using $250,985 more capital. Neither is a global optimum. The extra capital has opportunity cost; we show the trade-off rather than claiming strict dominance. Earlier November 12 figures used older inputs and are archived.

## 11. Data-quality checks and remaining limits

APPENDIX. Source labelled June 15 contains June 15, June 16 and July 6 scrape dates. Excluding later review dates removes known look-ahead in the active flag, but later prices and trailing estimates remain possible. The comparison rows rebuild affected segment populations and reselect. Missing bedrooms are imputed to one in base; excluding them is a sensitivity. Including inactive listings reduces modelled income. Assessment joins use parcel centroids and residential proxies, not validated sale opportunities. We have not done out-of-time forecast validation. Public raw source hashes and assessment reconstruction metadata are recorded.
