# Investment committee presentation

`ddd_investment_pitch.pptx` has six main slides for a seven-minute pitch, plus five appendix slides. Use `speaker_notes.md` for delivery prompts and `preparation_and_qa.md` for rehearsal. Numerical source: `../current/results.json`.

## Rebuild

First run `python3 run.py` and `python3 scripts/prepare_materials.py` from the repository root. The slide builder uses the supplied `@oai/artifact-tool` Node runtime and presentation validation helpers, not Python PowerPoint libraries.

In the authoring environment, link this directory's ignored `node_modules` to the supplied runtime packages and execute:

```bash
node analysis/presentation/build_deck.mjs
```

The builder records the runtime/skill paths it uses near its start; adjust those paths for another compatible installation. It writes rendered previews under ignored `.build/` and its private validation receipt under the root `.codex-finalizer/`. The finalizer does not overwrite an existing final PPTX: move an old final to the archive or choose a new output filename before a new build.

The financial workflow itself uses the standard library and is independent of this slide-authoring runtime. The deck uses native editable tables and charts; literal chart data is embedded as a workbook snapshot. Speaker notes cite sources. Preview and package checks do not prove behaviour in Microsoft PowerPoint or Google Slides; open the file in the presentation application before presenting.
