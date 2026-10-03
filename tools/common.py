import requests, time, json, os, datetime
UA = {"User-Agent": "story-dna-research/0.1 (private non-commercial film research)"}
S = requests.Session(); S.headers.update(UA)
def get(url, **kw):
    for i in range(5):
        r = S.get(url, timeout=60, **kw)
        if r.status_code == 429:
            time.sleep(5*(i+1)); continue
        return r
    return r
def today(): return datetime.date.today().isoformat()
PILOT = {
 "1922-nosferatu": ("Nosferatu", 1922),
 "1960-psycho": ("Psycho", 1960),
 "1973-the-exorcist": ("The Exorcist", 1973),
 "1998-ringu": ("Ring", 1998),
 "2004-pontianak-harum-sundal-malam": ("Pontianak Harum Sundal Malam", 2004),
 "2016-train-to-busan": ("Train to Busan", 2016),
 "2017-get-out": ("Get Out", 2017),
 "2018-tumbbad": ("Tumbbad", 2018),
 "2018-hereditary": ("Hereditary", 2018),
 "2019-la-llorona": ("La Llorona", 2019),
}
def fdir(fid):
    d = f"films/{fid}"; os.makedirs(d, exist_ok=True); return d
def get_json(url, **kw):
    for i in range(6):
        r = get(url, **kw)
        try: return r.json()
        except Exception: time.sleep(4*(i+1))
    raise RuntimeError(f"no json from {url} {r.status_code} {r.text[:200]}")
