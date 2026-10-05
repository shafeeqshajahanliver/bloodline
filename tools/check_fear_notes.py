# Check reference/fear-notes/<lens>.json: one narration per fear, 55 to 120 words, 2 to 4 film links written as
# [phrase|film id], each a record film that carries the fear, no em dashes. Usage: python3 tools/check_fear_notes.py [lenses]
import json, os, re, sys
P = json.load(open("record/site/patterns.json"))
LINK = re.compile(r"\[([^\]|]+)\|([0-9a-z-]+)\]")
bad = total = 0
for lens in sys.argv[1:] or P["dims"]:
    p = f"reference/fear-notes/{lens}.json"
    if not os.path.exists(p): print(lens, "missing"); continue
    notes = json.load(open(p)); want = [x for x in P["fears"][lens] if x != "unclear"]
    if lens == "archetypes": notes = {k[0] + k[1:].lower(): v for k, v in notes.items()}   # names are shown in sentence case
    for fear in want:
        total += 1; t = notes.get(fear, {}).get("text", "") if isinstance(notes.get(fear), dict) else notes.get(fear, ""); errs = []
        if not t: errs.append("missing")
        else:
            n = len(LINK.sub(lambda m: m.group(1), t).split()); links = LINK.findall(t)
            ok = {f["id"] for f in P["films"] if f["rec"] and fear in f["g"].get(lens, {}).get("f", [])}
            if not 55 <= n <= 120: errs.append(f"{n} words")
            if not (2 if len(ok) >= 2 else len(ok)) <= len(links) <= 4: errs.append(f"{len(links)} links")
            for ph, fid in links:
                if fid not in ok: errs.append(f"film {fid} does not carry it")
            if "—" in t or "–" in t: errs.append("dash")
        if errs: bad += 1; print(f"{lens}|{fear}: " + "; ".join(errs))
    extra = set(notes) - set(want)
    if extra: print(lens, "unknown fears:", sorted(extra)[:5])
print(f"{total - bad} of {total} valid")
