# Coverage report across all 500 films, by source and by region.
import csv, json, os, collections, datetime
rows=list(csv.DictReader(open("films.csv"))); ids=json.load(open("tools/ids.json"))
def plot(fid):
    p=f"films/{fid}/wikipedia.json"
    return os.path.exists(p) and any(a.get("plot_words",0)>0 or "Plot" in a.get("sections",[]) for a in json.load(open(p))["articles"])
def has(fid):
    d=f"films/{fid}"; ex=lambda p: os.path.exists(f"{d}/{p}")
    subs={}
    if ex("dialogue/measures.json"):
        for l,s in json.load(open(f"{d}/dialogue/measures.json"))["by_language"].items():
            if s.get("found"): subs[l]=s.get("quality","?")
    return {"ids":bool(ids.get(fid,{}).get("match")),"facts":ex("wikidata.json"),"subs_en":"en" in subs,"subs_native":any(l!="en" for l in subs),
            "screenplay":ex("script/screenplay.txt"),"scares":ex("scares.json"),"stills":ex("visuals/stills.json"),"full_film":ex("visuals/measures.json"),"plot":plot(fid),"story":ex("story_elements.json")}
H=["ids","facts","plot","subs_en","subs_native","screenplay","scares","stills","full_film","story"]
N={"ids":"Matched IDs","facts":"Facts (Wikidata)","plot":"Plot summary (Wikipedia)","subs_en":"English subtitles","subs_native":"Original-language subtitles","screenplay":"Screenplay","scares":"Jump scares","stills":"Stills","full_film":"Full-film visuals","story":"Story elements (bottom-up, quoted)"}
tot=collections.Counter(); reg=collections.defaultdict(collections.Counter); regn=collections.Counter()
per={}
for r in rows:
    h=has(r["id"]); per[r["id"]]=h; regn[r["region"]]+=1
    for k,v in h.items():
        if v: tot[k]+=1; reg[r["region"]][k]+=1
md=f"# Coverage: all 500 films\n\nGenerated {datetime.date.today()}.\n\n| Layer | Films | Share |\n|---|---|---|\n"+"".join(f"| {N[k]} | {tot[k]} | {tot[k]/5:.0f}% |\n" for k in H)
md+="\n## By region (films with each layer / films in region)\n\n| Region | Films | Plot | Story elements | Subtitles (EN) | Screenplay | Jump scares | Stills |\n|---|---|---|---|---|---|---|---|\n"
for g,n in regn.most_common(): md+=f"| {g} | {n} | {reg[g]['plot']} | {reg[g]['story']} | {reg[g]['subs_en']} | {reg[g]['screenplay']} | {reg[g]['scares']} | {reg[g]['stills']} |\n"

# Story elements: one row per dimension
SD=[("threat","Threat"),("origin","Origin of the threat"),("wants","What it wants"),("wrong","The wrong underneath"),("trigger","Trigger"),("rules","Rules"),("who_suffers","Who suffers"),("ending","Ending"),("images","Images"),("beats","Beats")]
sf=collections.Counter(); sn=collections.Counter(); se=collections.Counter(); sv=collections.defaultdict(set); sr=collections.defaultdict(collections.Counter); thin=0; nst=0
for r in rows:
    p=f"films/{r['id']}/story_elements.json"
    if not os.path.exists(p): continue
    d=json.load(open(p)); nst+=1; thin+=d.get("plot_quality")!="full"
    for k,_ in SD:
        es=d.get("dimensions",{}).get(k,[])
        if es: sf[k]+=1; sr[r["region"]][k]+=1
        if k in d.get("not_stated",[]): sn[k]+=1
        se[k]+=len(es); sv[k]|={e["value"] for e in es}
md+=f"\n## Story elements by dimension\n\n{nst} films have story elements ({thin} from a thin plot). Each entry is quoted from the film's Wikipedia article; values are not yet merged, so 'distinct values' overstates variety.\n\n| Dimension | Films filled | Share | Not stated | Entries | Per film | Distinct values |\n|---|---|---|---|---|---|---|\n"
md+="".join(f"| {n} | {sf[k]} | {sf[k]/5:.0f}% | {sn[k]} | {se[k]} | {se[k]/max(1,sf[k]):.1f} | {len(sv[k])} |\n" for k,n in SD)
md+="\n### By region (films with each dimension filled / films in region)\n\n| Region | Films | "+" | ".join(n for _,n in SD)+" |\n|---|---|"+"---|"*len(SD)+"\n"
for g,n in regn.most_common(): md+=f"| {g} | {n} | "+" | ".join(str(sr[g][k]) for k,_ in SD)+" |\n"
md+="\n## Films with no IDs (need a manual match)\n\n"+"".join(f"- {r['title']} ({r['year']})\n" for r in rows if not per[r['id']]['ids'])
open("reports/coverage.md","w").write(md)
# write status back into films.csv
for r in rows:
    h=per[r["id"]]; r["status"]="; ".join(k for k in H if h[k]) or "not started"
    m=ids.get(r["id"],{}).get("match") or {}
    r["wikidata"]=m.get("qid",""); r["imdb"]=m.get("imdb","")
cols=["id","title","year","country","region","archetype_primary","archetype_secondary","pilot","wikidata","imdb","status"]
with open("films.csv","w",newline="") as f:
    w=csv.DictWriter(f,cols,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
print(md[:2500])
