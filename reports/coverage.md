# Pilot coverage

Generated 2026-10-03. A dash means the source had nothing for this film.

| Film | Year | Cast (Wikidata) | Wikipedia | Lineage links | Motifs | Screenplay | Jump scares | Visuals |
|---|---|---|---|---|---|---|---|---|
| Nosferatu | 1922 | 17 | en+de | 2 | 6 | – | – | full film |
| Psycho | 1960 | 17 | en | 2 | 5 | yes | 2 | 66 stills |
| The Exorcist | 1973 | 12 | en | 3 | 5 | yes | 11 | 28 stills |
| Ringu | 1998 | 9 | en+ja | 4 | 5 | – | 6 | 66 stills |
| Pontianak Harum Sundal Malam | 2004 | 2 | en+ms | 2 | 5 | – | – | – |
| Train to Busan | 2016 | 8 | en+ko | 2 | 5 | – | 4 | 44 stills |
| Get Out | 2017 | 12 | en | 0 | 6 | yes | 10 | 66 stills |
| Hereditary | 2018 | 5 | en | 1 | 6 | yes | 8 | 66 stills |
| Tumbbad | 2018 | 6 | en+hi | 4 | 6 | – | – | – |
| La Llorona | 2019 | 4 | en+es | 2 | 5 | – | – | 66 stills |

## Gaps and what fills them

| Gap | Films | Fix |
|---|---|---|
| Subtitles (full dialogue) | all 10 | OpenSubtitles account (Shaf setting up) |
| Screenplay | Nosferatu (silent: intertitles only), Ringu, Pontianak, Train to Busan, Tumbbad, La Llorona | Subtitles are the substitute; Nosferatu intertitles can be transcribed from the film |
| Jump-scare data | Nosferatu, Pontianak, Tumbbad, La Llorona | Not on Where's the Jump. Could be measured from the film's sound if Shaf owns copies |
| Stills | Pontianak, Tumbbad | Not on FILMGRAB. TMDB account (Shaf setting up) or own copies |
| Full-film visual measures | all except Nosferatu | Needs copies Shaf owns; then `tools/tier3_visual.py` runs unchanged |
| Content flags | all 10 | Does the Dog Die blocks automated access (403). Not worked around |

## Data-quality notes

- **Get Out** is listed on Wikidata as a US–Japan production. Nothing supports Japan; removed via `films/2017-get-out/corrections.json`, source data left untouched.
- **The Exorcist** screenplay is a fan transcript of the finished film, not Blatty's shooting script.
- **FILMGRAB's first "Psycho" result was the 1998 remake.** Caught and replaced; the stills script should check the year on every page.
- **Nosferatu** visual measures come from a 320×240 copy of the tinted restoration. Fine for colour and rhythm, too small for detailed frames.
- The source gaps fall unevenly: every gap in jump-scare and stills coverage is a non-Anglophone film except Nosferatu. Fan-built datasets reproduce the canon's bias, so the global films will always need more manual work.
