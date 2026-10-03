import re,json,glob,os
for f in sorted(glob.glob("films/*/script/screenplay.txt")):
    t=open(f,errors="ignore").read()
    heads=re.findall(r"^\s*(?:\d+\s+)?((?:INT|EXT|INTERIOR|EXTERIOR)[\.\-/ ][^\n]*)",t,re.M)
    H=[h.upper() for h in heads]
    night=sum(1 for h in H if "NIGHT" in h); day=sum(1 for h in H if re.search(r"\bDAY\b|MORNING|AFTERNOON",h))
    ints=sum(1 for h in H if h.startswith("INT")); exts=sum(1 for h in H if h.startswith("EXT"))
    words=re.findall(r"[a-z']+",t.lower())
    lex={k:sum(1 for w in words if w in v) for k,v in {"mother_words":{"mother","mom","mommy","mum","mama"},"blood":{"blood","bloody","bleeding"},"door":{"door","doors","doorway"},"dark":{"dark","darkness","shadow","shadows"},"scream":{"scream","screams","screaming"},"silence":{"silence","silent","quiet"}}.items()}
    rec={"words":len(words),"scene_headings":len(H),"interior":ints,"exterior":exts,"night_scenes":night,"day_scenes":day,"night_share":round(night/max(1,night+day),2),"word_counts":lex,"note":"Counts from the text file; heading detection is approximate."}
    json.dump(rec,open(os.path.dirname(f)+"/stats.json","w"),indent=1)
    print(f.split("/")[1],rec)
