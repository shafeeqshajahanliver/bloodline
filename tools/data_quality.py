# Write reports/data-quality.md from every film's corrections.json: unusable source files and upstream fixes.
import csv, glob, json, datetime
films = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
rows, fixes = [], []
for p in sorted(glob.glob("films/*/corrections.json")):
    fid = p.split("/")[1]; d = json.load(open(p)); t = f"{films[fid]['title']} ({films[fid]['year']})"
    for u in d.get("unusable_sources", []): rows.append((u["problem"], t, u["file"], u["use"], u["reason"]))
    for c in d.get("remove", []): fixes.append((t, c["field"], c["name"], c["reason"]))
USE = {"none": "not used", "quotes_only": "a few clean lines quoted; measures invalid"}
md = [f"# Data quality\n\nGenerated {datetime.date.today()} from `films/*/corrections.json`. Source files are never edited; problems are recorded per film and the tools skip what is marked unusable (coverage, era figures, the story-layer validator and search tools).\n",
      "## Unusable or damaged source files\n", "| Problem | Film | File | How it is treated | Note |", "|---|---|---|---|---|"]
md += [f"| {a} | {b} | `{c}` | {USE[d]} | {e} |" for a, b, c, d, e in sorted(rows)]
md += ["\nThese were found while reading subtitles and screenplays for the story layer, plus a scan for commentary vocabulary across every English subtitle file. The OPUS corpus files are matched by IMDb ID and length, so a commentary track of the right length can pass; more may exist among films whose files were not read closely.\n",
       "## Corrections to upstream data\n", "| Film | Field | Removed | Reason |", "|---|---|---|---|"]
md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in fixes]
open("reports/data-quality.md", "w").write("\n".join(md) + "\n"); print(len(rows), "problem files,", len(fixes), "fixes")
