# Bloodline: story DNA of 500 horror films

A private research corpus of 500 horror films, built to find the shared patterns ("story DNA") behind them, for the podcast *You've Heard This Before* and the Liver & Lung interactive pieces.

**Private use only.** This repository contains screenplays and film stills under copyright. Keep it private; do not publish raw files. Derived measurements (counts, colour values, timings) are what can be shared.

## Layout

- `films.csv`: the master list of all 500 films, with archetype tags (first pass) and status.
- `films/<year-title>/`: one folder per film. See `schema.md` for every file.
- `sources/`: articles on legends and real events that films descend from.
- `graph/`: **generated** network files (`nodes.csv`, `edges.csv`, `shared_nodes.json`). Never edit by hand: run `python3 tools/build_graph.py`.
- `reports/`: coverage, gaps and findings.
- `tools/`: the scripts that collected everything, so any step can be re-run or extended to the next films.

## Status

Automated collection has run across all 500 films; see `reports/coverage.md` for what each source covered and `reports/findings-500.md` for first trends. The pilot 10 also have a hand-curated story layer (motifs and lineage with evidence).

## Re-running

- `tools/resolve_ids.py`: match films.csv to Wikidata and IMDb
- `tools/run_batch.py --only tier1,subs,scares,scripts,stills [--part i/n]`: resumable collection
- `tools/tier1_bulk.py`: faster facts collection when Wikidata throttles
- `tools/tier2_subtitles.py <film ids>`: subtitles from the OPUS OpenSubtitles corpus (no login)
- `tools/subs_quality.py`, `tools/script_stats.py`, `tools/coverage.py`, `tools/eras.py`, `tools/build_graph.py`: measures, reports and graph

## Loading the graph

Kumu, Cosmograph or Gephi can import `graph/nodes.csv` and `graph/edges.csv` directly. Node `type` (film, person, archetype, motif, source, country, language, company) is the natural colour key.
