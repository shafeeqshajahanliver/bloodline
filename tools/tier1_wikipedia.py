from common import *
import re
q=json.load(open("tools/qids.json"))
NATIVE={"1922-nosferatu":"de","1998-ringu":"ja","2004-pontianak-harum-sundal-malam":"ms","2016-train-to-busan":"ko","2018-tumbbad":"hi","2019-la-llorona":"es"}
def sitelinks(qid):
    for i in range(6):
        r=S.get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",timeout=60)
        if r.status_code==200: return r.json()["entities"][qid].get("sitelinks",{})
        time.sleep(8*(i+1))
    return {}
def extract(lang,title):
    d=get_json(f"https://{lang}.wikipedia.org/w/api.php",params=dict(action="query",prop="extracts|revisions",rvprop="ids|timestamp",explaintext=1,titles=title,redirects=1,format="json"))
    p=list(d["query"]["pages"].values())[0]
    return p.get("extract",""), p.get("revisions",[{}])[0]
def sections(text):
    out={}; cur="Lead"; buf=[]
    for line in text.split("\n"):
        m=re.match(r"^(=+)\s*(.*?)\s*=+$",line)
        if m and len(m.group(1))==2:
            out[cur]="\n".join(buf).strip(); cur=m.group(2); buf=[]
        else: buf.append(line)
    out[cur]="\n".join(buf).strip(); return out
summary={}
for fid,v in q.items():
    d=fdir(fid); sl=sitelinks(v["qid"]); time.sleep(1)
    langs={"en":v["wikipedia_title"]}
    n=NATIVE.get(fid)
    if n and f"{n}wiki" in sl: langs[n]=sl[f"{n}wiki"]["title"]
    meta={"wikipedia_languages":sorted(k[:-4] for k in sl if k.endswith("wiki") and k not in("commonswiki","specieswiki")),"articles":[]}
    for lang,title in langs.items():
        txt,rev=extract(lang,title); secs=sections(txt)
        url=f"https://{lang}.wikipedia.org/wiki/{title.replace(' ','_')}"
        with open(f"{d}/wikipedia.{lang}.md","w") as f:
            f.write(f"# {title}\n\nSource: {url} (revision {rev.get('revid')}, {rev.get('timestamp')}). Text CC BY-SA 4.0, retrieved {today()}.\n\n")
            for k,s in secs.items():
                if s: f.write(f"## {k}\n\n{s}\n\n")
        meta["articles"].append({"lang":lang,"title":title,"url":url,"revision":rev.get("revid"),"sections":list(k for k,s in secs.items() if s),"words":len(txt.split())})
        time.sleep(1)
    json.dump(meta,open(f"{d}/wikipedia.json","w"),indent=1,ensure_ascii=False)
    summary[fid]=[(a["lang"],a["words"],[s for s in a["sections"] if s in("Plot","Synopsis","Themes","Production","Release","Reception","Legacy")]) for a in meta["articles"]]+[len(meta["wikipedia_languages"])]
    print(fid,summary[fid])
