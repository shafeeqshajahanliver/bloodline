# Shared helpers for reading .srt subtitle files (the OPUS files put spaces before punctuation: "I 've", "is ,").
import re
def secs(t):
    h, m, s = t.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
def hms(x):
    x = int(x); return f"{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}"
def tidy(s):
    s = re.sub(r"\s+([,.!?;:%)\]'’])", r"\1", s); s = re.sub(r"([(\[])\s+", r"\1", s)
    return re.sub(r"\s+(n't|'s|'re|'ve|'ll|'d|'m)\b", r"\1", s)
def cues(path):
    out = []
    for b in re.split(r"\n\s*\n", open(path, errors="ignore").read()):
        m = re.search(r"(\d\d:\d\d:\d\d[,.]\d+)\s*-->", b)
        if not m: continue
        text = " ".join(l.strip() for l in b.split("\n")[2:] if l.strip())
        if text: out.append((secs(m.group(1)), tidy(text)))
    return out
def key(s):
    """Letters and digits only, lower case: how quotes from subtitles and screenplays are matched."""
    return re.sub(r"[\W_]+", "", s.lower())
