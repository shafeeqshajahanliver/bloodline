# Print what a writer needs for a film's synopsis: title, year, country, its plot (Wikipedia lead and plot, trimmed),
# and the grouped fears it carries (lens|fear), which are the only allowed link targets.
# Usage: PYTHONPATH=tools python3 tools/synopsis_pack.py <film id> [...]
import csv, glob, json, re, sys
rows = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
P = {f["id"]: f for f in json.load(open("record/site/patterns.json"))["films"]}
KEEP = re.compile(r"^(lead|plot.*|synopsis|story|summary|premise|storyline|sinopsis|sinopse|trama|handlung|inhalt|intrigue|résumé)$", re.I)
for fid in sys.argv[1:]:
    r = rows[fid]; print(f"=================== {fid}\n{r['title']} ({r['year']}), {r['country']}")
    for f in sorted(glob.glob(f"films/{fid}/wikipedia.*.md"), key=lambda f: not f.endswith(".en.md"))[:1]:
        md = open(f).read(); out = []
        for m in re.finditer(r"^## (.+?)\n\n(.*?)(?=^## |\Z)", md, re.M | re.S):
            if KEEP.match(m.group(1).strip()): out.append(m.group(2).strip())
        print("--- plot\n" + " ".join(" ".join(out).split()[:900]))
    print("--- allowed links (lens|fear)")
    for d, v in P.get(fid, {}).get("g", {}).items():
        for fear in v["f"]:
            if fear != "unclear": print(f"{d}|{fear}")
