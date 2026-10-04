# Print what a writer needs for one kind of fear's narrations: for each fear, its definition, its kinds with original
# wording, how it moves through time and across regions, and the films in the record that carry it with their
# synopses (the only allowed film links). Usage: PYTHONPATH=tools python3 tools/fear_pack.py <lens>
import json, re, sys
P = json.load(open("record/site/patterns.json")); lens = sys.argv[1]
ERAS = [("<1960", 0, 1959), ("1960s-70s", 1960, 1979), ("1980s-90s", 1980, 1999), ("2000-14", 2000, 2014), ("2015+", 2015, 9999)]
era = lambda y: next(e for e, a, b in ERAS if a <= y <= b)
syn = {}
for f in P["films"]:
    if f["rec"]:
        try: syn[f["id"]] = re.sub(r"\[([^\]|]+)\|[^\]]+\]", r"\1", json.load(open(f"films/{f['id']}/synopsis.json"))["text"])
        except Exception: syn[f["id"]] = ""
for fear, d in sorted(P["fears"][lens].items()):
    if fear == "unclear": continue
    fs = [f for f in P["films"] if fear in f["g"].get(lens, {}).get("f", [])]
    print(f"=================== {lens}|{fear}\ndefinition: {d}\nin {len(fs)} of {len(P['films'])} films")
    print("by era: " + ", ".join(f"{e} {sum(1 for f in fs if era(f['y']) == e)}/{sum(1 for f in P['films'] if era(f['y']) == e)}" for e, _, _ in ERAS))
    regs = sorted({f["r"] for f in P["films"]}, key=lambda r: -sum(1 for f in fs if f["r"] == r))
    print("by region: " + ", ".join(f"{r} {sum(1 for f in fs if f['r'] == r)}/{sum(1 for f in P['films'] if f['r'] == r)}" for r in regs))
    ks = P["kinds"].get(lens, {}).get(fear, {})
    if any(ks.values()): print("kinds: " + "; ".join(f"{k} ({', '.join(v[:3])})" for k, v in ks.items()))
    print("films in the record (allowed links, id | title | synopsis):")
    for f in sorted([f for f in fs if f["rec"]], key=lambda f: f["y"]):
        print(f"  {f['id']} | {f['t']} ({f['y']}, {f['c']}) | {syn.get(f['id'], '')[:420]}")
    print("other films (mention by title only, no link): " + "; ".join(f"{f['t']} ({f['y']})" for f in fs if not f["rec"])[:900])
