# Choose a balanced set of films for the record: a quota per region, spread across eras, taking the film with the most data in each slot.
# Writes record/films.json. Run from the repo root.
import csv,os,glob,json,collections,math
rows=[r for r in csv.DictReader(open('films.csv')) if os.path.exists(f"films/{r['id']}/story_elements.json")]
def score(r):
    d=f"films/{r['id']}"; se=json.load(open(d+"/story_elements.json"))
    n=sum(len(v) for v in se['dimensions'].values())
    s=0
    s+=3*bool(glob.glob(d+"/visuals/stills/*.jpg"))
    s+=3*os.path.exists(d+"/dialogue/subtitles.en.srt")
    s+=1*os.path.exists(d+"/script/screenplay.txt")
    s+=1*bool(glob.glob(d+"/scares*.json"))
    s+=2*(r['pilot']!='')
    s+=2*(se.get('plot_quality')=='full')
    return s+min(n,60)/60
quota={'North America':32,'Continental Europe':14,'UK & Ireland':11,'East Asia':11,'Southeast Asia':8,
 'Latin America':6,'South Asia':6,'Australia & NZ':5,'Middle East & North Africa':4,'Sub-Saharan Africa':3}
def era(y):
    y=int(y); return '<1960' if y<1960 else '1960s-70s' if y<1980 else '1980s-90s' if y<2000 else '2000-14' if y<2015 else '2015+'
pick=[]
for reg,q in quota.items():
    rs=[r for r in rows if r['region']==reg]
    by=collections.defaultdict(list)
    for r in rs: by[era(r['year'])].append(r)
    for e in by: by[e].sort(key=score,reverse=True)
    # largest-remainder allocation by era share, at least 1 per era if quota allows
    alloc={e:min(len(by[e]),max(1 if q>=len(by) else 0,math.floor(q*len(by[e])/len(rs)))) for e in by}
    while sum(alloc.values())<q:
        e=max((e for e in by if alloc[e]<len(by[e])),key=lambda e:(q*len(by[e])/len(rs)-alloc[e]))
        alloc[e]+=1
    while sum(alloc.values())>q:
        e=max(alloc,key=lambda e:alloc[e]); alloc[e]-=1
    for e in by: pick+=by[e][:alloc[e]]
pick.sort(key=lambda r:(int(r['year']),r['title']))
json.dump([r['id'] for r in pick],open('record/films.json','w'),indent=0)
st=sum(bool(glob.glob(f"films/{r['id']}/visuals/stills/*.jpg")) for r in pick)
sb=sum(os.path.exists(f"films/{r['id']}/dialogue/subtitles.en.srt") for r in pick)
print(len(pick),'stills',st,'subs',sb,'pilots',sum(r['pilot']!='' for r in pick))
print(collections.Counter(era(r['year']) for r in pick))
for reg in quota:
    print(f"\n{reg}: "+"; ".join(f"{r['title']} ({r['year']}){'' if glob.glob(f'films/{r[chr(105)+chr(100)]}/visuals/stills/*.jpg') else ' *'}" for r in pick if r['region']==reg))
