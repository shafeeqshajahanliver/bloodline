# Search a film's subtitles (all languages) and screenplay for words or phrases; prints each hit with its time
# (subtitles) or line number (screenplay) and a little context.
# Usage: python3 tools/find_moment.py <film id> <term> [<term> ...]   (terms are case-insensitive regular expressions)
import glob, os, re, sys
from subs import cues, hms
from sources import unusable
fid, terms = sys.argv[1], sys.argv[2:]
d = f"films/{fid}"
for term in terms:
    rx = re.compile(term, re.I); print(f"===== {term}")
    for srt in sorted(glob.glob(f"{d}/dialogue/subtitles.*.srt")):
        if unusable(fid).get(srt.split("/", 2)[2]) == "none": print(f"----- {os.path.basename(srt)}: UNUSABLE (see corrections.json), skipped"); continue
        C = cues(srt); hits = [i for i, (t, x) in enumerate(C) if rx.search(x)]
        for i in hits[:15]:
            ctx = " / ".join(C[j][1] for j in range(max(0, i - 1), min(len(C), i + 2)))
            print(f"  {os.path.basename(srt)} [{hms(C[i][0])}] {ctx}")
        if len(hits) > 15: print(f"  ... {len(hits) - 15} more in {os.path.basename(srt)}")
    sp = f"{d}/script/screenplay.txt"
    if os.path.exists(sp):
        L = [re.sub(r"\s+", " ", l).strip() for l in open(sp, errors="ignore").read().split("\n")]
        hits = [i for i, l in enumerate(L) if rx.search(l)]
        for i in hits[:15]:
            ctx = " ".join(l for l in L[max(0, i - 2):i + 3] if l)
            print(f"  screenplay line {i + 1}: {ctx[:400]}")
        if len(hits) > 15: print(f"  ... {len(hits) - 15} more in screenplay")
