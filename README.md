# DataJam 2026 — The Airbnb Vancouver Problem

**Client:** Data-Driven Developments (DDD), a fictional fund with $10M CAD to deploy in BC short-term rentals.
**Question:** Where, how many, what type/mix, and what should DDD expect in 2027? What are the biggest risks?

> Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0.

## Run it

```bash
pip install -r requirements.txt
bash scripts/download_data.sh   # only if data/raw/ is empty
python run.py                   # -> outputs/tables/*.csv, outputs/key_numbers.json
```

The portfolio step needs `data/external/purchase_prices.csv` (copy the template, fill it from a public source).

## Files

```
run.py             Runs everything, prints the headline numbers
src/config.py      Every assumption (fees, thresholds, budget). Change here, rerun.
src/prep.py        Load, clean, revenue per listing, neighbourhood x type x bedrooms segments
src/portfolio.py   Costs -> yield, $10M greedy portfolio, few-vs-many, sensitivity range
notebooks/         Exploration and charts for the slides
docs/              Decision log + assumptions (both become slides)
```

## Rules
- No host names, listing URLs or real licence numbers in any output or slide.
- Licence-based compliance rates are estimates from free text; label them that way.
- Disclose AI assistance in the pitch (see bottom of `docs/assumptions.md`).
