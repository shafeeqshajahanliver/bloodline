# Coverage report across all 500 films, by source and by region.
import csv, json, os, collections, datetime
rows=list(csv.DictReader(open("films.csv"))); ids=json.load(open("tools/ids.json"))
def has(fid):
    d=f"films/{fid}"; ex=lambda p: os.path.exists(f"{d}/{p}")
    subs={}
    if ex("dialogue/measures.json"):
        for l,s in json.load(open(f"{d}/dialogue/measures.json"))["by_language"].items():
            if s.get("found"): subs[l]=s.get("quality","?")
    return {"ids":bool(ids.get(fid,{}).get("match")),"facts":ex("wikidata.json"),"subs_en":"en" in subs,"subs_native":any(l!="en" for l in subs),
            "screenplay":ex("script/screenplay.txt"),"scares":ex("scares.json"),"stills":ex("visuals/stills.json"),"full_film":ex("visuals/measures.json"),"story":ex("story.json")}
H=["ids","facts","subs_en","subs_native","screenplay","scares","stills","full_film","story"]
N={"ids":"Matched IDs","facts":"Facts (Wikidata)","subs_en":"English subtitles","subs_native":"Original-language subtitles","screenplay":"Screenplay","scares":"Jump scares","stills":"Stills","full_film":"Full-film visuals","story":"Story layer (archetypes, motifs, lineage)"}
tot=collections.Counter(); reg=collections.defaultdict(collections.Counter); regn=collections.Counter()
per={}
for r in rows:
    h=has(r["id"]); per[r["id"]]=h; regn[r["region"]]+=1
    for k,v in h.items():
        if v: tot[k]+=1; reg[r["region"]][k]+=1
md=f"# Coverage: all 500 films\n\nGenerated {datetime.date.today()}.\n\n| Layer | Films | Share |\n|---|---|---|\n"+"".join(f"| {N[k]} | {tot[k]} | {tot[k]/5:.0f}% |\n" for k in H)
md+="\n## By region (films with each layer / films in region)\n\n| Region | Films | Subtitles (EN) | Screenplay | Jump scares | Stills |\n|---|---|---|---|---|---|\n"
for g,n in regn.most_common(): md+=f"| {g} | {n} | {reg[g]['subs_en']} | {reg[g]['screenplay']} | {reg[g]['scares']} | {reg[g]['stills']} |\n"
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
