# Story DNA: horror

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

Pilot of 10 films complete across three tiers; see `reports/coverage.md`.

## Loading the graph

Kumu, Cosmograph or Gephi can import `graph/nodes.csv` and `graph/edges.csv` directly. Node `type` (film, person, archetype, motif, source, country, language, company) is the natural colour key.
