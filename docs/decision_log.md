# Decision log

Three presentation decisions, with controlled comparisons. All returns below restore modelled operating costs.

| Decision | What | Why | What changed | Evidence |
| --- | --- | --- | --- | --- |
| Pricing | Use neighbourhood assessed values instead of two-region GVR benchmarks. | More local price variation; both are acquisition proxies. Same matched listing universe in both cases. | GVR: 14 units, 2.51%; assessments: 13 units, 2.53%. | pricing_method_comparison.csv |
| Sample size | Require at least 30 comparables per segment (raised from 20 on 13 Nov). | Resampling Downtown 1-bed condos: a median from 20 listings is typically ±17% off, from 30 ±14%. Tested 5/10/20/30. | At 20: 13 units, $246,987. At 30: 13 units, $240,594 (West End 2-bed, 23 listings, drops; Kitsilano 1-bed comes in). | sample_size_sensitivity.csv |
| Concentration | Limit one neighbourhood to 40% of the full budget. | Accept a measured income cost to limit a single-neighbourhood exposure. Shared citywide and condo risks remain. | No cap: 16 units, $280,714, largest exposure 79.92% of budget. At 40%: 13 units, $240,594, 39.96% largest exposure. | concentration_sensitivity.csv |

Sources: [current results](../analysis/current/results.json). The 40% cap and minimum 30 comparables are team choices, not brief requirements.
