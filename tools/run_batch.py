# Automated collection for every film in films.csv. Resumable: skips anything already collected.
# Usage: python3 tools/run_batch.py [--limit N] [--only tier1,subs,scares,scripts,stills]
import csv, json, os, re, sys, time, html, subprocess
from common import S, today
import opus
sys.argv += [] ; args=" ".join(sys.argv[1:])
LIMIT=int(re.search(r"--limit (\d+)",args).group(1)) if "--limit" in args else 10**6
ONLY=set(re.search(r"--only (\S+)",args).group(1).split(",")) if "--only" in args else {"tier1","subs","scares","scripts","stills"}
rows=list(csv.DictReader(open("films.csv"))); ids=json.load(open("tools/ids.json"))
log=open("reports/batch.log","a")
def L(*a):
    s=time.strftime("%H:%M:%S ")+" ".join(map(str,a)); print(s,flush=True); log.write(s+"\n"); log.flush()
def slug(t): return re.sub(r"[^a-z0-9]+","-",t.lower().replace("'","")).strip("-")
P={"P57":"directors","P58":"screenwriters","P161":"cast","P344":"cinematographers","P1040":"editors","P86":"composers","P162":"producers","P272":"production_companies","P495":"countries","P364":"original_languages","P136":"genres","P144":"based_on","P4969":"derivative_works","P155":"follows","P156":"followed_by","P179":"series","P921":"main_subjects","P840":"narrative_locations","P915":"filming_locations","P166":"awards","P1411":"nominated_for","P941":"inspired_by","P737":"influenced_by"}
SC={"P2047":"duration_min","P2142":"box_office","P2130":"budget","P345":"imdb_id","P4947":"tmdb_id","P6127":"letterboxd_id","P1258":"rotten_tomatoes_id","P1712":"metacritic_id","P577":"release_dates"}
LABELS={}
def labels(qs):
    qs=[q for q in qs if q not in LABELS]
    for i in range(0,len(qs),200):
        vals=" ".join("wd:"+q for q in qs[i:i+200])
        q=f"SELECT ?i ?l WHERE {{ VALUES ?i {{ {vals} }} ?i rdfs:label ?l FILTER(LANG(?l)='en') }}"
        b=[]
        for k in range(5):
            try:
                b=S.get("https://query.wikidata.org/sparql",params={"query":q,"format":"json"},timeout=120).json()["results"]["bindings"]; break
            except Exception: time.sleep(8*(k+1))
        for x in b: LABELS[x["i"]["value"].rsplit("/",1)[1]]=x["l"]["value"]
def tier1(fid,m):
    d=f"films/{fid}"; os.makedirs(d,exist_ok=True)
    if os.path.exists(d+"/wikidata.json"): return
    for k in range(6):
        r=S.get(f"https://www.wikidata.org/wiki/Special:EntityData/{m['qid']}.json",timeout=60)
        if r.status_code==200: break
        time.sleep(10*(k+1))
    e=r.json()["entities"]; e=e.get(m["qid"]) or list(e.values())[0]; c=e["claims"]
    refs=[x["mainsnak"]["datavalue"]["value"]["id"] for p in P for x in c.get(p,[]) if isinstance(x["mainsnak"].get("datavalue",{}).get("value"),dict) and "id" in x["mainsnak"]["datavalue"]["value"]]
    labels(refs)
    rec={"wikidata_qid":e["id"],"wikidata_url":f"https://www.wikidata.org/wiki/{e['id']}","wikipedia_url":m.get("wp"),"wikipedia_languages":sorted(k[:-4] for k in e.get("sitelinks",{}) if k.endswith("wiki") and k not in("commonswiki","specieswiki"))}
    for p,n in P.items():
        v=[{"id":x["mainsnak"]["datavalue"]["value"]["id"],"name":LABELS.get(x["mainsnak"]["datavalue"]["value"]["id"])} for x in c.get(p,[]) if isinstance(x["mainsnak"].get("datavalue",{}).get("value"),dict) and "id" in x["mainsnak"]["datavalue"]["value"]]
        if v: rec[n]=v
    for p,n in SC.items():
        v=[]
        for x in c.get(p,[]):
            dv=x["mainsnak"].get("datavalue",{}).get("value")
            if isinstance(dv,dict) and "amount" in dv: v.append({"amount":dv["amount"].lstrip("+"),"unit":dv.get("unit","").rsplit("/",1)[-1]})
            elif isinstance(dv,dict) and "time" in dv: v.append(dv["time"][1:11])
            elif dv is not None: v.append(dv)
        if v: rec[n]=v if (len(v)>1 or n in("release_dates","box_office","budget")) else v[0]
    if isinstance(rec.get("duration_min"),dict): rec["duration_min"]=float(rec["duration_min"]["amount"])
    rec.update(retrieved=today(),source="Wikidata (CC0)")
    json.dump(rec,open(d+"/wikidata.json","w"),indent=1,ensure_ascii=False)
def scares(fid,r):
    d=f"films/{fid}"
    if os.path.exists(d+"/scares.json") or os.path.exists(d+"/scares.none"): return
    from bs4 import BeautifulSoup
    for sl in [f"{slug(r['title'])}-{r['year']}",slug(r['title'])]:
        u=f"https://wheresthejump.com/jump-scares-in-{sl}/"; x=S.get(u,timeout=30); time.sleep(1)
        cnt=BeautifulSoup(x.text,"html.parser").select_one(".entry-content") if x.status_code==200 else None
        t=cnt.get_text("\n",strip=True) if cnt else ""
        if "Jump Scare Times" in t and (r["year"] in t or r["title"].lower() in t.lower()):
            items=re.findall(r"(\d\d:\d\d:\d\d)\n–\s*(.+)",t.split("Jump Scare Times",1)[1])
            m=re.search(r"jump scare rating of (\d+(?:\.\d+)?)",t)
            sec=lambda s: sum(int(a)*b for a,b in zip(s.split(":"),(3600,60,1)))
            json.dump({"source":u,"site":"Where's the Jump (crowd-sourced)","retrieved":today(),"rating":float(m.group(1)) if m else None,"scares":[{"time":a,"seconds":sec(a),"description":b} for a,b in items]},open(d+"/scares.json","w"),indent=1,ensure_ascii=False)
            return
    open(d+"/scares.none","w").write(today())
def scripts(fid,r):
    d=f"films/{fid}/script"
    if os.path.exists(d+"/screenplay.txt") or os.path.exists(d+"/none"): return
    os.makedirs(d,exist_ok=True)
    s=f"{slug(r['title'])}-{r['year']}"; x=S.get(f"https://www.scriptslug.com/script/{s}",timeout=30); time.sleep(1)
    pdf=re.findall(r'https://assets\.scriptslug\.com/[^"\']+\.pdf',x.text) if x.status_code==200 else []
    if pdf:
        b=S.get(pdf[0],timeout=120).content; open(d+"/screenplay.pdf","wb").write(b)
        subprocess.run(["pdftotext","-layout",d+"/screenplay.pdf",d+"/screenplay.txt"])
        json.dump({"source":f"https://www.scriptslug.com/script/{s}","pdf":pdf[0],"site":"Script Slug","retrieved":today(),"note":"Draft may differ from the final film. Private research use only."},open(d+"/source.json","w"),indent=1)
    else: open(d+"/none","w").write(today())
def stills(fid,r):
    d=f"films/{fid}/visuals"
    if os.path.exists(d+"/stills.json") or os.path.exists(d+"/stills.none"): return
    os.makedirs(d,exist_ok=True)
    from bs4 import BeautifulSoup
    x=S.get("https://film-grab.com/",params={"s":r["title"]},timeout=30); time.sleep(1)
    links=[(a.get_text(strip=True),a["href"]) for a in BeautifulSoup(x.text,"html.parser").select("h2 a, h3 a, .entry-title a")]
    for t,u in links:
        if slug(t).replace("-","")!=slug(r["title"]).replace("-",""): continue
        pg=S.get(u,timeout=30); txt=BeautifulSoup(pg.text,"html.parser").select_one(".entry-content"); txt=txt.get_text(" ",strip=True) if txt else ""
        if f"Year: {r['year']}" in txt or f"Year : {r['year']}" in txt:
            subprocess.run([sys.executable,"tools/tier3_filmgrab.py",fid,u],env={**os.environ,"PYTHONPATH":"tools"},capture_output=True); return
        time.sleep(1)
    open(d+"/stills.none","w").write(today())
def main():
  pass
if __name__=='__main__':
    PART=tuple(map(int,re.search(r"--part (\d+)/(\d+)",args).groups())) if "--part" in args else (0,1)
    done=0
    for i_,r in enumerate(rows):
        if i_%PART[1]!=PART[0]: continue
        m=ids.get(r["id"],{}).get("match")
        if not m: continue
        if done>=LIMIT: break
        fid=r["id"]
        for name,fn in [("tier1",lambda:tier1(fid,m)),("subs",lambda:subprocess.run([sys.executable,"tools/tier2_subtitles.py",fid],env={**os.environ,"PYTHONPATH":"tools"},capture_output=True) if os.path.exists(f"films/{fid}/wikidata.json") and not os.path.exists(f"films/{fid}/dialogue/measures.json") else None),("scares",lambda:scares(fid,r)),("scripts",lambda:scripts(fid,r)),("stills",lambda:stills(fid,r))]:
            if name not in ONLY: continue
            try: fn()
            except Exception as ex: L(fid,name,"ERROR",repr(ex)[:150])
        done+=1; L("done",fid)
    L("batch finished",done)
    