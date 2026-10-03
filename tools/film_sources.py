# Print a compact pack of everything the story layer can draw on for one film, for refining story_elements.json:
# current story elements, subtitle sound captions with times, the opening and closing 10 minutes of dialogue,
# and the screenplay's opening and closing pages plus its scene list. Search the rest with tools/find_moment.py.
# Usage: python3 tools/film_sources.py <film id>
import glob, json, os, re, sys
from subs import cues, hms
fid = sys.argv[1]; d = f"films/{fid}"
print(f"=================== {fid}")
p = f"{d}/story_elements.json"
if os.path.exists(p):
    se = json.load(open(p))
    print("----- current story elements (dimension: value [when, role])")
    for k, es in se.get("dimensions", {}).items():
        for i, e in enumerate(es):
            extra = ", ".join(x for x in (e.get("when"), e.get("role")) if x)
            print(f"{k}[{i}]: {e['value']}" + (f" [{extra}]" if extra else "") + (f"  ({len(e['moments'])} moments)" if e.get("moments") else ""))
for srt in sorted(glob.glob(f"{d}/dialogue/subtitles.*.srt")):
    C = cues(srt); lang = srt.rsplit(".", 2)[1]
    if not C: continue
    end = C[-1][0]
    print(f"----- {os.path.basename(srt)}: {len(C)} cues, last at {hms(end)}")
    if lang != "en": continue
    caps = [(t, x) for t, x in C if re.search(r"[\(\[][^\)\]]{2,60}[\)\]]|♪", x)]
    print(f"--- sound captions ({len(caps)})")
    for t, x in caps: print(f"[{hms(t)}] {x}")
    print("--- opening 10 minutes of dialogue")
    for t, x in C:
        if t <= C[0][0] + 600: print(f"[{hms(t)}] {x}")
    print("--- closing 10 minutes of dialogue")
    for t, x in C:
        if t >= end - 600: print(f"[{hms(t)}] {x}")
sp = f"{d}/script/screenplay.txt"
if os.path.exists(sp):
    raw = open(sp, errors="ignore").read()
    lines = [re.sub(r"\s+", " ", l).strip() for l in raw.split("\n")]
    lines = [l for l in lines if l and not re.fullmatch(r"\d+\.?|\(?CONTINUED\)?:?|CONT'D", l, re.I)]
    words = " ".join(lines).split()
    print(f"----- screenplay.txt: {len(words)} words. Scene headings:")
    for l in lines:
        if re.match(r"(\d+\s+)?(INT|EXT|INTERIOR|EXTERIOR)[\.\-/ ]", l): print("  " + l[:90])
    print("--- opening pages"); print(" ".join(words[:2500]))
    print("--- closing pages"); print(" ".join(words[-2000:]))
