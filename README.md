# Where DDD should put $10M — Douglas Gang · DataJam 2026

**Recommendation:** buy 15 condos in Downtown Eastside, Downtown and Kitsilano for $9.87M, earning about $765K of revenue in 2027 (about 7.7% of the purchase price).

| Neighbourhood | Units | Price each | Revenue each / yr |
|---|---|---|---|
| Downtown Eastside | 7 × 1-bed | $524,875 | $49,140 |
| Downtown | 3 × 1-bed + 2 × 2-bed | $644,470 / $871,930 | $50,760 / $63,092 |
| Kitsilano | 3 × 1-bed | $840,565 | $47,511 |

- **Pitch:** [`presentation/douglas_gang_pitch.pptx`](presentation/douglas_gang_pitch.pptx)
- **Walkthrough:** [`notebooks/analysis.ipynb`](notebooks/analysis.ipynb)

## Method in one paragraph
An *option* is a neighbourhood × property type × bedroom count. For each option we take the median revenue of its active, short-term, whole-home listings and divide it by the median 2026 assessed value (condos scaled by bedrooms). We keep condos only, trust only options with 30+ listings, rank by revenue ÷ price, and buy from the top with at most 40% of the budget in one neighbourhood. Operating costs are not given in the brief, so they are left out.

## Key decisions
1. **Condos only.** Houses earn similar revenue but cost 2–3× more (best house 3.0% vs every trusted condo option 4.5%+).
2. **30+ listings per option.** A median from 20 listings is typically ±17% off, from 30 ±14% (resampling test).
3. **Rank by revenue ÷ price.** Our earlier cost-based ranking bought 13 units / $691K; this one buys 15 units / $765K.

## Reproduce
```bash
pip install -r requirements.txt
bash scripts/download_data.sh            # Inside Airbnb listings + neighbourhoods -> data/raw/
python scripts/build_property_values.py  # optional: rebuilds data/external/ from City of Vancouver Open Data
python run.py                            # -> outputs/ (every number in the deck)
python presentation/make_charts.py       # -> presentation/charts/
npm install pptxgenjs && node presentation/build_deck.js   # -> presentation/douglas_gang_pitch.pptx
```

| Path | What |
|---|---|
| `src/config.py` | Every threshold and assumption |
| `src/prep.py` | Cleaning and per-listing revenue |
| `src/final.py` | Options, ranking, allocation, checks |
| `outputs/` | `allocation.csv`, `options.csv`, `summary.json` and the check tables |

## Data
- Inside Airbnb, Vancouver, 15 June 2026 snapshot (scraped 15 June–6 July 2026), CC BY 4.0.
- City of Vancouver Open Data: property tax report 2026 and property parcel polygons (purchase prices).

Revenue and bookings are Inside Airbnb estimates, not reported figures. No host names, listing URLs or licence numbers are stored or shown.

**AI use:** we used Claude to help write code, run analysis and draft slides, and checked it by re-running every number from this repo, hand-checking the allocation and testing key choices against alternatives.
