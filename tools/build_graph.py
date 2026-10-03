# Generates graph/nodes.csv and graph/edges.csv from the film folders. Never edit graph/ by hand.
import json, glob, os, csv, re, collections
FAM=[("deer","the deer on the road"),("well","water, wells and drowning"),("water","water, wells and drowning"),("drown","water, wells and drowning"),("swamp","water, wells and drowning"),
 ("mother","the dead or dangerous mother"),("grandmother","the dead or dangerous mother"),("séance","invitation to the dead"),("spirit board","invitation to the dead"),("invitation","invitation to the dead"),
 ("ship","the vessel"),("train","the vessel"),("vessel","the vessel"),("trap","the house that traps"),("siege","the house that traps"),("welcomes","the house that traps"),("carriage","the house that traps"),("house opposite","the house that traps"),
 ("long black hair","the woman in white with long hair"),("returns","the woman who returns"),("pregnant","pregnancy and birth"),("womb","pregnancy and birth"),
 ("book","forbidden text"),("media","cursed media"),("copy","cursed media"),("gold","greed and gold"),("money","greed and gold"),("coven","the coven"),("decapitation","the head"),("head","the head"),
 ("doll","dolls and miniatures"),("miniatures","dolls and miniatures"),("taxidermy","the preserved dead"),("plague","contagion"),("rises","the dead rise"),("history","history's crime returns"),("maid","the servant who knows"),("staff","the servant who knows")]
def fam(m):
    m=m.lower(); return sorted({f for k,f in FAM if k in m}) or [m]
N={}; E=[]
def node(i,typ,label,**a): N.setdefault(i,{"id":i,"type":typ,"label":label or i,**a})
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
idx={r["id"]:r for r in csv.DictReader(open("films.csv"))}
for d in sorted(glob.glob("films/*/")):
    fid=d.rstrip("/").split("/")[-1]
    if not os.path.exists(d+"wikidata.json"): continue
    wd=json.load(open(d+"wikidata.json")); st=json.load(open(d+"story.json")) if os.path.exists(d+"story.json") else {"archetypes":[],"motifs":[],"lineage":[]}
    wp=json.load(open(d+"wikipedia.json")) if os.path.exists(d+"wikipedia.json") else {}
    sc=json.load(open(d+"scares.json")) if os.path.exists(d+"scares.json") else {}
    vm=json.load(open(d+"visuals/measures.json")) if os.path.exists(d+"visuals/measures.json") else {}
    vs=json.load(open(d+"visuals/stills.json")) if os.path.exists(d+"visuals/stills.json") else {}
    ss=json.load(open(d+"script/stats.json")) if os.path.exists(d+"script/stats.json") else {}
    if os.path.exists(d+"corrections.json"):
        for c in json.load(open(d+"corrections.json")).get("remove",[]):
            wd[c["field"]]=[x for x in wd.get(c["field"],[]) if x["name"]!=c["name"]]
    dm=json.load(open(d+"dialogue/measures.json"))["by_language"].get("en",{}) if os.path.exists(d+"dialogue/measures.json") else {}
    r=idx[fid]
    node(fid,"film",r["title"],year=r["year"],country=r["country"],region=r["region"],duration_min=wd.get("duration_min"),
         wikipedia_languages=len(wp.get("wikipedia_languages",wd.get("wikipedia_languages",[]))),jump_scares=len(sc.get("scares",[])) if sc else "",jump_rating=sc.get("rating","") if sc else "",
         first_scare_min=round(sc["scares"][0]["seconds"]/60,1) if sc.get("scares") else "",
         brightness=vm.get("brightness_mean",vs.get("brightness_mean","")),saturation=vm.get("saturation_mean",vs.get("saturation_mean","")),
         avg_shot_length_s=vm.get("average_shot_length_s",""),script_night_share=ss.get("night_share",""),script_interior_share=round(ss["interior"]/ss["scene_headings"],2) if ss and ss.get("scene_headings") else "",
         imdb=wd.get("imdb_id",""),words_per_minute=dm.get("words_per_minute",""),dialogue_share=dm.get("share_of_runtime_with_dialogue",""),longest_silence_s=(dm.get("longest_silences") or [{}])[0].get("seconds",""),tmdb=wd.get("tmdb_id",""),wikidata=wd["wikidata_qid"])
    for key,rel,typ in [("directors","directed_by","person"),("screenwriters","written_by","person"),("cinematographers","shot_by","person"),("composers","scored_by","person"),("editors","edited_by","person"),("countries","from_country","country"),("original_languages","in_language","language"),("production_companies","made_by","company")]:
        for x in wd.get(key,[]):
            node(x["id"],typ,x["name"]); E.append((fid,x["id"],rel,"Wikidata","sourced"))
    for x in wd.get("cast",[])[:6]:
        node(x["id"],"person",x["name"]); E.append((fid,x["id"],"stars","Wikidata","sourced"))
    if not st["archetypes"]:
        NM={"WOM":"The Woman Who Comes Back","HOU":"The House Remembers","CUR":"The Inherited Curse","OBJ":"The Thing You Took Home","POS":"The Voice Inside","BAR":"The Bargain","CHI":"The Wrong Child","MOT":"The Devouring Mother","DOU":"The Double","BEA":"The Beast Within","FEE":"The One Who Feeds","REV":"The Dead Won't Stay Dead","BOO":"The Book You Shouldn't Read","INV":"You Invited It In","HOS":"The Bad Host","SAC":"The Village Needs Blood","HUN":"The Hunger","OUT":"The Thing Outside","PAT":"Stray From the Path","MAD":"The Thing We Made","BOD":"The Body Betrays","CON":"The Contagion","WIT":"The Witch at the Edge of the Woods","CAS":"Nobody Believes Her","DES":"The Descent","RUL":"The Rule","LOO":"The Endless Night"}
        st["archetypes"]=[{"name":NM[c],"role":role} for c,role in ((r["archetype_primary"],"primary"),(r["archetype_secondary"],"secondary")) if c]
    for a in st["archetypes"]:
        aid="arch-"+slug(a["name"]); node(aid,"archetype",a["name"]); E.append((fid,aid,"carries_archetype",a["role"],"first pass"))
    for m in st["motifs"]:
        for f in fam(m["motif"]):
            mid="motif-"+slug(f); node(mid,"motif",f); E.append((fid,mid,"has_motif",m["motif"],m["confidence"]))
    for l in st["lineage"]:
        sid="src-"+slug(l["target"]); node(sid,"source",l["target"]); E.append((sid,fid,l["relation"],l["source"] or l["evidence"],l["confidence"]))
os.makedirs("graph",exist_ok=True)
cols=sorted({k for n in N.values() for k in n},key=lambda k:(k not in("id","type","label"),k))
with open("graph/nodes.csv","w",newline="") as f:
    w=csv.DictWriter(f,cols); w.writeheader(); [w.writerow(n) for n in N.values()]
with open("graph/edges.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["from","to","type","detail","confidence"]); w.writerows(E)
c=collections.Counter(n["type"] for n in N.values()); print("nodes",len(N),dict(c),"edges",len(E))
# shared nodes: anything linked to 2+ films
deg=collections.defaultdict(set)
for a,b,t,_,_ in E:
    for x,y in ((a,b),(b,a)):
        if N.get(x,{}).get("type")=="film" and N[y]["type"]!="film": deg[y].add(x)
shared=sorted(((len(v),N[k]["type"],N[k]["label"],sorted(N[f]["label"] for f in v)) for k,v in deg.items() if len(v)>1),reverse=True)
json.dump([dict(films=n,type=t,label=l,members=m) for n,t,l,m in shared],open("graph/shared_nodes.json","w"),indent=1,ensure_ascii=False)
for s in shared: print(s)
