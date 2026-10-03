# Data quality

Generated 2026-10-03 from `films/*/corrections.json`. Source files are never edited; problems are recorded per film and the tools skip what is marked unusable (coverage, era figures, the story-layer validator and search tools).

## Unusable or damaged source files

| Problem | Film | File | How it is treated | Note |
|---|---|---|---|---|
| commentary track | Alien (1979) | `dialogue/subtitles.en.srt` | not used | Cast and crew commentary (Weaver, Scott, Skerritt and others). |
| commentary track | Audition (1999) | `dialogue/subtitles.en.srt` | not used | Cast and crew commentary on the shoot. |
| commentary track | Bram Stoker's Dracula (1992) | `dialogue/subtitles.en.srt` | not used | Coppola's director's commentary, not the film's dialogue. |
| commentary track | Creature from the Black Lagoon (1954) | `dialogue/subtitles.en.srt` | a few clean lines quoted; measures invalid | Film historian Tom Weaver's commentary; the film's own lines appear only occasionally. One film line is quoted; measures are invalid. |
| commentary track | Dawn of the Dead (2004) | `dialogue/subtitles.en.srt` | not used | Director and producer commentary, not the film's dialogue. |
| commentary track | Don't Breathe (2016) | `dialogue/subtitles.en.srt` | a few clean lines quoted; measures invalid | Commentary track with some film lines and sound captions marked by speaker name; only those are quoted; measures are invalid. |
| commentary track | Dracula (1931) | `dialogue/subtitles.en.srt` | not used | Film historian commentary on Lugosi and the production. |
| commentary track | Frankenstein (1931) | `dialogue/subtitles.en.srt` | not used | Film historian commentary. |
| commentary track | Onibaba (1964) | `dialogue/subtitles.en.srt` | not used | Director's commentary (Shindo, Sato, Yoshimura), not the film's dialogue. |
| commentary track | Silent Hill (2006) | `dialogue/subtitles.en.srt` | not used | Director's commentary. |
| commentary track | The Housemaid (1960) | `dialogue/subtitles.en.srt` | not used | Critics' commentary on the film, not its dialogue. Entries quoted from it were removed. |
| commentary track | The Mummy (1932) | `dialogue/subtitles.en.srt` | not used | Film historian commentary. |
| empty file | Alien (1979) | `script/screenplay.txt` | not used | The screenplay file contains no text. |
| empty file | The Entity (1982) | `script/screenplay.txt` | not used | The screenplay file contains no text. |
| garbled scan | Bram Stoker's Dracula (1992) | `script/screenplay.txt` | a few clean lines quoted; measures invalid | Poor scan with garbled words; only clean lines are quoted, and its measures are unreliable. |
| garbled scan | Don't Look Now (1973) | `script/screenplay.txt` | not used | Unreadable scan output. |
| garbled scan | Picnic at Hanging Rock (1975) | `script/screenplay.txt` | not used | Badly garbled scan text. |
| garbled scan | The Amityville Horror (1979) | `script/screenplay.txt` | a few clean lines quoted; measures invalid | Poor scan; only clean lines are quoted. |
| garbled scan | The Texas Chain Saw Massacre (1974) | `script/screenplay.txt` | a few clean lines quoted; measures invalid | Poor scan with garbled characters; only clean lines are quoted. |
| wrong film | Bhoot (2003) | `dialogue/subtitles.en.srt` | not used | Subtitles of Ghost House (2004, South Korea), not Bhoot; its dialogue measures are wrong too. |
| wrong film | Salem's Lot (1979) | `dialogue/subtitles.en.srt` | not used | Subtitles of the 2004 TNT remake (soup kitchen opening, e-mails, Da Nang), not the 1979 miniseries. |

These were found while reading subtitles and screenplays for the story layer, plus a scan for commentary vocabulary across every English subtitle file. The OPUS corpus files are matched by IMDb ID and length, so a commentary track of the right length can pass; more may exist among films whose files were not read closely.

## Corrections to upstream data

| Film | Field | Removed | Reason |
|---|---|---|---|
| Get Out (2017) | countries | Japan | Wikidata lists Japan as a country of origin; the English Wikipedia article and production credits (Blumhouse, Universal) give no Japanese involvement. Likely a Wikidata error. Logged 2026-10-03; consider fixing upstream on Wikidata. |
