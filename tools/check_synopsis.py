# Check films/<id>/synopsis.json: 45 to 110 words, 3 to 6 links written as [phrase|lens|fear], every link one of the
# film's grouped fears, and no em dashes. Usage: python3 tools/check_synopsis.py [film ids]
import glob, json, re, sys
P = {f["id"]: f for f in json.load(open("record/site/patterns.json"))["films"]}
LINK = re.compile(r"\[([^\]|]+)\|([a-z_]+)\|([^\]]+)\]")
ids = sys.argv[1:] or [p.split("/")[1] for p in sorted(glob.glob("films/*/synopsis.json"))]
bad = 0
for fid in ids:
    p = f"films/{fid}/synopsis.json"; errs = []
    try: d = json.load(open(p))
    except Exception as e: print(fid, "missing or bad JSON:", e); bad += 1; continue
    t = d.get("text", ""); plain = LINK.sub(lambda m: m.group(1), t)
    n = len(plain.split()); links = LINK.findall(t)
    if not 45 <= n <= 110: errs.append(f"{n} words")
    if not 3 <= len(links) <= 6: errs.append(f"{len(links)} links")
    allowed = {(dm, x.lower()) for dm, v in P.get(fid, {}).get("g", {}).items() for x in v["f"]}   # archetype names change case for display
    for ph, lens, fear in links:
        if (lens, fear.lower()) not in allowed: errs.append(f"unknown link {lens}|{fear}")
    if "—" in t or "–" in t: errs.append("dash")
    if "[" in LINK.sub("", t) or "]" in LINK.sub("", t): errs.append("broken link markup")
    for k in ("source", "basis", "written", "status"):
        if k not in d: errs.append(f"missing {k}")
    if errs: bad += 1; print(fid, "; ".join(errs))
print(f"{len(ids) - bad} of {len(ids)} valid")
