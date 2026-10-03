# Wikipedia articles (plot, production, reception...) for every matched film. Resumable.
# English for all; the original-language article too when the English plot is missing or under 150 words.
# Uses index.php?action=raw (wikitext) because the Wikipedia API throttles bulk access; ~1 request per 3 s.
# Usage: python3 tools/tier1_wikipedia_bulk.py [film ids]
import json, os, re, sys, time, urllib.parse
import mwparserfromhell
from common import S, today
UA = "BloodlineResearch/0.2 (https://github.com/shafeeqshajahanliver/bloodline; non-commercial film research)"
H = {"User-Agent": UA}
LANG = {"Spanish":"es","Japanese":"ja","Italian":"it","French":"fr","Korean":"ko","Hindi":"hi","German":"de","Indonesian":"id","Malay":"ms","Standard Malay":"ms",
        "Thai":"th","Norwegian":"no","Mandarin":"zh","Standard Chinese":"zh","Chinese":"zh","Standard Taiwanese Mandarin":"zh","Cantonese":"zh-yue","Malayalam":"ml",
        "Swedish":"sv","Portuguese":"pt","Brazilian Portuguese":"pt","Turkish":"tr","Czech":"cs","Persian":"fa","Finnish":"fi","Arabic":"ar","Polish":"pl","Russian":"ru",
        "Alavese Basque":"eu","Wolof":"wo","Vietnamese":"vi","Xhosa":"xh","Icelandic":"is","Tagalog":"tl","Tamil":"ta","Danish":"da","Dutch":"nl","Hungarian":"hu"}
PLOT = re.compile(r"^(plot|synopsis|story|plot summary|summary|premise|storyline|sinopsis|plot synopsis)$", re.I)
WAIT = 3.0

def get(url, **kw):
    for k in range(6):
        r = S.get(url, headers=H, timeout=60, **kw)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("retry-after", 20)) + 5); continue
        time.sleep(WAIT); return r
    return r

def sitelinks(qid):
    r = get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
    e = r.json()["entities"]; e = e.get(qid) or list(e.values())[0]
    return {k[:-4].replace("_", "-"): v["title"] for k, v in e.get("sitelinks", {}).items() if k.endswith("wiki") and k not in ("commonswiki", "specieswiki")}

def raw(lang, title):
    for _ in range(3):  # follow redirects
        r = get(f"https://{lang}.wikipedia.org/w/index.php", params={"title": title, "action": "raw"})
        if r.status_code != 200: return None, None, title
        m = re.match(r"\s*#(?:REDIRECT|ALIH|WEITERLEITUNG|REDIRECCIÓN|REDIRECTION|RINVIA|転送|넘겨주기)\s*\[\[([^\]|#]+)", r.text, re.I)
        if not m: return r.text, r.headers.get("last-modified"), title
        title = m.group(1).strip()
    return None, None, title

def clean(wikitext):
    code = mwparserfromhell.parse(wikitext)
    for t in code.filter_tags(recursive=True):
        if str(t.tag).lower() in ("ref", "gallery", "table") and t in code: code.remove(t)
    for f in code.filter_wikilinks(recursive=True):
        if re.match(r"(file|image|category|fail|berkas|kategori|fichier|archivo|datei|ファイル|파일):", str(f.title), re.I) and f in code: code.remove(f)
    txt = code.strip_code(normalize=True, collapse=True)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return "\n".join(l.strip() for l in txt.split("\n")).strip()

def sections(wikitext):
    out, cur, buf = {}, "Lead", []
    for line in wikitext.split("\n"):
        m = re.match(r"^==\s*([^=].*?)\s*==\s*$", line)
        if m: out[cur] = "\n".join(buf); cur = clean(m.group(1)) or m.group(1); buf = []
        else: buf.append(line)
    out[cur] = "\n".join(buf)
    return {k: clean(v) for k, v in out.items()}

def save(fid, lang, title, lastmod, secs):
    url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
    with open(f"films/{fid}/wikipedia.{lang}.md", "w") as f:
        f.write(f"# {title}\n\nSource: {url} (last edited {lastmod}). Text CC BY-SA 4.0, retrieved {today()}.\n\n")
        for k, s in secs.items():
            if s and not re.match(r"^(references|external links|see also|notes|further reading|bibliography|rujukan|pautan luar|referensi|catatan)$", k, re.I):
                f.write(f"## {k}\n\n{s}\n\n")
    plot = next((k for k in secs if PLOT.match(k)), None)
    return {"lang": lang, "title": title, "url": url, "last_edited": lastmod, "sections": [k for k, s in secs.items() if s],
            "plot_section": plot, "plot_words": len(secs[plot].split()) if plot else 0, "words": sum(len(s.split()) for s in secs.values())}

def film(fid):
    d = f"films/{fid}"
    if os.path.exists(f"{d}/wikipedia.json") or os.path.exists(f"{d}/wikipedia.none"): return "skip"
    wd = json.load(open(f"{d}/wikidata.json"))
    sl = sitelinks(wd["wikidata_qid"])
    langs = [l for l in ["en"] if l in sl]
    orig = [LANG.get(x["name"]) for x in wd.get("original_languages", [])]
    native = next((l for l in orig if l and l != "en" and l in sl), None)
    meta = {"wikipedia_languages": sorted(sl), "articles": [], "source": "Wikipedia (CC BY-SA 4.0)", "retrieved": today()}
    for lang in langs + ([native] if native else []):
        if lang != "en" and meta["articles"] and meta["articles"][0]["plot_words"] >= 150: break
        text, lastmod, title = raw(lang, sl[lang])
        if text: meta["articles"].append(save(fid, lang, title, lastmod, sections(text)))
    if not meta["articles"]:
        open(f"{d}/wikipedia.none", "w").write(today()); return "none"
    json.dump(meta, open(f"{d}/wikipedia.json", "w"), indent=1, ensure_ascii=False)
    return [(a["lang"], a["plot_words"]) for a in meta["articles"]]

if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(f for f in os.listdir("films") if os.path.exists(f"films/{f}/wikidata.json"))
    for fid in ids:
        try: print(time.strftime("%H:%M:%S"), fid, film(fid), flush=True)
        except Exception as ex: print(time.strftime("%H:%M:%S"), fid, "ERROR", repr(ex)[:150], flush=True)
