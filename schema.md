# Schema

Every fact records where it came from. Confidence values used throughout:

- **sourced**: stated in the cited text
- **observed**: Claude's reading of the plot or film; plausible, unreviewed
- **claude-knowledge**: from Claude's general knowledge; verify before relying on it
- **first pass**: an interpretive tag (archetypes) awaiting Shaf's review

## Per film: `films/<id>/`

| File | Contents | Source |
|---|---|---|
| `wikidata.json` | Credits, countries, languages, genres, based-on, derivatives, awards, runtime, budget, box office, external IDs (IMDb, TMDB, Letterboxd, Rotten Tomatoes) | Wikidata (CC0) |
| `wikipedia.<lang>.md` | Full article text by section (plot, production, themes, reception) in English and the film's own language | Wikipedia (CC BY-SA) |
| `wikipedia.json` | Which language Wikipedias cover the film (a rough measure of global reach), article revisions used | Wikipedia |
| `story.json` | Archetypes, motifs (with evidence), lineage links (with evidence, source and confidence) | Curated |
| `corrections.json` | Fixes to upstream data, with reasons. Applied when the graph is built; source files stay untouched | Curated |
| `script/screenplay.txt` (+ `.pdf`), `source.json` | Screenplay text and where it came from | IMSDb, Script Slug |
| `script/stats.json` | Scene count, interior/exterior, night share, key word counts | Measured |
| `scares.json` | Jump-scare times and descriptions, rating | Where's the Jump (crowd-sourced) |
| `visuals/measures.json` | Brightness, saturation, tint, shot count, average shot length, by minute | Measured from the full film |
| `visuals/barcode.png` | One column per second of the film, in its average colour | Measured |
| `visuals/frames/` | 12 evenly spaced frames | Full film |
| `visuals/stills/`, `stills.json`, `stills_strip.png` | Curated stills, their colour strip, mean brightness and saturation | FILMGRAB |

## Graph: `graph/`

- **Node types:** film, person, company, country, language, archetype, motif, source (novels, legends, real events, grimoires)
- **Edge types:** directed_by, written_by, shot_by, scored_by, edited_by, stars, made_by, from_country, in_language, carries_archetype, has_motif, adapted_from, inspired_by_real, legend, draws_on, shares_motif, remade_as, followed_by, prequel
- **Motif families** group specific motifs ("a deer on the road", "a dead deer rises") so films connect. The mapping lives in `tools/build_graph.py`.
