# Analysis and recommendations

This folder collects the recommendations, calculation explanations, and earlier analysis prepared during the project discussion. The folder name `analsis` follows the requested spelling.

## Start here

1. **[Current recommendation in English](recommendation_en.md):** the team-facing report. Recommends 14 condos across four neighbourhoods, excluding Airbnb fees, management fees, and cleaning/supplies costs. Includes allocation, reasoning, assumptions, and sources.
2. **[Calculation explanations in Japanese](reasoning_ja.md):** explains how prices, annual contribution, ranking, and unit counts were calculated. Also defines “comparables” and identifies the source of the 40% neighbourhood cap.

## Earlier analysis and visuals

The [archive](archive/fee_inclusive_analysis/) contains the earlier fee-inclusive scenario and its source snapshot. **Its eight-unit recommendation is not the current 14-unit recommendation.** Its revenue inputs also predate the updated minimum-stay filter.

| Material | File | How to use it |
| --- | --- | --- |
| Earlier Japanese report | [report_ja.md](archive/fee_inclusive_analysis/report_ja.md) | Historical analysis of fees, sample sizes, concentration, and downside cases |
| Browser-ready comparison | [portfolio-recommendation-browser.html](archive/fee_inclusive_analysis/portfolio-recommendation-browser.html) | Open in Chrome or Safari; shows the earlier eight-unit recommendation |
| Inline visual source | [portfolio-recommendation.html](archive/fee_inclusive_analysis/portfolio-recommendation.html) | Editable source for the earlier visual; use the browser-ready version to view it |
| Scenario comparison tables | [portfolio_comparison.csv](archive/fee_inclusive_analysis/portfolio_comparison.csv) | Earlier holdings evaluated under different fee and revenue cases |
| Selected holdings | [portfolio_holdings.csv](archive/fee_inclusive_analysis/portfolio_holdings.csv) | Holdings for those earlier scenarios |
| Audit and provenance | [audit.csv](archive/fee_inclusive_analysis/audit.csv), [manifest.json](archive/fee_inclusive_analysis/manifest.json) | Checks and input hashes recorded for that snapshot |

Other archived CSVs contain fixed-holdings stress tests, price/revenue combinations, sample-size and concentration-cap tests, and segment diagnostics. Original paths recorded in the archived report and manifest describe where files were located when generated.

## Analysis code and original inputs

- [Deep-analysis script](../scripts/deep_analysis.py): reads the saved aggregate tables and applies the fee-inclusive assumptions. Future runs write to `analsis/deep_analysis/`, preserving the archive.
- [Analysis checks](../scripts/test_deep_analysis.py): independent underwriting and selection-boundary tests.
- [Aggregate input table](../outputs/tables/segments_underwritten.csv): current segment-level inputs for the 14-unit recommendation.
- [Configuration](../src/config.py) and [decision log](../docs/decision_log.md): original project assumptions, including the neighbourhood concentration limit.

From the repository root:

```bash
python3 scripts/deep_analysis.py
python3 -m unittest discover -s scripts -p 'test_deep_analysis.py'
```

These commands run the fee-inclusive analysis. They do **not** reproduce the current fee-excluded recommendation without applying the exclusions and selection rules documented in [the English report](recommendation_en.md).

## Reading the numbers correctly

- Current recommendation: 14 units, about CAD 9.50 million deployed, annual contribution of about CAD 560,509 **before the three excluded operating costs**.
- The 5.90% contribution-to-capital ratio is not a fully costed net investment return.
- The 40% neighbourhood cap, minimum 20 comparables, and 10% segment supply limit are modelling assumptions, not independently verified assignment requirements.
- Principal-residence eligibility is relaxed as a project simulation assumption. Actual operating feasibility has not been established.
- AI assistance and calculation checks are disclosed in the reports.
