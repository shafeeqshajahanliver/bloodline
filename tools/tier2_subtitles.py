# Subtitles for each film from the OPUS OpenSubtitles v2024 research corpus (no login needed).
# Picks the file whose length best matches the film's runtime; saves .srt + dialogue measures.
import json, re, os, sys, csv, statistics
import opus
NATIVE={"Japan":"ja","Malaysia":"ms","South Korea":"ko","India":"hi","Guatemala":"es","Mexico":"es","Spain":"es","Indonesia":"id","Thailand":"th","France":"fr","Italy":"it","Germany":"de"}
def parse(xml):
    out=[]; cur=None
    for m in re.finditer(r'<time id="T\d+([SE])" value="([\d:,]+)"\s*/>|<w[^>]*>([^<]*)</w>|<s id',xml):
        if m.group(1)=="S": cur={"start":m.group(2),"words":[]}
        elif m.group(1)=="E" and cur: cur["end"]=m.group(2); out.append(cur); cur=None
        elif m.group(3) is not None and cur is not None: cur["words"].append(m.group(3))
    return out
def secs(t):
    t=t.replace(",",".")
    h,m,s=t.split(":"); return int(h)*3600+int(m)*60+float(s)
def srt_time(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")
def best(lang,imdb,runtime_min):
    ix=opus.index(lang); cands=ix.get(str(int(imdb[2:])),[])
    if not cands: return None
    scored=[]
    for e in sorted(cands,key=lambda e:-e[4])[:4]:
        try: cues=parse(opus.extract(lang,e))
        except Exception: continue
        if len(cues)<50: continue
        end=secs(cues[-1]["end"])/60
        scored.append((abs(end-runtime_min) if runtime_min else 0,e,cues,end))
    if not scored: return None
    scored.sort(key=lambda x:x[0]); return scored[0]+(len(cands),)
def measures(cues,runtime_min):
    st=[(secs(c["start"]),secs(c["end"]),len(c["words"])) for c in cues if c.get("end")]
    total=runtime_min*60 if runtime_min else st[-1][1]
    words=sum(w for _,_,w in st); spoken=sum(max(0,b-a) for a,b,_ in st)
    gaps=[(st[i+1][0]-st[i][1],st[i][1]) for i in range(len(st)-1)]
    longest=sorted(gaps,reverse=True)[:5]
    per_min=[0]*(int(total//60)+1)
    for a,b,w in st:
        if int(a//60)<len(per_min): per_min[int(a//60)]+=w
    return {"lines":len(st),"words":words,"words_per_minute":round(words/(total/60),1),"share_of_runtime_with_dialogue":round(spoken/total,3),
            "first_line_at_s":round(st[0][0]),"longest_silences":[{"seconds":round(g),"starts_at":srt_time(t)} for g,t in longest],
            "words_by_minute":per_min,"quietest_10min_window_start_min":min(range(max(1,len(per_min)-9)),key=lambda i:sum(per_min[i:i+10]))}
idx={r["id"]:r for r in csv.DictReader(open("films.csv"))}
targets=sys.argv[1:] or sorted(d for d in os.listdir("films"))
for fid in targets:
    wd=json.load(open(f"films/{fid}/wikidata.json")); imdb=wd.get("imdb_id"); rt=wd.get("duration_min")
    if not imdb: print(fid,"no IMDb id"); continue
    langs=["en"]; n=NATIVE.get(idx[fid]["country"])
    if n and n!="en": langs.append(n)
    os.makedirs(f"films/{fid}/dialogue",exist_ok=True); summary={}
    for lang in langs:
        try: r=best(lang,imdb,rt)
        except Exception as e: print(fid,lang,"error",e); continue
        if not r: summary[lang]={"found":False}; continue
        diff,e,cues,end,ncands=r
        with open(f"films/{fid}/dialogue/subtitles.{lang}.srt","w") as f:
            for i,c in enumerate(cues,1): f.write(f"{i}\n{c['start']} --> {c.get('end',c['start'])}\n{' '.join(c['words'])}\n\n")
        summary[lang]={"found":True,"candidates":ncands,"chosen":e[0],"ends_at_min":round(end,1),"runtime_min":rt,"runtime_gap_min":round(diff,1),**measures(cues,rt)}
    json.dump({"source":"OPUS OpenSubtitles v2024 (Lison & Tiedemann; opus.nlpl.eu), research corpus","retrieved":__import__('datetime').date.today().isoformat(),"by_language":summary},open(f"films/{fid}/dialogue/measures.json","w"),indent=1,ensure_ascii=False)
    print(fid,{l:(s.get("words"),s.get("runtime_gap_min"),s.get("words_per_minute")) if s.get("found") else "none" for l,s in summary.items()})
