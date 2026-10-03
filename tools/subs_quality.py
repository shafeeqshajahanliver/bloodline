# Flag subtitle files that don't match the film's runtime or look partial.
import json,glob
for p in glob.glob("films/*/dialogue/measures.json"):
    d=json.load(open(p)); bl=d["by_language"]; en=bl.get("en",{}).get("words")
    for l,s in bl.items():
        if not s.get("found"): continue
        flags=[]
        if s.get("runtime_min") is None: flags.append("no runtime to check against")
        elif s["runtime_gap_min"]>5: flags.append("ends more than 5 min from the runtime: different cut or partial file")
        if l!="en" and en and s["words"]<0.3*en and l not in("ko","ja","th","zh"): flags.append("far fewer words than the English file: likely partial")
        s["quality"]="check" if flags else "good"; s["quality_notes"]=flags
    json.dump(d,open(p,"w"),indent=1,ensure_ascii=False)
