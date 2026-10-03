# Story elements: bottom-up story layer

Each film is described along ten independent dimensions read from its Wikipedia plot. Nothing is assigned from a fixed list: values are short phrases in open vocabulary, merged into shared terms afterwards. Archetypes are not used here; they can later be tested as combinations of these dimensions.

File: `films/<id>/story_elements.json`. Check with `PYTHONPATH=tools python3 tools/validate_story.py [film ids]`.

## Dimensions

| Key | Question | Example values |
|---|---|---|
| `threat` | What is the danger? | ghost, killer, creature, possessing spirit, cursed object, place, cult, village, disease, the self, unseen force |
| `origin` | Where did the threat come from? | person who died wronged, made by someone, summoned, inherited, from nature, from outside, unexplained |
| `wants` | What drives the threat? | revenge, hunger, a body, to spread, to replace someone, to be acknowledged, nothing stated |
| `wrong` | What past act sits underneath? | murder, betrayal, abandoned child, broken promise, sin, colonial crime |
| `trigger` | What sets the story off? | moving in, taking an object, breaking a rule, an invitation, a ritual, a journey, watching something |
| `rules` | How does the threat work, and how can it be stopped? | dies in seven days, must not look, must be invited, weak to fire, cannot be stopped |
| `who_suffers` | Who is endangered, and how are they related to the threat? | mother, child, couple, newcomer, friends, investigator |
| `ending` | How does it resolve? | threat destroyed, threat survives, everyone dies, cycle passes on, victim becomes threat, ambiguous |
| `images` | Concrete recurring images | well, mirror, videotape, long black hair, doll, deer, doorway |
| `beats` | Key events in order | opening omen, first death, warning ignored, reveal, final confrontation, closing sting |

## Entry fields

Every entry has:

- `value`: a short generic phrase in English, lower case, 1 to 6 words ("ghost", "parent kills child"). Specifics go in `detail`.
- `detail` (optional): the specific case ("Sadako, thrown into a well by her father").
- `quote`: a verbatim passage (5 to 40 words) copied from the film's `wikipedia.<lang>.md`. It may be in the article's language. The validator rejects quotes that are not found in the article.
- `confidence`: `sourced` when the quote states it directly; `observed` when it is a reasonable reading of the quoted passage.

Extra fields:

- `who_suffers`: `relation_to_threat`: one of `stranger`, `family`, `lover`, `community`, `self`, `unknown`.
- `images`: `state` (free text, e.g. "dead", "hurt", "rising"), `when` and `role`.
- `beats`: `order` (1, 2, 3…), `when` and optional `role`.
- `when` is one of `opening`, `early`, `middle`, `late`, `ending` (position in the plot summary, which runs in order).
- `role` for images and beats is one of `omen`, `trigger`, `mirror`, `threat`, `weapon`, `clue`, `symbol`, `setting`, `turn`.

## Rules

- No quote, no entry. Only use the plot, lead and themes/analysis sections of the film's own article.
- A dimension the article doesn't cover goes in `not_stated`. Not stated is different from absent.
- Several entries per dimension are fine. Aim for 1 to 3 per dimension, 3 to 8 images and 4 to 8 beats.
- `plot_quality`: `full` (plot section of 150+ words), `thin` (under 150), `none` (no plot section; then only the lead is used).
- `status` stays `first pass, unreviewed` until Shaf reviews it.

## Refining with subtitles and screenplays

Wikipedia plots keep the plot and drop texture (Get Out's deer is not in its plot summary). A second pass refines each film using its subtitles (`dialogue/subtitles.*.srt`, which often include sound captions such as "(DEER GROANING)") and screenplay (`script/screenplay.txt`, 116 films).

- `moments`: any entry can carry a list of moments that pin it to the film: `{"source": "subtitles", "at": "HH:MM:SS", "quote": "..."}` or `{"source": "screenplay", "quote": "..."}`. Subtitle times are those of the subtitle file, which may be a slightly different cut from other versions.
- New entries found only in subtitles or the screenplay set `"source": "subtitles"` (with `at`) or `"source": "screenplay"` and quote that file. Entries without `source` come from Wikipedia.
- Quotes from subtitles and screenplays may be 2 to 40 words (sound captions are short). The validator matches them on letters and digits only, because the subtitle files put spaces before punctuation, and checks that a subtitle quote appears within a minute after its `at` time.
- Up to 12 beats and 12 images once refined. `refined` records the date of the pass.
- Screenplays are drafts and may differ from the finished film; prefer subtitles for timing.
- Tools: `tools/film_sources.py <id>` prints the current elements, all sound captions with times, the opening and closing ten minutes of dialogue, and the screenplay's scene list and opening and closing pages. `tools/find_moment.py <id> <terms>` searches subtitles and screenplay.

Worked example of a refined film: `films/2017-get-out/story_elements.json`.
