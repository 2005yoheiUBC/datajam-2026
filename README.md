# DataJam 2026: Vancouver short-term rental investment

DDD has CAD 10 million to invest, with properties operational throughout 2027. The business brief explicitly waives principal-residence requirements for this simulation; other operating rules remain relevant.

**Current investment-committee recommendation:** 13 condos across Downtown Eastside, Downtown, and West End. Deploy about CAD 9.64 million for modelled annual operating income of CAD 247,000 (2.56% of deployed cash), before income tax and major capital repairs. These are historical-revenue run-rate assumptions, not a calibrated forecast.

The requested **fee-excluded allocation study** is retained separately: 14 condos. Its before-cost ratio must not be presented as a fully costed return. Every current number is generated from the same inputs by `src/analysis.py`.

## Reproduce the presentation numbers: no dependencies or downloads

From a fresh checkout with Python 3.10+:

```bash
python3 run.py
python3 scripts/prepare_materials.py
python3 -m unittest discover -s scripts -p 'test_deep_analysis.py'
```

This route rebuilds pricing and selection from committed, privacy-safe `outputs/tables/segments.csv` and `data/external/property_values_2026.csv`. It writes current results and scenario CSVs to `analysis/current/`, updates the public headline tables under `outputs/`, and regenerates reports, assumptions, decision log and rehearsal guide. The optional pandas-only raw-date test is skipped without pandas; financial and capacity tests still run.

## Rebuild from public raw sources

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
bash scripts/download_data.sh
python scripts/build_property_values.py
python run.py --source raw
python scripts/prepare_materials.py
python -m unittest discover -s scripts -p 'test_deep_analysis.py'
```

`download_data.sh` downloads detailed listings and neighbourhood geometry by default. Use `bash scripts/download_data.sh --all` for reviews and calendars needed by exploratory notebooks. Network access is required. Raw files and locally cleaned listing-level data are ignored by Git. The raw route and assessed-value rebuild were executed successfully on November 13, 2026. Source hashes and join counts are recorded in `analysis/current/raw_validation.json` and `data/external/property_values_provenance.json`.

The frozen environment is in `requirements-lock.txt` and was tested with Python 3.13 on macOS; `requirements.txt` lists top-level exploration dependencies. Assessment rebuilding uses curl with certificate verification and public City API exports. It never scrapes Airbnb pages.

## Presentation and team materials

- [Current English report](analysis/recommendation_en.md)
- [Japanese calculation explanation](analysis/reasoning_ja.md)
- [Editable PPTX](analysis/presentation/ddd_investment_pitch.pptx): six main slides plus five appendix slides
- [Speaker notes](analysis/presentation/speaker_notes.md)
- [Rehearsal and Q&A guide](analysis/presentation/preparation_and_qa.md)
- [Measured decision log](docs/decision_log.md)
- [Current assumptions](docs/assumptions.md)
- [Exact current results](analysis/current/results.json)

The PPTX is committed as a deliverable. Its source is `analysis/presentation/build_deck.mjs`, authored using `@oai/artifact-tool`. Rebuilding requires the presentation runtime described in [the presentation README](analysis/presentation/README.md); the Python numerical workflow does not require that runtime. Changes to numerical inputs require rebuilding the deck after regenerating results and reports.

## Important interpretation limits

- Revenue and occupancy are Inside Airbnb estimates, not booking receipts.
- The file labelled June 15 includes mixed June/July scrape dates. Known later review dates are excluded from active status; residual time uncertainty is disclosed.
- Acquisition prices are neighbourhood median assessed-value proxies adjusted by assumed bedroom factors. They are not confirmed transaction prices or available opportunities.
- The minimum 20 comparables, 40% neighbourhood cap, and 10% listing-supply limit are team choices, not brief requirements. Selection is greedy, not a proven global optimum.
- Operating income includes modelled platform 15.5%, management 20%, cleaning/supplies 8%, plus fixed costs. Repairs reserves are separate cases. Income tax, major capital works, debt and resale changes are excluded.
- Planning scenarios and listing p25/p75 comparisons have no calibrated probabilities.
- Earlier reports and visuals are in `analysis/archive/`. They are historical comparisons and do not contain the current recommendation. Exploratory notebooks can contain older narrative text; current reports and results take precedence.

## Files and traceability

```text
run.py                         Aggregate or raw rebuild entry point
src/analysis.py                Pricing, selection, costs, scenarios and output generation
src/prep.py                    Raw listing cleaning and segmentation
src/portfolio.py               Pandas equivalents for exploratory use
src/config.py                  Model assumptions
scripts/build_property_values.py   Rebuild the public assessment/parcel join
scripts/prepare_materials.py    Generate reports and presentation preparation materials
scripts/test_deep_analysis.py   Independent financial and selection checks
analysis/current/                Exact current results, scenarios and provenance
analysis/presentation/           Slides, speaker notes and rehearsal guide
analysis/archive/                Superseded analysis snapshots
```

Data: Inside Airbnb, Vancouver, 15 June 2026, CC BY 4.0.

Do not show host names, listing URLs or real licence numbers. Licence-text indicators are estimates, not verified compliance. Disclose material AI assistance and how important outputs were checked, as required by the business brief.
