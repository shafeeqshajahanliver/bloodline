# Build the release-3 pattern data: every film with story elements (not just the 100 in the record), with each of its
# elements mapped to the grouped vocabulary in reference/vocab/<dim>.tsv. Writes record/site/patterns.json.
# Usage: PYTHONPATH=tools python3 tools/build_patterns.py
import csv, glob, json, os, re
from subs import tidy
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
    # one-line definitions from the .md: the first plain paragraph under each "## fear" heading
    defs = {}
    mdp = f"reference/vocab/{d}.md"
    if os.path.exists(mdp):
        cur = None
        for line in open(mdp):
            line = line.strip()
            if line.startswith("## "):
                cur = re.sub(r"\s*\(.*\)\s*$", "", line[3:]).strip().lower(); continue
            if cur and line and not line.startswith(("-", "#", "|", "*")):
                defs.setdefault(cur, line); cur = None
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
# archetypes: the 27 top-down story shapes from archetypes.csv, tagged on every film (primary and secondary)
ARCH = {r["code"]: dict(r, name=r["name"][0] + r["name"][1:].lower()) for r in csv.DictReader(open("archetypes.csv"))}   # names in sentence case
for f in films:
    r = rows[f["id"]]; got = [(c, role) for c, role in ((r["archetype_primary"], "the main story"), (r["archetype_secondary"], "a second thread")) if c in ARCH]
    if got: f["g"]["archetypes"] = {"f": sorted({ARCH[c]["name"] for c, _ in got}), "k": sorted({f"{ARCH[c]['name']}|{role}" for c, role in got})}
defs["archetypes"] = {a["name"]: f"{a['beat']}. Roots: {a['roots']}." for a in ARCH.values()}
# nightmares: the 12 groups of films found by the graph model (tools/graph_model.py), named in reference/model/family-names.json
NIGHT = {}
if os.path.exists("reference/model/families.json"):
    names = json.load(open("reference/model/family-names.json")); byid = {f["id"]: f for f in films}
    for fam in json.load(open("reference/model/families.json")):
        name = names.get(fam["defining_fears"][0]["fear"], fam["defining_fears"][0]["fear"])
        for m in fam["members"]:
            if m in byid: byid[m]["g"]["nightmares"] = {"f": [name], "k": [f"{name}|a nightmare"]}
        NIGHT[name] = {"n": fam["films"], "fears": [[x["lens"], x["fear"], x["share_inside"], x["share_overall"]] for x in fam["defining_fears"]],
                       "arch": [[a["archetype"][0] + a["archetype"][1:].lower(), a["share"]] for a in fam.get("archetypes_inside", [])], "core": fam["core_films"]}
    defs["nightmares"] = {n: "Found by a graph model: films that carry " + ", ".join(x[1] for x in v["fears"][:3]) + " far more often than the rest." for n, v in NIGHT.items()}
# for each fear's page: its kinds, each with a few of the original phrasings (most used first)
kinds = {}
for d in vocab:
    used = {r["value"]: int(r["films"]) for r in csv.DictReader(open(f"reference/vocab/input/{d}.tsv"), delimiter="\t")}
    kd = {}
    for v, (fear, kind) in vocab[d].items():
        kd.setdefault(fear, {}).setdefault(kind, []).append((used.get(v, 0), v))
    kinds[d] = {fear: {k: [v for _, v in sorted(vs, key=lambda x: (-x[0], x[1]))[:5]] for k, vs in ks.items()} for fear, ks in kd.items()}
kinds["archetypes"] = {a["name"]: {"the main story": [], "a second thread": []} for a in ARCH.values()}
if NIGHT: kinds["nightmares"] = {n: {"a nightmare": []} for n in NIGHT}
# a few lines from the films for each fear's page: spoken lines first, then the plot, films in the record first
quotes = {d: {} for d in vocab}
for f in sorted(glob.glob("films/*/story_elements.json")):
    se = json.load(open(f)); fid = se["film"]; r = rows.get(fid)
    if not r: continue
    for d in vocab:
        for e in se["dimensions"].get(d, []):
            if e["value"] not in vocab[d]: continue
            fear = vocab[d][e["value"]][0]
            for m in [e] + e.get("moments", []):
                q = tidy((m.get("quote") or "").strip()); n = len(q.split())
                if not 5 <= n <= 26: continue
                src = m.get("source", "wikipedia")
                score = (0 if src == "subtitles" else 1 if src == "screenplay" else 2, 0 if fid in record else 1, abs(n - 12))
                quotes[d].setdefault(fear, []).append((score, {"id": fid, "t": r["title"], "y": int(r["year"]), "q": q, "src": src, "at": m.get("at", ""), "rec": fid in record}))
for d in quotes:
    for fear, qs in quotes[d].items():
        seen, out = set(), []
        for _, q in sorted(qs, key=lambda x: x[0]):
            if q["id"] in seen: continue
            seen.add(q["id"]); out.append(q)
            if len(out) == 3: break
        quotes[d][fear] = out
# hand-written narrations for each fear's page (reference/fear-notes/<lens>.json)
notes = {}
for d in list(vocab) + ["archetypes", "nightmares"]:
    np_ = f"reference/fear-notes/{d}.json"
    if os.path.exists(np_): notes[d] = {(k[0] + k[1:].lower() if d == "archetypes" else k): (v.get("text") if isinstance(v, dict) else v) for k, v in json.load(open(np_)).items()}
os.makedirs("record/site", exist_ok=True)
json.dump({"dims": (["nightmares"] if NIGHT else []) + list(vocab) + ["archetypes"], "fears": defs, "nightmares": NIGHT, "kinds": kinds, "quotes": quotes, "notes": notes, "films": films}, open("record/site/patterns.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(films)} films · dimensions grouped: {', '.join(vocab) or 'none yet'} · plus archetypes")
