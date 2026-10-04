# Grouping the story vocabulary

The story elements were written in open wording, so the same idea appears many ways ("ghost", "vengeful spirit", "the dead wife's ghost"). Release 3 needs them grouped so patterns can be counted. Grouping adds two labels to every value; the original wording is never changed or lost.

## Inputs and outputs

- Input: `reference/vocab/input/<dim>.tsv`, one row per distinct value across all films: the value, how many films use it, up to three example films, an example detail, and (for images) roles or (for who suffers) relations.
- Output: `reference/vocab/<dim>.tsv`, tab-separated with the header `value	kind	fear`. Every input value appears exactly once, copied character for character.
- Output: `reference/vocab/<dim>.md`, listing each fear with a one-line definition, then its kinds.
- Check with `python3 tools/check_vocab.py <dim>` until it prints OK.

## The two levels

- **kind**: a specific idea that several phrasings share. Values that mean the same thing share a kind.
- **fear**: a broad group of kinds, named in plain human terms. Aim for roughly 8 to 25 fears per dimension, as many as the material needs.
- Both labels are lower case, short (a kind up to 6 words, a fear up to 5), and describe the human situation or fear rather than a genre or trope label.

## Rules

1. Read every value before naming anything. Let the groups come from the values. Do not start from a list of horror categories, folklore types or archetypes, and do not reuse names from other dimensions.
2. Group by meaning, not by shared words. Values with opposite meanings never share a kind or a fear.
3. Some values were suggested to the original readers as examples and are over-used. Group them by meaning like any other value; do not give them their own group because they are common.
4. A catch-all group is allowed only for values that genuinely fit nowhere, at most 3% of values, named `unclear`.
5. Keep fears distinct from each other: someone reading two fear names should be able to tell which a new value belongs to.
6. When a value is ambiguous, use the example films and detail to decide, and list the hardest cases at the end of the `.md` file.
