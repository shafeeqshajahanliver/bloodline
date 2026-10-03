from common import *
P={"P57":"directors","P58":"screenwriters","P161":"cast","P344":"cinematographers","P1040":"editors","P86":"composers","P162":"producers","P272":"production_companies","P750":"distributors","P495":"countries","P364":"original_languages","P136":"genres","P144":"based_on","P4969":"derivative_works","P155":"follows","P156":"followed_by","P179":"series","P921":"main_subjects","P840":"narrative_locations","P915":"filming_locations","P166":"awards","P1411":"nominated_for","P5970":"_","P8345":"franchise","P1877":"after_a_work_by","P941":"inspired_by","P737":"influenced_by"}
SCAL={"P2047":"duration_min","P2142":"box_office","P2130":"budget","P345":"imdb_id","P4947":"tmdb_id","P1874":"netflix_id","P1562":"allmovie_id","P6127":"letterboxd_id","P1258":"rotten_tomatoes_id","P1712":"metacritic_id","P577":"release_dates"}
q=json.load(open("tools/qids.json")); raw={}
for fid,v in q.items():
    for i in range(6):
        r=S.get(f"https://www.wikidata.org/wiki/Special:EntityData/{v['qid']}.json",timeout=60)
        if r.status_code==200: break
        time.sleep(8*(i+1))
    raw[fid]=r.json()["entities"][v["qid"]]; print(fid,"ok"); time.sleep(2)
# collect referenced ids
ref=set()
for e in raw.values():
    for p in P:
        for c in e["claims"].get(p,[]):
            dv=c["mainsnak"].get("datavalue",{}).get("value")
            if isinstance(dv,dict) and "id" in dv: ref.add(dv["id"])
ref=list(ref); labels={}
for i in range(0,len(ref),50):
    for k in range(6):
        r=S.get("https://www.wikidata.org/w/api.php",params=dict(action="wbgetentities",ids="|".join(ref[i:i+50]),props="labels",languages="en",format="json"),timeout=60)
        try: d=r.json()["entities"]; break
        except Exception: time.sleep(8*(k+1))
    for k,v in d.items(): labels[k]=v.get("labels",{}).get("en",{}).get("value",k)
    time.sleep(2)
for fid,e in raw.items():
    c=e["claims"]; rec={"wikidata_qid":e["id"],"wikidata_url":f"https://www.wikidata.org/wiki/{e['id']}","titles":{k:v["value"] for k,v in e.get("labels",{}).items() if k in ("en","ms","ja","ko","hi","es","de","id","mr")}}
    for p,name in P.items():
        if name=="_": continue
        vals=[]
        for x in c.get(p,[]):
            dv=x["mainsnak"].get("datavalue",{}).get("value")
            if isinstance(dv,dict) and "id" in dv: vals.append({"id":dv["id"],"name":labels.get(dv["id"],dv["id"])})
        if vals: rec[name]=vals
    for p,name in SCAL.items():
        vals=[]
        for x in c.get(p,[]):
            dv=x["mainsnak"].get("datavalue",{}).get("value")
            if dv is None: continue
            if isinstance(dv,dict) and "amount" in dv: vals.append({"amount":dv["amount"].lstrip("+"),"unit":dv.get("unit","").rsplit("/",1)[-1]})
            elif isinstance(dv,dict) and "time" in dv: vals.append(dv["time"][1:11])
            else: vals.append(dv)
        if vals: rec[name]=vals if len(vals)>1 or name in("release_dates","box_office","budget") else vals[0]
    if "duration_min" in rec and isinstance(rec["duration_min"],dict): rec["duration_min"]=float(rec["duration_min"]["amount"])
    rec["retrieved"]=today(); rec["source"]="Wikidata (CC0)"
    d=fdir("../films/"+fid) if False else fdir(fid)
    json.dump(rec,open(f"{d}/wikidata.json","w"),indent=1,ensure_ascii=False)
    print(fid, {k:(len(v) if isinstance(v,list) else v) for k,v in rec.items() if k not in("titles",)})
