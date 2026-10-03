from common import *
from bs4 import BeautifulSoup
import re
M={"1960-psycho":"psycho-1960","1973-the-exorcist":"the-exorcist-1973","1998-ringu":"ring-1998","2017-get-out":"get-out-2017","2016-train-to-busan":"train-to-busan-2016","2018-hereditary":"hereditary-2018","2004-pontianak-harum-sundal-malam":"pontianak-harum-sundal-malam-2004","2018-tumbbad":"tumbbad-2018","2019-la-llorona":"la-llorona-2019","1922-nosferatu":"nosferatu-1922"}
def secs(t): h,m,s=map(int,t.split(":")); return h*3600+m*60+s
for fid,sl in M.items():
    u=f"https://wheresthejump.com/jump-scares-in-{sl}/"; r=S.get(u,timeout=30); time.sleep(1)
    c=BeautifulSoup(r.text,"html.parser").select_one(".entry-content") if r.status_code==200 else None
    txt=c.get_text("\n",strip=True) if c else ""
    if "Jump Scare Times" not in txt and "Jump Scares:" not in txt:
        print(fid,"not on Where's the Jump"); continue
    m=re.search(r"jump scare rating of (\d+(?:\.\d+)?)",txt); cnt=re.search(r"Jump Scares:\n(\d+)\s*\(([^)]*)\)",txt)
    body=txt.split("Jump Scare Times",1)[-1]
    items=re.findall(r"(\d\d:\d\d:\d\d)\n–\s*(.+)",body)
    scares=[{"time":t,"seconds":secs(t),"major":"(major)" in d.lower() or "[major]" in d.lower() or d.strip().endswith("(Major)"),"description":d.strip()} for t,d in items]
    rec={"source":u,"site":"Where's the Jump (crowd-sourced)","retrieved":today(),"rating":float(m.group(1)) if m else None,"count_summary":cnt.group(0).replace("\n"," ") if cnt else None,"scares":scares}
    json.dump(rec,open(f"{fdir(fid)}/scares.json","w"),indent=1,ensure_ascii=False)
    print(fid,rec["rating"],rec["count_summary"],len(scares),"first at",scares[0]["time"] if scares else None)
