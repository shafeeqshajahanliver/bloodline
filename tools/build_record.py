# Build the release-1 record (the private Bloodline Record page) for the films listed in record/films.json:
# one JSON per film, one still sheet per film, and the page with the index embedded. Output goes to record/site/ (gitignored).
import csv, glob, json, os, re, sys
from PIL import Image
sys.path.insert(0, "tools")
from sources import unusable
OUT = "record/site"
os.makedirs(OUT + "/data", exist_ok=True); os.makedirs(OUT + "/stills", exist_ok=True)
ids = json.load(open("record/films.json"))
rows = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
arch = {r["code"]: r for r in csv.DictReader(open("archetypes.csv"))}
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

def sheet(fid):
    fs = sorted(glob.glob(f"films/{fid}/visuals/stills/*.jpg"))
    if not fs: return 0, None
    if len(fs) > MAXS: fs = [fs[round(i * (len(fs) - 1) / (MAXS - 1))] for i in range(MAXS)]
    H = round(W * 9 / 16); ims = []
    for f in fs:
        try:
            im = Image.open(f).convert("RGB")
        except Exception: continue
        # cover-crop to 16:9
        r = im.width / im.height
        if r > 16 / 9: nw = round(im.height * 16 / 9); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else: nh = round(im.width * 9 / 16); im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
        ims.append(im.resize((W, H), Image.LANCZOS))
    if not ims: return 0, None
    S = Image.new("RGB", (W, H * len(ims)))
    for i, im in enumerate(ims): S.paste(im, (0, i * H))
    S.save(f"{OUT}/stills/{fid}.jpg", quality=74, optimize=True, progressive=True)
    src = json.load(open(f"films/{fid}/visuals/stills.json")) if os.path.exists(f"films/{fid}/visuals/stills.json") else {}
    return len(ims), src.get("source")

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
    nst, stsrc = sheet(fid)
    dims = {k: se["dimensions"].get(k, []) for k in DIMS}
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
        "stills": nst, "stills_source": stsrc,
        "unusable": corr.get("unusable_sources", []), "removed": corr.get("remove", []),
    }
    json.dump(rec, open(f"{OUT}/data/{fid}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    # index row: enough to search and filter without loading the film
    vals = sorted({e["value"] for k in DIMS for e in dims[k]})
    index.append({"id": fid, "t": r["title"], "y": int(r["year"]), "c": r["country"], "r": r["region"], "a": rec["arch"],
                  "dir": rec["directors"][:2], "cast": rec["cast"][:6], "f": filled, "ns": rec["not_stated"],
                  "n": sum(len(dims[k]) for k in DIMS), "st": nst, "sub": "en" in dia, "osub": any(l != "en" for l in dia),
                  "sp": bool(sp), "sc": bool(sc), "pl": bool(pilot), "pq": rec["plot_quality"],
                  "v": vals, "lede": (dims["threat"][0]["value"] if dims["threat"] else "")})
json.dump({"films": index, "arch": {k: {"name": v["name"], "beat": v["beat"], "roots": v["roots"], "status": v["status"]} for k, v in arch.items()}},
          open(f"{OUT}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(index), "films;", sum(1 for x in index if x["st"]), "with stills")
# assemble the page: the index is embedded so the ledger works before any film loads
page = open("record/template.html").read().replace("__INDEX__", open(f"{OUT}/index.json").read().replace("</", "<\\/"))
open(f"{OUT}/bloodline-record.html", "w").write(page)
