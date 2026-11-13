# Decision log (9 of 30 points)

Each decision scores 3 points: **what** (1), **why, with evidence or alternatives compared** (1),
**what it changed in the result** (1). Log decisions as you make them; pick the best 3 for the appendix.

| # | Decision | Why (evidence / alternatives compared) | What changed as a result | Where in code |
|---|---|---|---|---|
| 1 | Return metric = year-1 net cash yield on cash deployed (all-cash) | vs. gross revenue (ignores price), vs. cap rate (ignores furnishing/closing), vs. levered IRR (needs a financing assumption we can't defend) | _e.g. ranking flipped: Downtown tops gross revenue but X tops yield_ | `portfolio.py` |
| 2 | Drop listings with minimum stay ≥ 30 nights | BC defines STR as < 30 nights; these are monthly rentals. _N removed_ | _median revenue moved from A to B_ | `prep.py` |
| 3 | Use Inside Airbnb's occupancy/revenue estimate instead of our own review model | Our model gave the same numbers (Spearman ρ = 1.0), so it added nothing; calendar can't tell booked from blocked (6.4% of listings blocked all year) | Same results, simpler and citable | `prep.py` |
| 4 | Stay in City of Vancouver vs. Kelowna / elsewhere | _Kelowna opt-out covers tourism zones only; need outside data_ | | |
| 5 | Concentration cap (≤40% per neighbourhood, ≤10% of a segment's supply) | _regulatory/ local saturation risk_ | _portfolio spread across N neighbourhoods; yield fell by Y bp_ | `portfolio.build_portfolio` |
| 6 | Price outliers: drop < $30 and > $2,000/night | _show the histogram and a few examples (no URLs)_ | | `config.py` |

**Phrase to use in the pitch:** "We tested that, and it didn't hold." Judges reward this.
