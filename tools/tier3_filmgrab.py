from common import *
from bs4 import BeautifulSoup
import re, numpy as np
from PIL import Image
from io import BytesIO
P={"1960-psycho":"https://film-grab.com/2012/12/31/psycho-2/","1998-ringu":"https://film-grab.com/2025/10/30/ringu/","2016-train-to-busan":"https://film-grab.com/2020/07/13/train-to-busan/","2017-get-out":"https://film-grab.com/2019/05/08/get-out/","2018-hereditary":"https://film-grab.com/2019/03/20/hereditary/","2019-la-llorona":"https://film-grab.com/2026/01/01/la-llorona/"}
import sys
if len(sys.argv)>2: P={sys.argv[1]:sys.argv[2]}
for fid,u in P.items():
    r=S.get(u,timeout=30); s=BeautifulSoup(r.text,"html.parser")
    info=s.select_one(".entry-content"); meta=info.get_text(" ",strip=True)[:400] if info else ""
    imgs=[]
    for a in s.select("a[href]"):
        h=a["href"]
        if re.search(r"/wp-content/uploads/.+\.(jpg|jpeg|png)$",h,re.I) and h not in imgs: imgs.append(h)
    if not imgs:
        for im in s.select("img"):
            h=im.get("data-src") or im.get("src") or ""
            if "/wp-content/uploads/" in h and h not in imgs: imgs.append(re.sub(r"-\d+x\d+(\.\w+)$",r"\1",h))
    d=fdir(fid)+"/visuals/stills"; os.makedirs(d,exist_ok=True)
    stats=[]; saved=[]
    for i,h in enumerate(imgs[:80]):
        try:
            b=S.get(h,timeout=60).content; im=Image.open(BytesIO(b)).convert("RGB")
        except Exception as e: continue
        name=f"{i+1:03d}.jpg"; im.thumbnail((960,960)); im.save(f"{d}/{name}",quality=82); saved.append({"file":name,"url":h})
        a=np.asarray(im.resize((32,24)),dtype=np.float32)/255; m=a.mean(axis=(0,1))
        mx=a.max(2); mn=a.min(2); stats.append((0.2126*m[0]+0.7152*m[1]+0.0722*m[2], float(np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0).mean()), m))
        time.sleep(0.3)
    if stats:
        cols=np.array([x[2] for x in stats]); order=np.argsort([x[0] for x in stats])
        strip=np.repeat((cols[None,:,:]*255).astype(np.uint8),200,axis=0)
        Image.fromarray(strip).resize((1200,200),Image.NEAREST).save(fdir(fid)+"/visuals/stills_strip.png")
        json.dump({"source":u,"site":"FILMGRAB","retrieved":today(),"page_text":meta,"stills":saved,
                   "brightness_mean":round(float(np.mean([x[0] for x in stats])),3),"saturation_mean":round(float(np.mean([x[1] for x in stats])),3),
                   "note":"Stills are curated by FILMGRAB, in film order, not a random sample. Brightness and colour from stills are indicative only. Private research use only."},
                  open(fdir(fid)+"/visuals/stills.json","w"),indent=1,ensure_ascii=False)
    print(fid,len(imgs),"found",len(saved),"saved", meta[:160])
