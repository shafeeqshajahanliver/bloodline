# Resolve every film in films.csv to Wikidata + IMDb IDs in bulk via the Wikidata query service.
# Matches English label or alias, requires a film item, and a release year within 1 year of ours.
import csv, json, time, re
from common import S
rows=list(csv.DictReader(open("films.csv")))
def variants(t):
    v={t}; m=re.match(r"(.*?)\s*\((.*?)\)$",t)
    if m: v|={m.group(1),m.group(2)}
    v|={x.replace("'","’") for x in list(v)}|{x.replace("’","'") for x in list(v)}
    return v
lab={}
for r in rows:
    for v in variants(r["title"]): lab.setdefault(v,[]).append(r)
labels=sorted(lab)
Q='''SELECT ?f ?l ?imdb ?y ?wp WHERE {{ VALUES ?l {{ {vals} }}
 {{ ?f rdfs:label ?l }} UNION {{ ?f skos:altLabel ?l }}
 ?f wdt:P31 ?t. VALUES ?t {{ wd:Q11424 wd:Q202866 wd:Q506240 wd:Q24862 wd:Q93204 wd:Q29168811 }}
 OPTIONAL {{ ?f wdt:P577 ?d. BIND(YEAR(?d) AS ?y) }} OPTIONAL {{ ?f wdt:P345 ?imdb }}
 OPTIONAL {{ ?wp schema:about ?f; schema:isPartOf <https://en.wikipedia.org/> }} }}'''
hits={}
for i in range(0,len(labels),40):
    vals=" ".join(json.dumps(x,ensure_ascii=False)+"@en" for x in labels[i:i+40])
    for k in range(6):
        try:
            r=S.get("https://query.wikidata.org/sparql",params={"query":Q.format(vals=vals),"format":"json"},timeout=120)
            b=r.json()["results"]["bindings"]; break
        except Exception: time.sleep(10*(k+1))
    for x in b:
        hits.setdefault(x["l"]["value"],[]).append({"qid":x["f"]["value"].rsplit("/",1)[1],"imdb":x.get("imdb",{}).get("value"),"year":int(x["y"]["value"]) if "y" in x else None,"wp":x.get("wp",{}).get("value")})
    time.sleep(1.5)
out={}; ok=0
for r in rows:
    cands=[h for v in variants(r["title"]) for h in hits.get(v,[]) if h["year"] and abs(h["year"]-int(r["year"]))<=1]
    byq={}
    for h in cands: byq.setdefault(h["qid"],h)
    import urllib.parse
    C={"US":"American","UK":"British","Spain":"Spanish","Mexico":"Mexican","South Korea":"South Korean","India":"Indian"}
    def score(h):
        wt=urllib.parse.unquote(h["wp"].rsplit("/",1)[1]) if h["wp"] else ""
        return (-(wt!="") , -(r["year"] in wt), -(C.get(r["country"],"~") in wt), abs(h["year"]-int(r["year"])), h["imdb"] is None)
    best=sorted(byq.values(),key=score)
    out[r["id"]]={"match":best[0] if best else None,"alternatives":best[1:3]}
    ok+=bool(best)
# Manual matches (checked by hand) override the automatic ones
import os
if os.path.exists("tools/ids_manual.json"):
    for k,v in json.load(open("tools/ids_manual.json")).items():
        if v.get("match"): out[k]={"match":v["match"],"alternatives":[]}
json.dump(out,open("tools/ids.json","w"),indent=1,ensure_ascii=False)
print("matched",ok,"of",len(rows),"with imdb",sum(1 for v in out.values() if v["match"] and v["match"]["imdb"]))
print("ambiguous",sum(1 for v in out.values() if v["alternatives"]))
print("unmatched:",[r["title"]+" ("+r["year"]+")" for r in rows if not out[r["id"]]["match"]])
