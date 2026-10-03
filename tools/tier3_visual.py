# Visual measurements from a video file: per-second colour, brightness, shot cuts, a colour barcode and key frames.
import subprocess, numpy as np, json, sys, os, re
from PIL import Image
src, fid = sys.argv[1], sys.argv[2]
out=f"films/{fid}/visuals"; os.makedirs(out+"/frames",exist_ok=True)
W,H=32,24
p=subprocess.run(["ffmpeg","-v","error","-i",src,"-vf",f"fps=1,scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True)
a=np.frombuffer(p.stdout,np.uint8).reshape(-1,H,W,3).astype(np.float32)/255
n=len(a); mean=a.mean(axis=(1,2))
lum=(0.2126*mean[:,0]+0.7152*mean[:,1]+0.0722*mean[:,2])
mx=a.max(axis=3); mn=a.min(axis=3); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0).mean(axis=(1,2))
# barcode: one column per second, mean colour, 300px tall, then resized to 1200 wide
bar=np.repeat((mean[None,:,:]*255).astype(np.uint8),300,axis=0)
Image.fromarray(bar).resize((1200,300),Image.LANCZOS).save(f"{out}/barcode.png")
# tint classification per second (dominant channel bias)
def tint(c):
    r,g,b=c; s=max(c)-min(c)
    if s<0.04: return "monochrome"
    if b>r and b>g: return "blue"
    if r>b and g>b and abs(r-g)<0.06: return "amber/yellow"
    if r>g and r>b: return "red/sepia"
    if g>r and g>b: return "green"
    return "other"
tints=[tint(c) for c in mean]
from collections import Counter
tc=Counter(tints)
# shot cuts
q=subprocess.run(["ffmpeg","-v","info","-i",src,"-vf","select='gt(scene,0.35)',showinfo","-f","null","-"],capture_output=True,text=True)
cuts=[float(x) for x in re.findall(r"pts_time:([\d.]+)",q.stderr)]
dur=n
# key frames: 12 evenly spaced
for i,t in enumerate(np.linspace(dur*0.04,dur*0.96,12)):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(int(t)),"-i",src,"-frames:v","1","-q:v","3",f"{out}/frames/{i+1:02d}_{int(t)//60:02d}m{int(t)%60:02d}s.jpg"])
minute=[{"minute":m,"brightness":round(float(lum[m*60:(m+1)*60].mean()),3),"saturation":round(float(sat[m*60:(m+1)*60].mean()),3),"tint":Counter(tints[m*60:(m+1)*60]).most_common(1)[0][0]} for m in range(int(np.ceil(n/60)))]
rec={"source_file":os.path.basename(src),"seconds_analysed":n,"method":"1 frame per second, downscaled to 32x24; cuts via ffmpeg scene score > 0.35",
 "brightness_mean":round(float(lum.mean()),3),"brightness_by_quarter":[round(float(x.mean()),3) for x in np.array_split(lum,4)],
 "darkest_minute":int(np.argmin([m["brightness"] for m in minute])),"saturation_mean":round(float(sat.mean()),3),
 "tint_share":{k:round(v/n,3) for k,v in tc.most_common()},
 "shots":len(cuts)+1,"average_shot_length_s":round(dur/(len(cuts)+1),1),"cuts_per_minute":round(len(cuts)/(dur/60),2),
 "by_minute":minute,"cut_times_s":[round(c,1) for c in cuts]}
json.dump(rec,open(f"{out}/measures.json","w"),indent=1)
print({k:v for k,v in rec.items() if k not in("by_minute","cut_times_s")})
