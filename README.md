# Bloodline

**The story DNA of 500 horror films.**

Horror keeps telling the same stories. A wronged woman comes back. A house remembers what was done in it. Someone invites the thing in. Bloodline maps 500 horror films from 1913 to 2025 and 44 countries to find those shared patterns, and traces each one back to the folk tales, legends and real events it descends from.

It is the research base for interactive pieces by Liver & Lung.

> **Status:** research in progress. Archetype tags and story elements are a first pass and not yet reviewed. Trends are leads to test, not conclusions.

---

## What's in it

| Layer | What it holds | Source |
|---|---|---|
| **The list** | 500 films with country, region and two archetype tags each | Curated (`films.csv`) |
| **Archetypes** | 27 recurring story shapes, each with its beat and documented folk roots on at least two continents | Curated (`archetypes.csv`) |
| **Facts** | Cast, crew, companies, countries, languages, runtime, budget, awards, external IDs | Wikidata |
| **Plot summaries** | Full Wikipedia articles by section: plot, production, reception, themes | Wikipedia |
| **Dialogue** | Subtitles and measures: words per minute, share of runtime with dialogue, longest silences | OPUS OpenSubtitles corpus |
| **Scares** | Jump-scare timings and ratings | Where's the Jump |
| **Screenplays** | Script text and measures: interior/exterior split, night scenes | IMSDb, Script Slug |
| **Visuals** | Curated stills with brightness, saturation and a colour strip | FILMGRAB |
| **Story elements** | Each film described along 10 dimensions (threat, origin, what it wants, the wrong underneath, trigger, rules, who suffers, ending, images, beats), every entry quoted from its Wikipedia article. 497 films | Read from Wikipedia (`story_elements.json`) |
| **Pilot story layer** | Hand-curated motifs and lineage links with evidence and confidence (10 pilot films) | Curated (`story.json`) |
| **Graph** | A network of films, people, archetypes, motifs and sources | Generated (`graph/`) |

Current coverage for each layer is in [`reports/coverage.md`](reports/coverage.md).

## First findings

From [`reports/findings-500.md`](reports/findings-500.md), [`reports/story-elements.md`](reports/story-elements.md) and [`reports/pilot-findings.md`](reports/pilot-findings.md). All are leads to test.

- **Horror stopped letting the monster lose.** Before 1960, 59% of films end with the threat beaten and 12% with it surviving or passing on. Since 2000 it's about 17% beaten and 50% surviving.
- **The threat moved closer to home.** The share of films where the victims are the threat's own family, or the threat is the self, rose from 49% before 1960 to 62% since 2015.
- **Horror got quieter.** Counting English-language films only, dialogue fell from about 113 words a minute before 1960 to about 88 from the 1960s, and 81 since 2015. The share of runtime with dialogue has fallen from 50% to 39%. (Subtitles of non-English films run far lower, around 56 words a minute, because translation compresses speech, so they are compared separately. Twelve subtitle files turned out to be commentary tracks and one belonged to the wrong film; they are excluded, see [`reports/data-quality.md`](reports/data-quality.md).)
- **The first scare moved forward ten minutes,** from around minute 28 in the 1960s and 70s to around minute 18 from 1980, and it has stayed there.
- **Jump scares peaked and retreated:** a median of 9 per film in 2000–14, down to 5 since 2015, in line with the rise of slower "elevated" horror.
- **An animal is the commonest omen.** 221 of the 497 films (44%) use an animal as a warning sign, 148 of them in the opening or first act. Dogs lead by far, then cats, birds, crows and snakes; Get Out's deer, Talk to Me's kangaroo and The Invitation's coyote all come back at the end. Most of these are invisible in plot summaries and were found in the subtitles and screenplays.
- **Every South Asian film in the list has a past wrong driving it** (16 of 16), against 74% in North America, and endings where the dead are laid to rest or appeased are more common in South, Southeast and East Asia than in the US.

Jump-scare and screenplay data comes from fan and English-language sources, so trends built on them describe US and UK horror more than horror in general. Plot summaries and story elements cover every region.

## The 27 archetypes

| | | |
|---|---|---|
| The Woman Who Comes Back | The House Remembers | The Inherited Curse |
| The Thing You Took Home | The Voice Inside | The Bargain |
| The Wrong Child | The Devouring Mother | The Double |
| The Beast Within | The One Who Feeds | The Dead Won't Stay Dead |
| The Book You Shouldn't Read | You Invited It In | The Bad Host |
| The Village Needs Blood | The Hunger | The Thing Outside |
| Stray From the Path | The Thing We Made | The Body Betrays |
| The Contagion | The Witch at the Edge of the Woods | Nobody Believes Her |
| The Descent | The Rule | The Endless Night *(on probation)* |

Each one must have documented roots on at least two continents, appear in roughly 3 to 30 films, and not be a catch-all like "good versus evil". Beats and roots are in [`archetypes.csv`](archetypes.csv).

## Methodology

**The list.** 500 films compiled from critics' and fan canons, deliberately weighted towards global horror (though North America, the UK and continental Europe still make up 72%). Each film was matched to Wikidata and IMDb automatically, checking year and country; 16 hard cases were matched by hand (`tools/ids_manual.json`). Two films (Seru, The Tokoloshe) have no Wikidata item.

**Collected layers.** Facts come from Wikidata, plots from Wikipedia (English, plus the original-language article when the English plot is missing or under 150 words), subtitles from the OPUS OpenSubtitles research corpus (the file closest to the film's runtime is chosen and flagged if it is more than 5 minutes off), jump scares from Where's the Jump, screenplays from IMSDb and Script Slug, and stills from FILMGRAB, always checking the page's year. Every file records its source and retrieval date; a `*.none` file means the source was checked and had nothing. Sites that block automated access are recorded as gaps, not worked around.

**Story elements (bottom-up).** Rather than sorting films into predefined categories, each film is described along ten independent dimensions read from its Wikipedia plot:

| Dimension | Question |
|---|---|
| Threat | What is the danger? |
| Origin | Where did it come from? |
| What it wants | What drives it? |
| The wrong underneath | What past act sits underneath? |
| Trigger | What sets the story off? |
| Rules | How does the threat work, and how can it be stopped? |
| Who suffers | Who is endangered, and how are they related to the threat? |
| Ending | How does it resolve? |
| Images | Concrete images, with their state, when they appear and their role (omen, clue, weapon…) |
| Beats | Key events in order, with when they happen |

How it works:

- **Open vocabulary.** Values are short generic phrases written by the reader, not picked from a list, so patterns can emerge from the films rather than from a scheme imposed on them. Merging near-duplicates into a shared vocabulary is the next step.
- **No quote, no entry.** Every entry carries a verbatim passage from the article. `tools/validate_story.py` rejects any quote that does not appear word for word in the article, plus quotes under 5 or over 40 words.
- **Gaps are explicit.** A dimension the article doesn't cover is marked `not_stated`, which is different from absent.
- **Confidence.** `sourced` when the quote states it directly, `observed` when it is a reasonable reading of the quoted passage (553 of 15,086 entries).
- **Who did the reading.** The plots were read by Claude, split across parallel helpers working from one schema (`docs/story-elements.md`) and one worked example (Ringu). Every entry is a first pass until reviewed.
- **Refined from subtitles and screenplays.** A second pass read every film's subtitles (including sound captions such as "(DEER GROANING)") and, for 116 films, its screenplay. It pinned 11,558 entries to a timestamp and added 3,109 entries that plot summaries miss, especially animal omens, spoken rules and closing stings. Each carries its source and a verbatim quote, checked against the file (and, for subtitles, against the time). Get Out's deer, absent from its Wikipedia plot, is now in the data four times. Screenplays are drafts and can differ from the finished film; entries from them say so.
- **Known limit.** Twelve subtitle files turned out to be commentary tracks and two belonged to other films; they are excluded (`reports/data-quality.md`). Films with no subtitles and no screenplay (about 50) rest on their plot summary alone.

**Archetypes.** The 27 archetypes are a separate, top-down lens: first-pass tags on every film, to be tested against the bottom-up story elements rather than treated as findings.

## How it's organised

```
films.csv            the 500 films: tags, IDs, and which data layers each one has
archetypes.csv       the 27 archetypes: code, beat, folk roots
films/<year-title>/  one folder per film (see docs/schema.md for every file)
graph/               network files, generated by tools/build_graph.py
reports/             coverage, findings, era figures
sources/             articles on the legends and real events films descend from
reference/           the original spreadsheet and a log of every tag change
tools/               the scripts that collected and measured everything
docs/                schema, story-elements method and project handover notes
```

## Principles

- **Every fact says where it came from** and when it was retrieved.
- **Interpretation is kept apart from fact.** Archetypes and motifs carry a confidence level: `sourced` (stated in a cited text), `observed` (a reading of the film), `claude-knowledge` (needs checking) or `first pass` (awaiting review).
- **Source data is never edited.** Fixes go in a per-film `corrections.json`, applied when the graph is built.
- **Gaps are recorded, not hidden.** A `*.none` file means a source was checked and had nothing.

## Exploring the graph

`graph/nodes.csv` and `graph/edges.csv` load straight into Kumu, Cosmograph or Gephi. Colour by node `type` (film, person, archetype, motif, source, country, language, company).

## Re-running

Python 3. Install with `pip install -r requirements.txt`; `pdftotext` and `ffmpeg` are also needed for screenplays and full-film analysis. Run everything from the repo root with `PYTHONPATH=tools`.

| Step | Script |
|---|---|
| Match films to Wikidata and IMDb | `tools/resolve_ids.py` (hand-checked matches in `tools/ids_manual.json` override the automatic ones) |
| Collect data (resumable, skips what's done) | `tools/run_batch.py --only tier1,subs,scares,scripts,stills` |
| Wikipedia articles (resumable, ~1 request per 3 s) | `tools/tier1_wikipedia_bulk.py [film ids]` |
| Subtitles for given films | `tools/tier2_subtitles.py <film ids>` |
| Full-film colour and pacing | `tools/tier3_visual.py <video> <film id>` |
| Read a film's plot for the story layer | `tools/plot_text.py <film id>` |
| Check story elements | `tools/validate_story.py [film ids]` |
| Rebuild reports and graph | `tools/coverage.py`, `tools/eras.py`, `tools/story_report.py`, `tools/build_graph.py` |

## Rights

The repository mixes material with different rights:

- **Facts from Wikidata** are CC0. **Wikipedia text** (in `sources/` and each film's `wikipedia.*.md`, and the quotes in `story_elements.json`) is CC BY-SA.
- **Screenplays, subtitles and film stills** are copyrighted by their owners and are held here for private, non-commercial research only. They are not covered by any licence and should not be reused.
- **Derived measurements** (counts, timings, colour values) and the curated layers (archetypes, story element values, motifs, lineage) are the project's own work.

No licence has been chosen yet for the code and curated data, so all rights are reserved for now.
