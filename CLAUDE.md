# Bloodline

Private research corpus of 500 horror films, owned by Shafeeq Shajahan (Shaf). Full context, data structure, archetype codes, tool list and next steps are in `docs/handover.md`; read it before substantial work. `docs/schema.md` defines every file. Archetype codes, beats and folk roots are in `archetypes.csv`.

## Working rules

- Shaf is non-technical. Explain in plain English, lead with what the data shows, and keep code out of the conversation unless he asks.
- Never sign in with Shaf's credentials or use his API keys. If a step needs a login, he runs it himself. Never read `.env`.
- Never work around a site that blocks automated access (e.g. Does the Dog Die). Record it as a gap.
- Keep the repo private (it is public for now by Shaf's choice; he will make it private when he's done). Don't commit PDFs or video; use Git LFS for images.
- Never edit source files to fix data. Use `films/<id>/corrections.json`.
- Every new fact carries a source, retrieval date and confidence level (`sourced`, `observed`, `claude-knowledge`, `first pass`). Interpretive tags stay labelled as first pass until Shaf reviews them.
- Regenerate `graph/` and `reports/coverage.md` after any data change.
- Bad source files (commentary tracks, wrong film, empty or garbled scans) are listed under `unusable_sources` in the film's `corrections.json` and skipped by the tools; `tools/data_quality.py` writes `reports/data-quality.md`. Check a subtitle file is the film's dialogue before measuring or quoting it.
- Story elements (`films/<id>/story_elements.json`) follow `docs/story-elements.md`: every entry needs a verbatim quote from the film's Wikipedia article. Run `tools/validate_story.py` after any change, and `tools/story_report.py` to refresh `reports/story-elements.md`.
- The front end (the Liver & Lung piece) may show every layer, including stills, subtitles and screenplay text. Shaf is not publishing it, so don't restrict it to derived data.
- Check year and country when matching titles; remakes and same-name films are common.

## Running things

- Install dependencies: `pip install -r requirements.txt`. `pdftotext` and `ffmpeg` are needed for screenplays and full-film analysis.
- Run scripts from the repo root with `PYTHONPATH=tools`, e.g. `PYTHONPATH=tools python3 tools/build_graph.py`.
- After a data change: `tools/coverage.py`, `tools/eras.py`, `tools/build_graph.py`. All three are deterministic; on unchanged data they reproduce the committed files exactly.
- Collection is resumable: `tools/run_batch.py --only tier1,subs,scares,scripts,stills`. It skips anything collected or marked absent (`*.none`, `script/none`).
- Keep requests to Wikipedia slow (1 per 3 s) with an identifying User-Agent. The Wikipedia API (`api.php`, REST) throttles this environment after a few calls; `index.php?action=raw` works, which is what `tools/tier1_wikipedia_bulk.py` uses. Wikidata's `wbsearchentities` is also throttled; use the SPARQL endpoint (with `mwapi` EntitySearch) instead.

## Repo notes

- Git history starts with the 10-film pilot (5 commits from Cowork), then the 500-film import. Section 2 of `docs/handover.md` describes a fresh `git init`; that was not needed because history was preserved.
- `graph/` is generated. Never hand-edit it.
- `_cache/` (subtitle-archive indexes) is gitignored and rebuilt on demand.
