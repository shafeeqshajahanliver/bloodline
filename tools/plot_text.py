# Print the sections of a film's Wikipedia article(s) that the story layer may draw on:
# lead, plot and themes/analysis. Usage: python3 tools/plot_text.py <film id> [<film id> ...]
import glob, re, sys
KEEP = re.compile(r"^(lead|plot.*|synopsis|story|summary|premise|storyline|sinopsis|sinopse|trama|handlung|inhalt|intrigue|résumé|hikâye|konu|jalan cerita|alur|plot cerita|cốt truyện|줄거리|あらすじ|ストーリー|剧情|劇情|情节|故事|कथानक|कहानी|الحبكة|القصة|ملخص|сюжет|theme.*|analysis|interpretation.*|symbolism)$", re.I)
for fid in sys.argv[1:]:
    print(f"=================== {fid}")
    for f in sorted(glob.glob(f"films/{fid}/wikipedia.*.md")):
        md = open(f).read()
        print(f"----- {f.rsplit('/', 1)[1]}")
        for m in re.finditer(r"^## (.+?)\n\n(.*?)(?=^## |\Z)", md, re.M | re.S):
            if KEEP.match(m.group(1).strip()):
                body = m.group(2).strip()
                if re.match(r"theme|analysis|interpret|symbol", m.group(1), re.I): body = " ".join(body.split()[:700])
                print(f"## {m.group(1)}\n{body}\n")
