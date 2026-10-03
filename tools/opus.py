# Read single subtitle files out of the OPUS OpenSubtitles v2024 archives without downloading them whole.
# Indexes are cached in _cache/. Uses HTTP range requests only.
import requests, zipfile, os, json, zlib, struct, io, gzip
BASE="https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/xml/{}.zip"
def _size(url): return int(requests.head(url,timeout=60).headers["content-length"])
def _range(url,a,b):
    for i in range(5):
        try:
            r=requests.get(url,headers={"Range":f"bytes={a}-{b}"},timeout=300)
            if r.status_code==206: return r.content
        except Exception: pass
    raise RuntimeError("range failed")
def index(lang):
    slim=f"_cache/opus_{lang}_slim.json"
    if os.path.exists(slim): return json.load(open(slim))
    cache=f"_cache/opus_{lang}_index.json"
    if os.path.exists(cache): return json.load(open(cache))
    url=BASE.format(lang); size=_size(url)
    tail=_range(url,size-1024*1024,size-1)
    # zip64 end record gives central directory offset/size
    i=tail.rfind(b"PK\x06\x06")
    if i>=0:
        cd_size,cd_off=struct.unpack("<QQ",tail[i+40:i+56])
    else:
        j=tail.rfind(b"PK\x05\x06"); cd_size,cd_off=struct.unpack("<II",tail[j+12:j+20])
    path=f"_cache/opus_{lang}.sparse"
    with open(path,"wb") as f:
        f.truncate(size); f.seek(cd_off)
        step=64*1024*1024; p=cd_off
        while p<size:
            q=min(size-1,p+step-1); f.seek(p); f.write(_range(url,p,q)); p=q+1
    z=zipfile.ZipFile(path)
    out={}
    for zi in z.infolist():
        n=zi.filename
        if n.endswith(".xml") or n.endswith(".xml.gz"):
            parts=n.split("/")  # OpenSubtitles/xml/<lang>/<year>/<imdb>/<id>.xml
            out.setdefault(parts[4],[]).append([n,zi.header_offset,zi.compress_size,zi.compress_type,zi.file_size,parts[3]])
    os.remove(path)
    json.dump(out,open(cache,"w")); return out
def extract(lang,entry):
    n,off,csize,ctype,fsize,year=entry; url=BASE.format(lang)
    h=_range(url,off,off+29+1024)
    fnlen,extlen=struct.unpack("<HH",h[26:30]); start=off+30+fnlen+extlen
    data=_range(url,start,start+csize-1)
    raw=zlib.decompress(data,-15) if ctype==8 else data
    if n.endswith(".gz"): raw=gzip.decompress(raw)
    return raw.decode("utf-8","ignore")
