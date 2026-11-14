# Analysis and presentation materials

The folder name `analysis` follows the requested spelling. Updated November 13, 2026.

## Current recommendation

Read [recommendation_en.md](recommendation_en.md) for the team-facing report and [reasoning_ja.md](reasoning_ja.md) for Japanese calculation explanations.

**Investment pitch:** 13 condos (7 one-bedroom Downtown Eastside, 4 two-bedroom Downtown, 2 two-bedroom West End), about CAD 9.64m deployed, and CAD 247k modelled operating income before income tax and capital repairs. A separate 5% repairs-reserve scenario is included. The requested fee-excluded selection remains a 14-unit comparison; it is not the final cost-aware recommendation.

## Presentation

- [Editable PowerPoint](presentation/ddd_investment_pitch.pptx)
- [Speaker notes](presentation/speaker_notes.md)
- [Rehearsal and Q&A](presentation/preparation_and_qa.md)
- [Decision log](../docs/decision_log.md)
- [Assumptions](../docs/assumptions.md)

## Numerical source of truth

[Current results](current/results.json) contains the recommendation, alternative allocation, financial scenarios, constraint tests and input hashes. Its companion CSVs provide each experiment separately. [Raw validation](current/raw_validation.json) records the downloaded listing-source hash and date anomaly. [Assessment provenance](../data/external/property_values_provenance.json) records external source hashes and join counts.

Reproduce from repository root:

```bash
python3 run.py
python3 scripts/prepare_materials.py
python3 -m unittest discover -s scripts -p 'test_deep_analysis.py'
```

See the [root README](../README.md) for the fully tested raw-data route. The presentation is rebuilt separately after input changes.

## Archive

[archive/fee_inclusive_analysis](archive/fee_inclusive_analysis/) preserves the earlier eight-unit risk-focused scenario and visuals. Earlier recommendations used different prices, dates, costs and objectives. They must not be mixed with the current numerical results.
