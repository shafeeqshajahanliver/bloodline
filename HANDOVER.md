# Bloodline: handover to Claude Code

Bloodline is a private research corpus of 500 horror films. Shafeeq Shajahan (Shaf) owns it. It was built in a Claude Cowork session between 1 and 3 October 2026, and this file carries everything needed to continue in Claude Code.

Put this file in the repository root. Copy the "Working rules" section into `CLAUDE.md` so it applies to every session.

---

## 1. What this is for

- **Purpose:** find the shared "story DNA" across horror films. That means archetypes, motifs, lineage back to folk tales, and measurable trends (dialogue, scares, colour, pacing).
- **Who it feeds:**
  - Shaf's podcast *You've Heard This Before*. Each episode traces one story archetype from a specific cultural tale to modern film. Acts: The Story, The DNA, The Code.
  - Interactive pieces for the Liver & Lung website (Shaf's British-Malaysian theatre company), mainly:
    - a "DNA strip" view, where each film is a strip of coloured archetype bands;
    - a lineage view (tale → film → remake).
  - Possibly the horror musical *Melur / When Jasmine Blooms*, which draws on the pontianak tradition.
- **About Shaf:** VP Product, non-technical. Explain things in plain English, focus on what the data shows, and be direct. He doesn't read code.
- **Status:** private, personal research. The repository holds copyrighted screenplay text, subtitles and film stills. **Keep the GitHub repo private.** Derived measurements (counts, timings, colour values) are the only things that can be published.

---

## 2. Reassembling the files

The data came over as seven zips:

- `bloodline-part1-data.zip`
- `bloodline-part2a-visuals.zip`
- `bloodline-part2b-visuals.zip`
- `bloodline-part3-visuals.zip`
- `bloodline-part4-visuals.zip`
- `bloodline-part5a-visuals.zip`
- `bloodline-part5b-visuals.zip`

Every zip has `bloodline/` at its root. They must be **merged** into one tree; don't unzip them into separate folders. From the folder holding the zips:

```bash
for f in bloodline-part*.zip; do unzip -oq "$f"; done
```

If they were already unzipped by macOS into `bloodline`, `bloodline 2` … `bloodline 8`, merge them like this:

```bash
mkdir -p ~/Documents/bloodline
for d in bloodline "bloodline "[0-9]*; do [ -d "$d" ] && ditto "$d" ~/Documents/bloodline; done
```

`bloodline-data-only.zip` is an older, partial export. Ignore it.

**There is no git history in the zips.** Initialise fresh:

```bash
git init
git lfs install
git add . && git commit -m "Initial import"
```

Then push to the private repo at `https://github.com/shafeeqshajahanliver/bloodline`.

---

## 3. Expected data structure

### Top level

```
bloodline/
├── README.md              project overview and how to re-run
├── schema.md              every file and field defined, plus confidence conventions
├── HANDOVER.md            this file
├── films.csv              master index: 500 rows + header
├── .gitattributes         Git LFS rules for *.jpg *.jpeg *.png *.pdf *.mp4 (hidden file; must exist)
├── .gitignore             excludes _cache/, video files, *.pdf, .env (hidden file)
├── films/                 482 folders, one per film that matched an ID
├── graph/
│   ├── nodes.csv          4,507 nodes + header
│   ├── edges.csv          7,161 edges + header
│   └── shared_nodes.json  every non-film node linked to 2+ films, sorted by count
├── reports/
│   ├── coverage.md        coverage by layer and by region; lists the 18 unmatched films
│   ├── findings-500.md    first cross-era trends (dialogue, scares, runtime)
│   ├── pilot-findings.md  leads from the 10-film pilot
│   ├── eras.json          numbers behind findings-500
│   └── batch.log          log of the automated run
├── sources/               12 Wikipedia articles on source legends and real events
│                          (Okiku / Banchō Sarayashiki, Kuntilanak/Pontianak, La Llorona,
│                          Sadako Yamamura, Ed Gein, Roland Doe exorcism, Paimon, Dracula,
│                          Narayan Dharap, Ríos Montt, Ring novel, Exorcist novel)
└── tools/                 every collection and analysis script (Python 3); see section 6
```

`_cache/` (not shipped, gitignored) holds subtitle-archive indexes and working files. It gets rebuilt when needed.

### `films.csv` columns

```
id,title,year,country,region,archetype_primary,archetype_secondary,pilot,wikidata,imdb,status
```

- `id` is `<year>-<slugified title>`, e.g. `1998-ringu`. It matches the folder name in `films/`.
- `archetype_primary` / `archetype_secondary` are three-letter codes (see section 5). They are Claude's first-pass tags, **unreviewed by Shaf**.
- `pilot` is `yes` for the 10 pilot films.
- `wikidata` / `imdb` are blank for the 18 unmatched films.
- `status` is a semicolon list of the layers present, e.g. `ids; facts; subs_en; scares; stills`.

### Per film: `films/<id>/`

Not every film has every file. The "absent" markers record that a source was checked and had nothing, so the batch job doesn't recheck it.

| Path | Films | Contents |
|---|---|---|
| `wikidata.json` | 482 | Credits (directors, screenwriters, cast, cinematographers, editors, composers, producers), companies, countries, languages, genres, based_on, derivative works, series, awards, nominations, runtime, budget, box office, release dates, external IDs (IMDb, TMDB, Letterboxd, Rotten Tomatoes, Metacritic), Wikipedia language editions. Source: Wikidata (CC0) |
| `dialogue/measures.json` | 482 | Per language: found yes or no, chosen file, runtime match, lines, words, words per minute, share of runtime with dialogue, first line time, 5 longest silences, words by minute, quietest 10-minute window, `quality` (`good` / `check`) and notes |
| `dialogue/subtitles.<lang>.srt` | 490 files | 427 English; also es 17, fr 10, it 10, id 9, ko 7, th 5, de 2, ms 2, hi 1. Source: OPUS OpenSubtitles v2024 corpus |
| `scares.json` / `scares.none` | 188 / 294 | Jump-scare times, descriptions, rating. Source: Where's the Jump (crowd-sourced) |
| `script/screenplay.txt` + `source.json` + `stats.json` / `script/none` | 115 / 367 | Screenplay text, where it came from, and measures (scene headings, interior/exterior, night share, key word counts). Sources: IMSDb, Script Slug. PDFs were deliberately dropped |
| `visuals/stills/NNN.jpg` + `stills.json` + `stills_strip.png` / `visuals/stills.none` | 260 / 222 | Up to 24 stills per film (66 for the pilot films), mean brightness and saturation, a colour strip. Source: FILMGRAB. 6,100 jpgs in total |
| `story.json` | 10 (pilot only) | Archetypes with roles; motifs with evidence and confidence; lineage links (relation, target, evidence, source URL, confidence) |
| `wikipedia.json` + `wikipedia.<lang>.md` | 10 (pilot only) | Full Wikipedia article text by section, in English plus the film's own language where available |
| `corrections.json` | 1 (Get Out) | Overrides to upstream data with reasons. Applied at graph build; source files stay untouched |
| `visuals/measures.json`, `barcode.png`, `frames/` | 1 (Nosferatu) | Full-film analysis: per-second colour, brightness, tint share, shot count, average shot length, a colour barcode, 12 frames |

### Graph files

- **`nodes.csv`:**
  - `id, type, label` plus film attributes: year, country, region, duration, wikipedia_languages, jump_scares, jump_rating, first_scare_min, brightness, saturation, avg_shot_length_s, script_night_share, script_interior_share, words_per_minute, dialogue_share, longest_silence_s, imdb, tmdb, wikidata.
  - Node types and counts: film 482, person 3,575, company 256, country 58, language 50, archetype 27, motif 37, source 22.
- **`edges.csv`:**
  - `from, to, type, detail, confidence`.
  - Types: directed_by, written_by, shot_by, scored_by, edited_by, stars (top 6 cast), made_by, from_country, in_language, carries_archetype, has_motif, adapted_from, inspired_by_real, legend, draws_on, shares_motif, remade_as, followed_by, prequel.
- **Regenerated, never hand-edited:** `python3 tools/build_graph.py`. Motif families (how specific motifs group so films connect) are defined in `FAM` inside `build_graph.py`.

### Verification

Run from the repo root. It should print the numbers shown in the comments:

```bash
ls films | wc -l                                   # 482
find films -name "*.jpg" | wc -l                   # 6100
find films -name "*.srt" | wc -l                   # 490
ls films/*/wikidata.json | wc -l                   # 482
ls films/*/script/screenplay.txt | wc -l           # 115
ls films/*/scares.json | wc -l                     # 188
ls films/*/visuals/stills.json | wc -l             # 260
wc -l films.csv graph/nodes.csv graph/edges.csv    # 501 / 4508 / 7162
ls -a | grep -E "^\.git(attributes|ignore)$"       # both present
```

---

## 4. Conventions

- **Provenance on everything.** Every file says where its data came from and when it was retrieved.
- **Confidence levels** (used in `story.json` and `edges.csv`):
  - `sourced`: stated in a cited text.
  - `observed`: Claude's reading of the plot or film; unreviewed.
  - `claude-knowledge`: from Claude's general knowledge; verify before relying on it.
  - `first pass`: an interpretive tag awaiting Shaf's review.
- **Source data is never edited.** Fixes go in `corrections.json` per film.
- **Interpretation stays separate from facts.** Archetypes and motifs are readings, and they must stay labelled as such.

---

## 5. Archetype codes

There are 26 archetypes plus one on probation. Each has documented folk roots; these are listed in the Archetypes sheet of the earlier `horror-500-story-dna.xlsx`.

| Code | Archetype | Code | Archetype |
|---|---|---|---|
| WOM | The Woman Who Comes Back | INV | You Invited It In |
| HOU | The House Remembers | HOS | The Bad Host |
| CUR | The Inherited Curse | SAC | The Village Needs Blood |
| OBJ | The Thing You Took Home | HUN | The Hunger |
| POS | The Voice Inside | OUT | The Thing Outside |
| BAR | The Bargain | PAT | Stray From the Path |
| CHI | The Wrong Child | MAD | The Thing We Made |
| MOT | The Devouring Mother | BOD | The Body Betrays |
| DOU | The Double | CON | The Contagion |
| BEA | The Beast Within | WIT | The Witch at the Edge of the Woods |
| FEE | The One Who Feeds | CAS | Nobody Believes Her |
| REV | The Dead Won't Stay Dead | DES | The Descent |
| BOO | The Book You Shouldn't Read | RUL | The Rule |
| LOO | The Endless Night (probation) | | |

Rules used to define the list:

- Each archetype has documented roots from at least two continents.
- Each appears in roughly 3 to 30 films.
- The list excludes catch-alls ("hero's journey", "good vs evil").

---

## 6. Tools and how the collection works

All scripts run from the repo root with `PYTHONPATH=tools`. They need Python 3 with `requests`, `beautifulsoup4`, `numpy` and `Pillow`. `pdftotext` (poppler) is needed for screenplays and `ffmpeg` for full-film analysis.

| Script | Does |
|---|---|
| `common.py` | Shared HTTP session (identifying User-Agent), retries, `PILOT` map |
| `resolve_ids.py` | Matches films.csv to Wikidata/IMDb in bulk via the Wikidata query service (SPARQL). Prefers items with an English Wikipedia page, the year in the title, and the country; this fixes remake confusion. Writes `tools/ids.json` |
| `run_batch.py` | Resumable collector: `--only tier1,subs,scares,scripts,stills`, `--part i/n` for parallel workers, `--limit N`. Skips anything already collected or marked absent |
| `tier1_bulk.py` | Wikidata facts via `Special:EntityData` plus SPARQL labels. Use it when the `wbgetentities` API is throttled |
| `opus.py` | Reads single subtitle files out of the OPUS OpenSubtitles v2024 archives (`object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/xml/<lang>.zip`, English is 66 GB) using HTTP range requests only. It builds the index from the zip's central directory, caches it in `_cache/`, and keeps slim indexes filtered to our IMDb IDs |
| `tier2_subtitles.py <ids>` | Picks the subtitle file whose length best matches the runtime, and writes the `.srt` and `measures.json`. Fetches English plus the native language by country |
| `subs_quality.py` | Flags subtitle files more than 5 min off the runtime, or partial |
| `tier2_jumps.py` | Where's the Jump scraper (pilot version; batch logic is in `run_batch.py`) |
| `tier3_filmgrab.py <id> <url>` | FILMGRAB stills, capped by `MAX_STILLS`. **Always checks the page year:** the first "Psycho" hit was the 1998 remake |
| `tier3_visual.py <video> <id>` | Full-film analysis: 1 fps colour and brightness, ffmpeg scene cuts, barcode, 12 frames |
| `script_stats.py` | Screenplay measures |
| `write_story.py` | Hand-curated story layer for the pilot (data lives in the script) |
| `tier1_wikipedia.py` | Wikipedia articles (pilot only) |
| `coverage.py` | Rewrites `reports/coverage.md` and the `status`/ID columns in films.csv |
| `eras.py` | Era medians in `reports/eras.json` |
| `build_graph.py` | Regenerates `graph/` |

### Access notes as of 3 October 2026

- **Wikipedia API** (`action=query` and REST) returned 429 to the Cowork session's shared IP. From a home connection it should work; keep requests slow (1 per 2–3 s).
- **The Wikidata `wbgetentities` API was throttled.** `Special:EntityData/<Q>.json` and `query.wikidata.org/sparql` worked fine.
- **Does the Dog Die returns 403 to automated access.** Do not work around it.
- **OpenSubtitles and TMDB need logins.** Claude must not sign in with Shaf's passwords or API keys. The OPUS corpus replaces OpenSubtitles. If TMDB is wanted, Shaf has to run that step himself, with his key kept in a local `.env` file that Claude never reads.

---

## 7. Coverage and known gaps

| Layer | Films |
|---|---|
| IDs and facts | 482 / 500 |
| English subtitles | 427 (335 `good` runtime match, 91 `check`) |
| Original-language subtitles | 63 |
| Screenplays | 115 (almost all US) |
| Jump scares | 188 (mostly US/UK) |
| Stills | 260 |
| Story layer | 10 |
| Full-film visuals | 1 |

**Regional bias is real.** South Asia has 0 stills, scares or screenplays. Southeast Asia has 3 sets of stills. Every fan-built source follows the Anglophone canon. Any trend from scares or screenplays describes US/UK horror only.

**18 films have no ID match and need a manual QID/IMDb lookup:**

- Sumpah Orang Minyak (1958), A Bay of Blood (1971), Salem's Lot (1979), Satan's Slave (1982), Perfect Blue (1997)
- Ju-on: The Grudge (2002), Dabbe (2006), KM 31 (2006), Hantu Kak Limah Balik Rumah (2010), Rare Exports (2010)
- Seru (2011), Corazon: The First Aswang (2012), Siccin (2014), IT (2017), Dukun (2018)
- The Nightshifter (2018), Tokoloshe (2018), Tiger Stripes (2023)

### Data-quality notes

- **Get Out:** Wikidata lists Japan as a country; it was removed via `corrections.json`.
- **The Exorcist:** the screenplay is a fan transcript of the film, not Blatty's shooting script.
- **Nosferatu:** visuals come from a 320×240 copy of the tinted restoration (Internet Archive, public domain). Good for colour and rhythm only.
- **Ringu:** the Japanese subtitle in OPUS is empty.
- **Subtitle word counts** depend on the subtitler. Korean, Japanese and Thai counts aren't comparable with English.
- **The 500-film list** was compiled from Claude's knowledge of the horror canon, deliberately weighted to global horror. It is not a live ranked list.

---

## 8. Findings so far

These are leads, not conclusions. See `reports/`.

- **Pilot (10 films):**
  - A dead or dangerous mother is in 6 of 10 films, making it the most connected motif.
  - A deer in the road is an early omen in Train to Busan, Get Out and Hereditary.
  - Water carries the returning woman (Ringu's well, La Llorona, Okiku).
  - Train to Busan is markedly the brightest film.
  - Hereditary's screenplay is 83% interiors, against Psycho's 44%.
- **Across 500, by era (medians):**
  - Pre-1960 horror runs at about 106 words a minute, with dialogue over 50% of the film. From 1960 on it's about 75.
  - The first jump scare moved from about minute 28 (1960s–70s) to about minute 18 (1980 onwards).
  - Scares per film peaked at 9 (2000–14), then fell to 5 (2015–25), which fits the "elevated horror" shift.
  - Runtime grew from 82 to about 100 minutes.
- **Graph hubs:** Dario Argento (9 films), Cronenberg (8), Carpenter, Craven, Stephen King. Universal (19 films) is the biggest company.

---

## 9. Next steps, in priority order

1. **Push to the private GitHub repo** with Git LFS.
2. **Shaf reviews the archetype tags.** Every downstream view inherits them.
3. **Fetch Wikipedia plot summaries for all 482,** throttled. These unlock step 4.
4. **Extend the story layer to all films:** motifs with evidence, lineage links with citations, the same confidence levels. Use the Thompson Motif-Index or ATU tale types as the backbone where possible. Draft for Shaf to review; never present it as fact.
5. **Manually match the 18 unmatched films,** then rerun `run_batch.py` for them.
6. **Fill the regional gaps** for South and Southeast Asian films: stills, native-language subtitles, and any regional scare or content sources.
7. **Full-film visual analysis** for films Shaf owns, plus all public-domain titles on the Internet Archive (roughly pre-1930, and others such as Night of the Living Dead).
8. **The lineage map,** Shaf's favourite view: 20–30 well-documented chains first (e.g. Okiku → Ringu → The Ring; Nosferatu 1922 → 1979 → 2024; La Llorona → KM 31 → La Llorona 2019).
9. **Visual front end for the Liver & Lung site.** Seat Intelligence (seat-intelligence.com) is the style reference:
   - paper background `#fbfbf9`, ink `#151515`, a single accent;
   - Source Serif 4, Libre Caslon Text italic, Courier Prime for machine-made numbers;
   - printed-object feel, two-pane layout, no gamification;
   - the DNA strip as the main view.

---

## 10. Working rules (copy into CLAUDE.md)

- Shaf is non-technical. Explain in plain English, lead with what the data shows, and keep code out of the conversation unless he asks.
- Never sign in with Shaf's credentials or use his API keys. If a step needs a login, he runs it himself.
- Never work around a site that blocks automated access. Record it as a gap.
- Keep the repo private. Don't commit PDFs or video; use Git LFS for images.
- Never edit source files to fix data. Use `corrections.json`.
- Every new fact carries a source, retrieval date and confidence level. Interpretive tags stay labelled as first pass until Shaf reviews them.
- Regenerate `graph/` and `reports/coverage.md` after any data change.
- Check year and country when matching titles; remakes and same-name films are common.
