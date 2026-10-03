# Medians by era across the corpus: dialogue density, silence, scare timing, runtime.
import csv,json,os,statistics as st,collections
rows=list(csv.DictReader(open("films.csv")))
def era(y): y=int(y); return "pre-1960" if y<1960 else "1960-79" if y<1980 else "1980-99" if y<2000 else "2000-14" if y<2015 else "2015-25"
def num(v):
    if isinstance(v,list): v=v[0]
    if isinstance(v,dict): v=v.get("amount")
    try: return float(v)
    except Exception: return None
E=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rows:
    d=f"films/{r['id']}"; e=era(r["year"])
    if os.path.exists(d+"/dialogue/measures.json"):
        s=json.load(open(d+"/dialogue/measures.json"))["by_language"].get("en",{})
        if s.get("found") and s.get("quality")=="good":
            E[e]["wpm"].append(s["words_per_minute"]); E[e]["dshare"].append(s["share_of_runtime_with_dialogue"]); E[e]["silence"].append(s["longest_silences"][0]["seconds"])
    if os.path.exists(d+"/scares.json"):
        sc=json.load(open(d+"/scares.json"))["scares"]
        if sc: E[e]["first"].append(sc[0]["seconds"]/60); E[e]["n"].append(len(sc))
    if os.path.exists(d+"/wikidata.json"):
        rt=num(json.load(open(d+"/wikidata.json")).get("duration_min"))
        if rt and 40<rt<240: E[e]["runtime"].append(rt)
out=[]
for e in ["pre-1960","1960-79","1980-99","2000-14","2015-25"]:
    x=E[e]; md=lambda k: round(st.median(x[k]),1) if x[k] else None
    row=dict(era=e,films_with_good_subs=len(x["wpm"]),words_per_min=md("wpm"),share_with_dialogue=md("dshare"),longest_silence_s=md("silence"),films_with_scare_data=len(x["first"]),first_scare_min=md("first"),scares_per_film=md("n"),runtime_min=md("runtime"))
    out.append(row); print(row)
json.dump(out,open("reports/eras.json","w"),indent=1)
