from common import *
WP={"1922-nosferatu":"Nosferatu","1960-psycho":"Psycho (1960 film)","1973-the-exorcist":"The Exorcist (film)","1998-ringu":"Ring (1998 film)","2004-pontianak-harum-sundal-malam":"Pontianak Harum Sundal Malam","2016-train-to-busan":"Train to Busan","2017-get-out":"Get Out","2018-tumbbad":"Tumbbad","2018-hereditary":"Hereditary (film)","2019-la-llorona":"La Llorona (2019 film)"}
r=S.get("https://en.wikipedia.org/w/api.php",params=dict(action="query",titles="|".join(WP.values()),prop="pageprops",redirects=1,format="json"),timeout=30).json()
norm={x["from"]:x["to"] for x in r["query"].get("normalized",[])+r["query"].get("redirects",[])}
pages={p["title"]:p for p in r["query"]["pages"].values()}
out={}
for fid,t in WP.items():
    tt=norm.get(t,t); tt=norm.get(tt,tt); p=pages.get(tt,{})
    out[fid]=dict(wikipedia_title=tt,wikipedia_url="https://en.wikipedia.org/wiki/"+tt.replace(" ","_"),qid=p.get("pageprops",{}).get("wikibase_item"),shortdesc=p.get("pageprops",{}).get("wikibase-shortdesc"),missing="missing" in p)
    print(fid,out[fid]["qid"],out[fid]["shortdesc"],out[fid]["missing"])
json.dump(out,open("qids.json","w"),indent=1)
