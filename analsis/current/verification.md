# Verification record

Checked November 13, 2026 against the inputs hashed in `results.json`.

- Downloaded the official detailed Inside Airbnb file and rebuilt listing filters and segment aggregates.
- Downloaded public tax and parcel exports and rebuilt the neighbourhood price table: 229,095 matched tax rows, 191,840 selected residential-proxy rows. Output prices matched the committed table.
- Measured the effect of mixed scrape dates, future review dates, inactive listings, missing bedrooms, price filtering and minimum-stay thresholds.
- Tested purchase prices +10%/+20%, condo price multipliers ±10%, comparable thresholds, concentration limits, selection objectives and revenue/repair cases.
- Verified unit-count, capital, segment-capacity and neighbourhood-cap constraints. Independently rechecked financial arithmetic.
- All nine tests passed in the project's virtual environment. Without pandas, seven standard-library tests passed and two optional raw/cross-engine tests were skipped.
- Rebuilt in a clean copied workspace using only committed aggregate inputs and provenance files, without raw data or third-party packages. Holdings and performance matched exactly.
- Checked current Markdown links and input hashes. Git whitespace checks passed.
- Exported an 11-slide PPTX with 11 speaker-note pages, native tables and three editable data charts. Reviewed every slide preview. Package, layout, chart/workbook and import validations passed. Headline values in the PPTX matched current results.
- Six main-slide speaker notes contain approximately 691 words, excluding source notes; rehearse to the 6:30 target rather than assuming a fixed speaking rate.

Limits: no independent out-of-time revenue validation; no confirmed property acquisition opportunities; no proof of global optimisation; no PowerPoint/Google Slides application-level test. Public source reconstruction validates the implemented joins and calculations, not the economic truth of assessment prices or revenue estimates.
