# Check films/<id>/story_elements.json against docs/story-elements.md.
# Every quote must appear verbatim (ignoring whitespace and quote-mark style) in one of the film's wikipedia.<lang>.md files.
# Usage: python3 tools/validate_story.py [film ids]   (no ids: every film that has the file)
import glob, json, os, re, sys
from subs import cues, key, secs
DIMS = ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images", "beats"]
WHEN = {"opening", "early", "middle", "late", "ending"}
ROLE = {"omen", "trigger", "mirror", "threat", "weapon", "clue", "symbol", "setting", "turn"}
REL = {"stranger", "family", "lover", "community", "self", "unknown"}
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()
def check(fid):
    p = f"films/{fid}/story_elements.json"
    if not os.path.exists(p): return ["missing file"]
    try: d = json.load(open(p))
    except Exception as e: return [f"bad JSON: {e}"]
    text = " ".join(norm(open(f).read()) for f in glob.glob(f"films/{fid}/wikipedia.*.md"))
    subs = {f: cues(f) for f in glob.glob(f"films/{fid}/dialogue/subtitles.*.srt")}
    subkey = key(" ".join(x for C in subs.values() for _, x in C))
    sp = f"films/{fid}/script/screenplay.txt"
    spkey = key(open(sp, errors="ignore").read()) if os.path.exists(sp) else ""
    def other(tag, m):
        """Check a quote taken from subtitles or the screenplay (and its time, for subtitles)."""
        e2 = []; q = m.get("quote", ""); src = m.get("source")
        nw = len(q) // 2 if CJK.search(q) else len(q.split())
        if nw < 2: e2.append(f"{tag}: quote under 2 words")
        elif nw > 40: e2.append(f"{tag}: quote over 40 words")
        if src == "screenplay":
            if key(q) not in spkey: e2.append(f"{tag}: quote not found in screenplay: {q[:60]}")
        elif src == "subtitles":
            if key(q) not in subkey: e2.append(f"{tag}: quote not found in subtitles: {q[:60]}")
            at = m.get("at", "")
            if not re.fullmatch(r"\d\d:\d\d:\d\d", at): e2.append(f"{tag}: at must be HH:MM:SS")
            else:
                t = secs(at + ",0")
                if not any(key(q) in key(" ".join(x for tt, x in C if t - 10 <= tt <= t + 60)) for C in subs.values()):
                    e2.append(f"{tag}: quote not found within a minute after {at}")
        else: e2.append(f"{tag}: source must be subtitles or screenplay")
        return e2
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
            elif v != v.lower(): errs.append(f"{tag}: value not lower case: {v}")
            for j, m in enumerate(e.get("moments", [])): errs += other(f"{tag}.moments[{j}]", m)
            if e.get("source", "wikipedia") != "wikipedia":
                errs += other(tag, e)
                if e.get("confidence") not in ("sourced", "observed"): errs.append(f"{tag}: confidence")
                if k in ("images", "beats") and e.get("when") not in WHEN: errs.append(f"{tag}: when")
                continue
            q = e.get("quote", "")
            nw = len(q) // 2 if CJK.search(q) else len(q.split())  # no spaces in CJK text: count ~2 characters per word
            if nw < 5: errs.append(f"{tag}: quote under 5 words")
            elif nw > 40: errs.append(f"{tag}: quote over 40 words")
            if nw >= 1 and norm(q) not in text: errs.append(f"{tag}: quote not found in article: {q[:60]}")
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
