# Build the release-3 pattern data: every film with story elements (not just the 100 in the record), with each of its
# elements mapped to the grouped vocabulary in reference/vocab/<dim>.tsv. Writes record/site/patterns.json.
# Usage: PYTHONPATH=tools python3 tools/build_patterns.py
import csv, glob, json, os
DIMS = ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images"]
rows = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
record = set(json.load(open("record/films.json")))
vocab, meta = {}, {}
for d in DIMS:
    p = f"reference/vocab/{d}.tsv"
    if not os.path.exists(p): continue
    m = {r["value"]: (r["fear"].strip(), r["kind"].strip()) for r in csv.DictReader(open(p), delimiter="\t") if r.get("fear") and r.get("kind")}
    want = {r["value"] for r in csv.DictReader(open(f"reference/vocab/input/{d}.tsv"), delimiter="\t")}
    if not want <= set(m): print(f"skipping {d}: grouping incomplete ({len(want - set(m))} values missing)"); continue
    vocab[d] = m
    # one-line definitions from the .md, if the reader wrote them as "## fear" or "- **fear**: definition"
    defs = {}
    mdp = f"reference/vocab/{d}.md"
    if os.path.exists(mdp):
        import re
        for m in re.finditer(r"^(?:#+\s*|\-\s*\*\*)([a-z][^*\n:—–]+?)(?:\*\*)?\s*(?:[:—–-]\s*|\n+)([^\n#]+)", open(mdp).read(), re.M):
            defs.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    meta[d] = defs
films = []
for f in sorted(glob.glob("films/*/story_elements.json")):
    se = json.load(open(f)); fid = se["film"]; r = rows.get(fid)
    if not r: continue
    g = {}
    for d in vocab:
        es = se["dimensions"].get(d, [])
        fears = sorted({vocab[d][e["value"]][0] for e in es if e["value"] in vocab[d]})
        kinds = sorted({"|".join(vocab[d][e["value"]]) for e in es if e["value"] in vocab[d]})
        if fears: g[d] = {"f": fears, "k": kinds}
    films.append({"id": fid, "t": r["title"], "y": int(r["year"]), "c": r["country"], "r": r["region"], "rec": fid in record,
                  "ns": se.get("not_stated", []), "g": g})
defs = {d: {fear: meta[d].get(fear, "") for fear in sorted({v[0] for v in vocab[d].values()})} for d in vocab}
os.makedirs("record/site", exist_ok=True)
json.dump({"dims": list(vocab), "fears": defs, "films": films}, open("record/site/patterns.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(films)} films · dimensions grouped: {', '.join(vocab) or 'none yet'}")
