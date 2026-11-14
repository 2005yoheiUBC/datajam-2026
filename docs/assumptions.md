# Current assumptions

Updated November 13, 2026. Authoritative values are in src/config.py and analsis/current/results.json.

| Assumption | Value / status |
| --- | --- |
| Revenue | Inside Airbnb trailing-year estimates, carried forward unchanged for 2027; not booking receipts |
| Acquisition price | Neighbourhood median assessed value × assumed condo bedroom multiplier; not market-price quotes |
| Condo bedroom factors | Studio .7, 1-bed .85, 2-bed 1.15, 3+ 1.5; tested ±10% |
| Platform | 15.5% scenario; Airbnb help/article/1857, checked November 13, 2026 |
| Management / cleaning | 20% / 8% of revenue, project assumptions |
| Property tax | 0.3% of purchase price, project assumption |
| Condo strata / insurance / licence | 6,000 / 2,000 / 1,500 annually per unit, project assumptions |
| Closing / furniture | 4% of purchase price / 25,000 per unit |
| Financing / income tax / resale | No debt; income tax and resale changes excluded |
| Repairs | Separate 5%-of-revenue reserve scenario; major works excluded |
| Selection constraints | At least 20 segment comparables, floor(10% of supply), 40% of total budget per neighbourhood; team choices |
| Simulation rule | Principal residence requirement explicitly waived by business brief; other permissions remain |
| Missing bedrooms | Impute one; alternative excluding missing tested |
| Dates | Mixed scrape dates; last-review dates after nominal snapshot excluded from active flag; residual date uncertainty remains |

External data: public City of Vancouver property tax and parcel datasets. Source reconstruction hashes are in data/external/property_values_provenance.json. GVR October 2026 is used only as a controlled counterfactual.

AI assistance: code, analytical comparisons and presentation drafting. Important outputs were checked through raw reconstruction, source-join reconstruction, independent arithmetic, budget/capacity tests and slide review.
