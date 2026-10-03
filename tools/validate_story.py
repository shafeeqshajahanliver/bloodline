# Check films/<id>/story_elements.json against docs/story-elements.md.
# Every quote must appear verbatim (ignoring whitespace and quote-mark style) in one of the film's wikipedia.<lang>.md files.
# Usage: python3 tools/validate_story.py [film ids]   (no ids: every film that has the file)
import glob, json, os, re, sys
DIMS = ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images", "beats"]
WHEN = {"opening", "early", "middle", "late", "ending"}
ROLE = {"omen", "trigger", "mirror", "threat", "weapon", "clue", "symbol", "setting", "turn"}
REL = {"stranger", "family", "lover", "community", "self", "unknown"}
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()
def check(fid):
    p = f"films/{fid}/story_elements.json"
    if not os.path.exists(p): return ["missing file"]
    try: d = json.load(open(p))
    except Exception as e: return [f"bad JSON: {e}"]
    text = " ".join(norm(open(f).read()) for f in glob.glob(f"films/{fid}/wikipedia.*.md"))
    errs = []
    if d.get("film") != fid: errs.append("film id mismatch")
    if d.get("plot_quality") not in ("full", "thin", "none"): errs.append("plot_quality")
    dims = d.get("dimensions", {})
    for k in dims:
        if k not in DIMS: errs.append(f"unknown dimension {k}")
    for k in DIMS:
        if k not in dims and k not in d.get("not_stated", []): errs.append(f"{k}: neither filled nor in not_stated")
        for i, e in enumerate(dims.get(k, [])):
            tag = f"{k}[{i}]"
            v = e.get("value", "")
            if not v or len(v.split()) > 6: errs.append(f"{tag}: value missing or over 6 words")
            q = e.get("quote", "")
            if len(q.split()) < 3: errs.append(f"{tag}: quote too short")
            elif norm(q) not in text: errs.append(f"{tag}: quote not found in article: {q[:60]}")
            if e.get("confidence") not in ("sourced", "observed"): errs.append(f"{tag}: confidence")
            if k in ("images", "beats"):
                if e.get("when") not in WHEN: errs.append(f"{tag}: when")
                if e.get("role") and e["role"] not in ROLE: errs.append(f"{tag}: role {e['role']}")
            if k == "beats" and not isinstance(e.get("order"), int): errs.append(f"{tag}: order")
            if k == "who_suffers" and e.get("relation_to_threat") not in REL: errs.append(f"{tag}: relation_to_threat")
    return errs
if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(p.split("/")[1] for p in glob.glob("films/*/story_elements.json"))
    bad = 0
    for fid in ids:
        e = check(fid)
        if e: bad += 1; print(fid, "\n  " + "\n  ".join(e))
    print(f"{len(ids) - bad} of {len(ids)} valid")
