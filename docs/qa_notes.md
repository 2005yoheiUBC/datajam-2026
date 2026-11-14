# Q&A notes: filtering and merging

For the pptx appendix and for answering judges. Every number comes from `python run.py` / the notebooks.

## Funnel: from raw data to the shortlist

| Step | Listings left | Removed | Why |
|---|---|---|---|
| Raw Inside Airbnb snapshot (15 Jun 2026) | 6,509 | | |
| Has a price | 5,845 | 664 | No price = not bookable on scrape day |
| Price $30–$2,000/night | 5,446 | 399 | Outside = placeholder or error |
| Minimum stay under 90 nights | **4,447** | 999 | BC STRAA + Vancouver bylaw (since 2024): short-term = under 90 consecutive days |
| Whole places only | 3,757 | 690 | DDD buys whole properties; private/shared rooms aren't comparable |
| Active (reviewed in last 12 months) | **3,219** (23 neighbourhoods) | 538 | Drops dead listings that would drag typical numbers down |
| Merge purchase prices | **2,557** (22 neighbourhoods) | 662 | 636 suites + 13 "other" can't be bought on their own; Strathcona (13) has no homes in the tax data |
| At least 50 listings per neighbourhood | 14 neighbourhoods | 8 neighbourhoods | Fewer than 50 = typical numbers too unreliable |
| Rank by gross yield | **Top 5** | | Downtown, Downtown Eastside, West End, Mount Pleasant, Kensington-Cedar Cottage |

## Likely questions

**Why under 90 nights, not 30?**
BC's Short-Term Rental Accommodations Act and Vancouver's bylaw (updated 2024) both define short-term as under 90 consecutive days. We first used the old 30-day rule; switching added back 46 listings (all exactly 30-night minimums) and moved portfolio yield 4.0% → 3.9%.

**Where does occupancy / revenue come from?**
Inside Airbnb's own estimates (`estimated_occupancy_l365d`, `estimated_revenue_l365d`), 12 months to 15 June 2026. They're estimates from reviews, not real bookings. Revenue = nights booked × nightly price. We first built our own review model, but it gave identical numbers (rank agreement 1.0), so we used theirs.

**Where do purchase prices come from?**
City of Vancouver Open Data, property tax report 2026 (BC Assessment values) + property parcel map. We placed ~229,000 properties into the Inside Airbnb neighbourhoods and took the median value per neighbourhood × condo/house (~192,000 homes). Script: `scripts/build_property_values.py`. We first used a 2-region benchmark (GVR, East/West); the per-neighbourhood values kept the same top 5.

**Assessed value isn't market value.**
True: assessed ≈ market value as of mid-2025. Used consistently for every neighbourhood, so the ranking is fair.

**Why exclude suites?**
A guest suite or laneway home can't be bought separately; you'd have to buy the whole house.

**Why did Strathcona drop out? It had the highest revenue.**
Only 14 listings (unreliable), and in the Inside Airbnb map it's an industrial/commercial area with no homes in the tax data, so there's no purchase price.

**Why rank by gross yield (revenue ÷ price), ignoring operating costs?**
Most costs are a % of revenue or the same everywhere, so they shrink every neighbourhood equally. Tested: same top 5, rank agreement 0.99. Costs come back for the final 2027 profit number.

**Downtown looks cheap; isn't the ranking just "condos beat houses"?**
Partly, yes. Downtown listings are almost all condos (~$870K) while most other areas are houses ($1.7M–$3.2M), so the mixed ranking favours condo areas. Notebook 02 Step 2b ranks each type separately (≥50 listings of that type). Condos: Downtown Eastside 7.6%, Downtown 7.4%, West End 5.8%, Mount Pleasant 4.6%, Kitsilano 3.6%. Houses: Kensington-Cedar Cottage 2.3%, Hastings-Sunrise 2.1%, Renfrew-Collingwood 2.0%, … Dunbar Southlands 1.0%. Even the best house area yields less than every condo area on the list.

**Why not revenue − price?**
Revenue is yearly, price is paid once; subtracting them is meaningless. A ratio (or payback years = price ÷ revenue) is the right comparison.

**Condo prices don't know bedrooms.**
Correct. Tax data has no bedroom count, so condos are scaled from the neighbourhood median: 1-bed 0.85×, 2-bed 1.15×, 3+ 1.5×. That's our assumption (in `src/config.py`).

**What are the concentration caps?**
Our risk rules, not from the brief: max 40% of the $10M per neighbourhood, max 10% of a segment's existing listings, at least 5 comparable listings. They spread risk across neighbourhoods.
