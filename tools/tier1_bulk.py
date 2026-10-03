import json, os, time, csv
import run_batch as rb
from common import S, today
rows=list(csv.DictReader(open("films.csv"))); ids=json.load(open("tools/ids.json"))
todo=[(r["id"],ids[r["id"]]["match"]) for r in rows if ids.get(r["id"],{}).get("match") and not os.path.exists(f"films/{r['id']}/wikidata.json")]
print("todo",len(todo))
def getents(qs):
    out={}
    for q in qs:
        for k in range(5):
            r=S.get(f"https://www.wikidata.org/wiki/Special:EntityData/{q}.json",timeout=60)
            if r.status_code==200:
                e=r.json()["entities"]; out[q]=e.get(q) or list(e.values())[0]; break
            time.sleep(5*(k+1))
    return out
for i in range(0,len(todo),25):
    chunk=todo[i:i+25]; ents=getents([m["qid"] for _,m in chunk])
    refs=[x["mainsnak"]["datavalue"]["value"]["id"] for e in ents.values() for p in rb.P for x in e.get("claims",{}).get(p,[]) if isinstance(x["mainsnak"].get("datavalue",{}).get("value"),dict) and "id" in x["mainsnak"]["datavalue"]["value"]]
    rb.labels(sorted(set(refs)))
    for fid,m in chunk:
        e=ents.get(m["qid"]); 
        if not e: continue
        c=e["claims"]; d=f"films/{fid}"; os.makedirs(d,exist_ok=True)
        rec={"wikidata_qid":e["id"],"wikidata_url":f"https://www.wikidata.org/wiki/{e['id']}","wikipedia_url":m.get("wp"),"wikipedia_languages":sorted(k[:-4] for k in e.get("sitelinks",{}) if k.endswith("wiki") and k not in("commonswiki","specieswiki"))}
        for p,n in rb.P.items():
            v=[{"id":x["mainsnak"]["datavalue"]["value"]["id"],"name":rb.LABELS.get(x["mainsnak"]["datavalue"]["value"]["id"])} for x in c.get(p,[]) if isinstance(x["mainsnak"].get("datavalue",{}).get("value"),dict) and "id" in x["mainsnak"]["datavalue"]["value"]]
            if v: rec[n]=v
        for p,n in rb.SC.items():
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
    print(i+len(chunk),"done",flush=True); time.sleep(2)
