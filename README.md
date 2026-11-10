# DataJam 2026 — The Airbnb Vancouver Problem

**Client:** Data-Driven Developments (DDD), a fictional fund with $10M CAD to deploy in BC short-term rentals.
**Question:** Where, how many, what type/mix, and what should DDD expect in 2027? And what are the biggest risks?

> Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0.

## Reproduce every number

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/download_data.sh        # Inside Airbnb snapshot -> data/raw/
make all                             # clean -> features -> analysis -> outputs/
```

Every figure in the pitch comes from `outputs/key_numbers.json` or a table in `outputs/tables/`.
Each key in `key_numbers.json` names the function that produced it (see `src/analysis.py`).

## Layout

```
data/raw/          Inside Airbnb files (not committed)
data/external/     Outside public data we joined in (CMHC, Vancouver Open Data, ...)
data/processed/    Cleaned parquet files written by src/clean.py
src/
  config.py        Paths, the snapshot date and every tunable assumption in one place
  load.py          Raw readers with explicit dtypes and date parsing
  clean.py         Price parsing, filters and data-quality report
  features.py      Calendar-based occupancy, revenue, licence status, per-neighbourhood metrics
  analysis.py      Portfolio scenarios ($10M allocation), return metric, sensitivity range
  pipeline.py      Runs it all end to end
notebooks/         Exploration only; nothing in the pitch should come only from a notebook
docs/
  decision_log.md  The 3+ decisions (9 of 30 points). Fill this in as you go.
  data_quality.md  Auto-written by clean.py
  assumptions.md   Every assumption with source and sensitivity
tests/             Sanity checks on parsing and the money maths
```

## Rules we follow
- No host names, listing URLs or real licence numbers in any output or slide.
- Licence-based compliance rates are estimates from imperfect data; we label them that way.
- AI assistance is disclosed in the pitch (see `docs/ai_disclosure.md`).
