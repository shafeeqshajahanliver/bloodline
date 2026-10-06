# Build the release-1 record (the private Bloodline Record page) for the films listed in record/films.json:
# one JSON per film, one still sheet per film, and the page with the index embedded. Output goes to record/site/ (gitignored).
import csv, glob, json, os, re, sys
from PIL import Image
sys.path.insert(0, "tools")
from sources import unusable
from subs import cues
import colorsys
OUT = "record/site"
os.makedirs(OUT + "/data", exist_ok=True); os.makedirs(OUT + "/stills", exist_ok=True)
ids = json.load(open("record/films.json"))
rows = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
# archetype names shown in sentence case ("The woman who comes back"); archetypes.csv keeps its own spelling
arch = {r["code"]: dict(r, name=r["name"][0] + r["name"][1:].lower()) for r in csv.DictReader(open("archetypes.csv"))}
DIMS = ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images", "beats"]
PLOT = re.compile(r"^(plot.*|synopsis|story|summary|premise|storyline|sinopsis|sinopse|trama|handlung|inhalt|intrigue|résumé|hikâye|konu|jalan cerita|alur|plot cerita|cốt truyện|줄거리|あらすじ|ストーリー|剧情|劇情|情节|故事|कथानक|कहानी|الحبكة|القصة|ملخص|сюжет)$", re.I)
W = 560; MAXS = 12

def names(w, k, n=None):
    v = [x["name"] for x in w.get(k, []) if x.get("name") and not re.fullmatch(r"Q\d+", x["name"])]
    v = list(dict.fromkeys(v)); return v[:n] if n else v

def money(w, k):
    for x in w.get(k, []):
        if x.get("unit") == "Q4917":
            try: return int(float(x["amount"]))
            except Exception: pass
    return None

def plot(fid):
    for f in sorted(glob.glob(f"films/{fid}/wikipedia.*.md"), key=lambda f: (not f.endswith(".en.md"), f)):
        md = open(f).read()
        for m in re.finditer(r"^## (.+?)\n\n(.*?)(?=^## |\Z)", md, re.M | re.S):
            if PLOT.match(m.group(1).strip()):
                body = re.sub(r"\n{3,}", "\n\n", m.group(2).strip())
                if len(body.split()) > 40: return {"lang": f.rsplit(".", 2)[1], "heading": m.group(1).strip(), "text": body}
    return None

def tone(im):
    # the frame's prevailing colour: the average of its more saturated pixels, falling back to the plain average
    sm = im.resize((48, 27)); px = list(sm.get_flattened_data() if hasattr(sm, "get_flattened_data") else sm.getdata())
    sat = [p for p in px if colorsys.rgb_to_hsv(*[c / 255 for c in p])[1] > 0.25 and 20 < sum(p) / 3 < 235]
    use = sat if len(sat) > len(px) * 0.15 else px
    return "#%02x%02x%02x" % tuple(round(sum(p[i] for p in use) / len(use)) for i in range(3))

def per_minute(fid, bad):
    f = f"films/{fid}/dialogue/subtitles.en.srt"
    if not os.path.exists(f) or bad.get("dialogue/subtitles.en.srt") == "none": return None
    C = cues(f)
    if not C: return None
    n = int(C[-1][0] // 60) + 1; out = [0] * n
    for t, x in C: out[int(t // 60)] += len(x.split())
    return out

def sheet(fid):
    fs = sorted(glob.glob(f"films/{fid}/visuals/stills/*.jpg"))
    if not fs: return 0, None, []
    if len(fs) > MAXS: fs = [fs[round(i * (len(fs) - 1) / (MAXS - 1))] for i in range(MAXS)]
    H = round(W * 9 / 16); ims = []; cols = []
    for f in fs:
        try:
            im = Image.open(f).convert("RGB")
        except Exception: continue
        # cover-crop to 16:9
        r = im.width / im.height
        if r > 16 / 9: nw = round(im.height * 16 / 9); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else: nh = round(im.width * 9 / 16); im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
        ims.append(im.resize((W, H), Image.LANCZOS))
        cols.append(tone(im))
    if not ims: return 0, None, []
    S = Image.new("RGB", (W, H * len(ims)))
    for i, im in enumerate(ims): S.paste(im, (0, i * H))
    S.save(f"{OUT}/stills/{fid}.jpg", quality=74, optimize=True, progressive=True)
    src = json.load(open(f"films/{fid}/visuals/stills.json")) if os.path.exists(f"films/{fid}/visuals/stills.json") else {}
    return len(ims), src.get("source"), cols

# the grouped vocabulary (reference/vocab), so each story element can point to its fear's page
VOCAB = {}
for d in ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images"]:
    vp = f"reference/vocab/{d}.tsv"
    if os.path.exists(vp): VOCAB[d] = {r["value"]: r["fear"] for r in csv.DictReader(open(vp), delimiter="\t") if r.get("fear") and r["fear"] != "unclear"}
index = []
for fid in ids:
    r = rows[fid]; d = f"films/{fid}"
    w = json.load(open(f"{d}/wikidata.json")) if os.path.exists(f"{d}/wikidata.json") else {}
    corr = json.load(open(f"{d}/corrections.json")) if os.path.exists(f"{d}/corrections.json") else {}
    countries = names(w, "countries")
    for rm in corr.get("remove", []):
        if rm.get("field") == "countries": countries = [c for c in countries if c != rm["name"]]
    se = json.load(open(f"{d}/story_elements.json"))
    bad = unusable(fid)
    meas = json.load(open(f"{d}/dialogue/measures.json")) if os.path.exists(f"{d}/dialogue/measures.json") else {}
    dia = {}
    for lang, m in meas.get("by_language", {}).items():
        if m.get("found") and bad.get(f"dialogue/subtitles.{lang}.srt") != "none":
            dia[lang] = {k: m.get(k) for k in ("words_per_minute", "share_of_runtime_with_dialogue", "first_line_at_s", "lines", "words", "runtime_gap_min")}
            dia[lang]["longest_silences"] = m.get("longest_silences", [])[:3]
    sc = None
    if os.path.exists(f"{d}/scares.json"):
        s = json.load(open(f"{d}/scares.json"))
        sc = {"rating": s.get("rating"), "source": s.get("source"), "scares": [{"t": x.get("time"), "d": x.get("description")} for x in s.get("scares", [])]}
    sp = None
    if os.path.exists(f"{d}/script/stats.json") and bad.get("script/screenplay.txt") != "none":
        st = json.load(open(f"{d}/script/stats.json")); src = json.load(open(f"{d}/script/source.json")) if os.path.exists(f"{d}/script/source.json") else {}
        sp = {k: st.get(k) for k in ("words", "scene_headings", "interior", "exterior", "night_share")}
        sp.update(site=src.get("site"), source=src.get("source"))
        if bad.get("script/screenplay.txt"): sp["note"] = "Scan is partly garbled; quotes only."
    pilot = json.load(open(f"{d}/story.json")) if os.path.exists(f"{d}/story.json") else None
    nst, stsrc, cols = sheet(fid)
    dims = {k: [dict(e, fear=VOCAB[k][e["value"]]) if e["value"] in VOCAB.get(k, {}) else e for e in se["dimensions"].get(k, [])] for k in DIMS}
    filled = [k for k in DIMS if dims[k]]
    wurl = w.get("wikipedia_url") or ""
    rec = {
        "id": fid, "title": r["title"], "year": int(r["year"]), "country": r["country"], "region": r["region"],
        "arch": [c for c in (r["archetype_primary"], r["archetype_secondary"]) if c],
        "directors": names(w, "directors"), "writers": names(w, "screenwriters", 6), "cast": names(w, "cast", 12),
        "dop": names(w, "cinematographers", 3), "music": names(w, "composers", 3), "producers": names(w, "producers", 4),
        "countries": countries, "languages": names(w, "original_languages"), "subjects": names(w, "main_subjects", 8),
        "set_in": names(w, "narrative_locations", 6), "shot_in": names(w, "filming_locations", 6),
        "runtime": w.get("duration_min"), "budget": money(w, "budget"), "box": money(w, "box_office"),
        "links": {"wikipedia": wurl, "wikidata": w.get("wikidata_url"), "imdb": f"https://www.imdb.com/title/{r['imdb']}/" if r["imdb"] else None,
                  "letterboxd": f"https://letterboxd.com/film/{w['letterboxd_id']}/" if w.get("letterboxd_id") else None},
        "plot_quality": se.get("plot_quality"), "status": se.get("status"), "not_stated": se.get("not_stated", []),
        "dims": dims, "plot": plot(fid), "dialogue": dia, "scares": sc, "script": sp, "pilot": pilot,
        "synopsis": (json.load(open(f"{d}/synopsis.json")).get("text") if os.path.exists(f"{d}/synopsis.json") else None),
        "stills": nst, "stills_source": stsrc, "tones": cols, "wpm_series": per_minute(fid, bad),
        "unusable": corr.get("unusable_sources", []), "removed": corr.get("remove", []),
    }
    json.dump(rec, open(f"{OUT}/data/{fid}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    # index row: enough to search and filter without loading the film
    vals = sorted({e["value"] for k in DIMS for e in dims[k]})
    index.append({"id": fid, "t": r["title"], "y": int(r["year"]), "c": r["country"], "r": r["region"], "a": rec["arch"],
                  "dir": rec["directors"][:2], "cast": rec["cast"][:6], "f": filled, "ns": rec["not_stated"],
                  "n": sum(len(dims[k]) for k in DIMS), "st": nst, "sub": "en" in dia, "osub": any(l != "en" for l in dia),
                  "sp": bool(sp), "sc": bool(sc), "pl": bool(pilot), "pq": rec["plot_quality"],
                  "rt": rec["runtime"], "wpm": (dia.get("en") or {}).get("words_per_minute"), "ds": (dia.get("en") or {}).get("share_of_runtime_with_dialogue"), "nsc": len(sc["scares"]) if sc else None, "fsc": (sc["scares"][0]["t"] if sc and sc["scares"] else None), "tone": cols[len(cols)//2] if cols else None, "rel": sorted({e.get("relation_to_threat") for e in dims["who_suffers"] if e.get("relation_to_threat")}), "v": vals, "lede": (dims["threat"][0]["value"] if dims["threat"] else "")})
json.dump({"films": index, "arch": {k: {"name": v["name"], "beat": v["beat"], "roots": v["roots"], "status": v["status"]} for k, v in arch.items()}},
          open(f"{OUT}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(index), "films;", sum(1 for x in index if x["st"]), "with stills")

# ---- the film as a node: its nearest neighbours among the chosen films, and what links them
import math, collections
PRIMED = ["vengeful ghost","serial killer","cult","possessing demon","person who died wronged","summoned by ritual","revenge","hunger","moving into a new home","must not look","cycle passes on","threat survives","threat destroyed","ambiguous","everyone dies","victim becomes threat","made by someone","unexplained","from nature","from outside","inherited"]
def primed(v): return any(v == p or re.search(r"\b" + re.escape(p.rstrip("s")) + r"s?\b", v) for p in PRIMED)
recs = {fid: json.load(open(f"{OUT}/data/{fid}.json")) for fid in ids}
def feats(d):
    out = {}
    for k, es in d["dims"].items():
        for e in es: out[f"el|{k}|{e['value']}"] = {"type": "element", "dim": k, "label": e["value"]}
    for role, key, n in (("director", "directors", None), ("writer", "writers", None), ("actor", "cast", 8)):
        for nm in (d[key][:n] if n else d[key]): out.setdefault(f"p|{nm}", {"type": "person", "label": nm, "roles": []})["roles"].append(role)
    for c in d["arch"]: out[f"a|{c}"] = {"type": "archetype", "label": arch[c]["name"] if c in arch else c, "code": c}
    return out
FE = {fid: feats(r) for fid, r in recs.items()}
allnb = {}
count = collections.Counter(k for f in FE.values() for k in f)
def weight(k, meta):
    base = {"person": 3.0, "archetype": 1.0, "element": 1.6}[meta["type"]]
    w = base / math.log2(1 + count[k])           # rarer links count for more
    if meta["type"] == "element" and primed(meta["label"]): w *= 0.5   # example wording over-connects
    return w
for fid, r in recs.items():
    mine = FE[fid]; nb = []
    for o in ids:
        if o == fid: continue
        sh = [k for k in mine if k in FE[o]]
        if sh: nb.append((sum(weight(k, mine[k]) for k in sh), o, sh))
    nb.sort(key=lambda x: (-x[0], x[1]))
    top = nb[:14]
    used = sorted({k for _, _, sh in top for k in sh})
    r["net"] = {"total": len(nb),
        "links": [dict(mine[k], id=k, films_in_100=count[k] - 1, fear=VOCAB.get(mine[k].get("dim"), {}).get(mine[k]["label"]) if mine[k]["type"] == "element" else mine[k]["label"] if mine[k]["type"] == "archetype" else None, primed=mine[k]["type"] == "element" and primed(mine[k]["label"]),
                       all=[o for o in ids if o != fid and k in FE[o]]) for k in used],
        "films": [{"id": o, "score": round(sc, 2), "via": sh} for sc, o, sh in top]}
    json.dump(r, open(f"{OUT}/data/{fid}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    allnb[fid] = nb
pos = {fid: i for i, fid in enumerate(ids)}
IX = json.load(open(f"{OUT}/index.json"))
# per-film data bundled 25 to a file (data/pack-N.json), so the published page stays within the host's file limit
PACK = 25
for n in range(0, len(ids), PACK):
    json.dump({fid: json.load(open(f"{OUT}/data/{fid}.json")) for fid in ids[n:n + PACK]}, open(f"{OUT}/data/pack-{n // PACK}.json", "w"), ensure_ascii=False, separators=(",", ":"))
IX["pack"] = PACK
# fears as graph nodes: each chosen film's grouped fears, from patterns.json (run tools/build_patterns.py first)
if os.path.exists(f"{OUT}/patterns.json"):
    P = json.load(open(f"{OUT}/patterns.json")); fl = {}; ff = {}
    for f in P["films"]:
        if f["id"] in pos:
            ff[pos[f["id"]]] = [fl.setdefault(f"{d}|{x}", len(fl)) for d in P["dims"] for x in f["g"].get(d, {}).get("f", []) if x != "unclear"]
    # a short description for each fear: the first sentence of its written narration, links stripped (else its definition)
    def blurb(d, x):
        t = (P.get("notes", {}).get(d, {}) or {}).get(x) or ""
        t = re.sub(r"\[([^\]|]+)\|[^\]]+\]", r"\1", t).strip()
        m = re.match(r"(.+?[.])(\s|$)", t)
        return m.group(1) if m else t
    IX["fears"] = [[k.split("|", 1)[0], k.split("|", 1)[1], P["fears"][k.split("|", 1)[0]].get(k.split("|", 1)[1], ""), blurb(*k.split("|", 1))] for k in sorted(fl, key=fl.get)]
    IX["ff"] = [ff.get(i, []) for i in range(len(ids))]
    nm = {f["id"]: f["g"]["nightmares"]["f"][0] for f in P["films"] if "nightmares" in f["g"]}
    IX["nm"] = [nm.get(fid, "") for fid in ids]   # each film's nightmare, for its page
json.dump(IX, open(f"{OUT}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
# assemble the page: the index is embedded so the ledger works before any film loads
page = open("record/template.html").read().replace("__INDEX__", open(f"{OUT}/index.json").read().replace("</", "<\\/"))
import base64
_au = open("record/author.jpg", "rb").read() if os.path.exists("record/author.jpg") else b""
if _au.startswith(b"version https://git-lfs"): _au = b""   # a Git LFS pointer, not the picture (LFS not fetched)
page = page.replace("__AUTHOR__", base64.b64encode(_au).decode())
_fp = open("record/film-poster.jpg", "rb").read() if os.path.exists("record/film-poster.jpg") else b""   # the launch film's poster frame, for the How Bloodline works section
if _fp.startswith(b"version https://git-lfs"): _fp = b""
page = page.replace("__FILMPOSTER__", base64.b64encode(_fp).decode())
open(f"{OUT}/bloodline-record.html", "w").write(page)
open(f"{OUT}/index.html", "w").write('<!doctype html>\n<html lang="en">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page)   # the same page as the site root, for static hosts such as Vercel
os.remove(f"{OUT}/index.json")   # only needed while building; it is embedded in the page
