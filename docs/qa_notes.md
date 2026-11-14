# Q&A notes

The current, checked Q&A and rehearsal guide is [analysis/presentation/preparation_and_qa.md](../analysis/presentation/preparation_and_qa.md). Older unverified statements about equal cost effects and ranking agreement have been removed.

## Added since

**Downtown looks cheap; isn't the ranking just "condos beat houses"?**
Partly, yes. Downtown listings are almost all condos (~$870K) while most other areas are houses ($1.7M–$3.2M), so the mixed ranking favours condo areas. Notebook 02 Step 2b ranks each type separately (≥50 listings of that type). Condos: Downtown Eastside 7.6%, Downtown 7.4%, West End 5.8%, Mount Pleasant 4.6%, Kitsilano 3.6%. Houses: Kensington-Cedar Cottage 2.3%, Hastings-Sunrise 2.1%, Renfrew-Collingwood 2.0%, … Dunbar Southlands 1.0%. Even the best house area yields less than every condo area on the list.

**How do you price condos by bedroom if the tax data has no bedrooms?**
Neighbourhood median condo value × assumed multiplier (studio 0.70, 1-bed 0.85, 2-bed 1.15, 3+ 1.50). Team judgment, not sourced. Moving all multipliers ±10% gives 2.76% / 2.56% / 2.29% yield on deployed cash; the downtown-condo recommendation holds.

**What changed on 13 Nov? (new allocation)**
Ranking metric is now revenue ÷ purchase price (operating costs not given). Condos only, options = neighbourhood × bedrooms with ≥30 listings, max 40% per neighbourhood, near-tied sizes (within 1 point) share money. Result: 15 condos (7 Downtown Eastside 1-bed, 3 Downtown 1-bed, 2 Downtown 2-bed, 3 Kitsilano 1-bed), $9.87M, $765K revenue/yr, 7.75%. Code: `scripts/final_allocation.py` → `outputs/final/`. The older cost-based model in `src/analysis.py` (13 units) is kept but no longer the recommendation.
