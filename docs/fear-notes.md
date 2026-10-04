# Fear narrations

Each fear's page opens with a short narration beside its stills: a few sentences that make a reader feel the fear and see it travel through the films, in the same voice as the film synopses.

## What to write

- 60 to 110 words, two to four sentences, present tense.
- Lead with the fear itself, in human terms, then show it at work in two to four specific films from the record: a named character, a place, a concrete moment. Let the films do the work; avoid listing.
- Where the numbers printed by `tools/fear_pack.py` show something striking (it rises or fades across the century, or it lives mostly in one part of the world), say so plainly in one clause. Do not invent figures.
- Every fact about a film must come from the synopsis printed for it, or from the fear's definition and kinds. Nothing from memory.
- Plain and atmospheric, like a good programme note. No rhetorical questions, no exclamation marks, no em dashes, no "not X, but Y" constructions, no lists.

## Links

- Link 2 to 4 films, written as `[phrase|film id]`, where the id comes from the fear's "films in the record" list. The phrase is your own words about that film's moment, not just its title (for example `[Laura searching the orphanage for Simón|2007-the-orphanage]`).
- If a fear has fewer than two films in the record, link the ones it has and mention others by title only.

## The file

One file per kind of fear, `reference/fear-notes/<lens>.json`, a JSON object keyed by fear name (copied exactly from the pack):

```json
{
  "a life taken": {"text": "Narration with a [linked phrase|1945-dead-of-night] in it.", "source": "Claude", "written": "<YYYY-MM-DD>", "status": "first pass, unreviewed"}
}
```

Check with `python3 tools/check_fear_notes.py <lens>` until every fear is valid.
