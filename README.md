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

The portfolio step uses `data/external/gvr_benchmark_2026-10.csv` and the bedroom multipliers in `src/config.py`.

To audit the saved aggregates and run deeper scenarios without downloading raw data or installing packages:

```bash
python3 scripts/deep_analysis.py
python3 -m unittest discover -s scripts -p 'test_deep_analysis.py'
```

Start with [analsis/README.md](analsis/README.md) for the organized recommendations, calculation explanations, and earlier visuals. The current English recommendation excludes platform, management, and cleaning/supplies costs. Earlier fee-inclusive reports and tables are preserved under `analsis/archive/fee_inclusive_analysis/`; they use an earlier aggregate snapshot. Future deep-analysis runs write their Japanese report and scenario tables to `analsis/deep_analysis/`. Selection uses a yield-first heuristic, not a proven global optimum. See each report for its assumptions and audit findings.

## Files

```
run.py             Runs everything, prints the headline numbers
src/config.py      Every assumption (fees, thresholds, budget). Change here, rerun.
src/prep.py        Load, clean, revenue per listing, neighbourhood x type x bedrooms segments
src/portfolio.py   Costs -> yield, $10M greedy portfolio, few-vs-many, sensitivity range
notebooks/         Exploration and charts for the slides
docs/              Decision log + assumptions (both become slides)
analsis/           Current recommendation, calculation explanations, and archived scenarios
```

## Rules
- No host names, listing URLs or real licence numbers in any output or slide.
- Licence-based compliance rates are estimates from free text; label them that way.
- Disclose AI assistance in the pitch (see bottom of `docs/assumptions.md`).
