# Film synopses

Each film in the record opens with a short synopsis beside its still: a few sentences that make a reader feel what the film is, with its key phrases linked to the fears it carries.

## What to write

- 50 to 90 words, two to four sentences, present tense.
- Specific to this film: its people, its place, its central image or situation. A reader should be able to tell which film it is without the title.
- Atmospheric but plain. Write like a good programme note, not a list of story parts and not a trailer. No rhetorical questions, no exclamation marks, no em dashes, and no "not X, but Y" constructions.
- Every fact must come from the film's plot text printed by `tools/synopsis_pack.py`. Do not add facts from memory. It is fine to leave the ending unresolved rather than spoil a twist.

## Links

- Weave in 3 to 5 links, written as `[phrase|lens|fear]`, where `lens|fear` is copied exactly from the film's "allowed links" list.
- The phrase is your own wording about this film, not the fear's name. Link the phrase that shows the fear at work in this story.
- Spread the links across different lenses where the story allows (for example a threat, a wrong, a symbol, an ending), and link each fear at most once.

## The file

`films/<id>/synopsis.json`:

```json
{
  "film": "<id>",
  "text": "Sentence with a [linked phrase|lens|fear] in it.",
  "source": "Claude",
  "basis": "the film's Wikipedia plot",
  "written": "<YYYY-MM-DD>",
  "status": "first pass, unreviewed"
}
```

Check with `python3 tools/check_synopsis.py <id>` until it prints valid.
