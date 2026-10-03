# Summarise the bottom-up story layer (films/*/story_elements.json) into reports/story-elements.md.
# Raw values only: no merging yet, so near-duplicates ("ghost", "vengeful ghost") are counted separately.
import collections, csv, glob, json, datetime
DIMS = ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images", "beats"]
NAME = {"threat": "Threat", "origin": "Origin of the threat", "wants": "What it wants", "wrong": "The wrong underneath", "trigger": "Trigger",
        "rules": "Rules", "who_suffers": "Who suffers", "ending": "Ending", "images": "Images", "beats": "Beats"}
films = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
data = {p.split("/")[1]: json.load(open(p)) for p in sorted(glob.glob("films/*/story_elements.json"))}
cnt = {k: collections.Counter() for k in DIMS}; filled = collections.Counter(); notst = collections.Counter()
quality = collections.Counter(); conf = collections.Counter(); entries = 0
rel = collections.Counter(); omen = collections.Counter(); opening = collections.Counter(); omen_films = collections.defaultdict(set)
for fid, d in data.items():
    quality[d.get("plot_quality")] += 1
    for k in d.get("not_stated", []): notst[k] += 1
    for k in DIMS:
        es = d.get("dimensions", {}).get(k, [])
        if es: filled[k] += 1
        for v in {e["value"].lower().strip() for e in es}: cnt[k][v] += 1
        for e in es:
            entries += 1; conf[e.get("confidence")] += 1
            if k == "who_suffers": rel[e.get("relation_to_threat")] += 1
            if k == "images" and e.get("role") == "omen": omen[e["value"].lower()] += 1; omen_films[e["value"].lower()].add(fid)
            if k == "beats" and e.get("when") == "opening": opening[e["value"].lower()] += 1
n = len(data)
md = [f"# Story elements: first pass\n\nGenerated {datetime.date.today()} from `films/*/story_elements.json` ({n} films, {entries} quoted entries). "
      "Values are raw, as written by the reader: near-duplicates are not merged yet, so counts understate how common each idea is. "
      "Every entry is a first pass, unreviewed. Schema: `docs/story-elements.md`.\n",
      f"Plot quality: {quality['full']} full, {quality['thin']} thin, {quality['none']} lead only. "
      f"Confidence: {conf['sourced']} entries stated directly in the article, {conf['observed']} read from it.\n",
      "## How often each dimension could be filled\n\n| Dimension | Films with at least one entry | Marked not stated |\n|---|---|---|"]
md += [f"| {NAME[k]} | {filled[k]} | {notst[k]} |" for k in DIMS]
for k in DIMS:
    md.append(f"\n## {NAME[k]}: most common values\n\n" + ", ".join(f"{v} ({c})" for v, c in cnt[k].most_common(25)))
    md.append(f"\n{len(cnt[k])} distinct values in total.")
md.append("\n## Who suffers: relation to the threat\n\n" + ", ".join(f"{k} ({v})" for k, v in rel.most_common()))
md.append("\n## Images used as omens\n\n" + ", ".join(f"{v} ({c})" for v, c in omen.most_common(25)))
import re
ANIMAL = re.compile(r"\b(deer|dogs?|cats?|kitten|birds?|crows?|ravens?|goats?|horses?|rabbits?|fox|owls?|snakes?|moths?|fly|flies|rats?|wolf|wolves|insects?|animals?|pigs?|cow|sheep|lamb|fish|pigeons?|reindeer|bat|frogs?|kangaroo|baboon|chimp\w*|monkey|spider|scorpion|lizards?|gulls?|hens?|elephant)\b")
animals = [a for a in omen if ANIMAL.search(a) and not re.search(r"\b(statue|doll|smell|nets)\b", a)]
md.append("\n### Animals as omens\n\n" + "\n".join(f"- {a}: " + ", ".join(sorted(films[f]["title"] + " (" + films[f]["year"] + ")" for f in omen_films[a])) for a in sorted(animals, key=lambda a: -len(omen_films[a]))))
md.append("\n## How films open (opening beats)\n\n" + ", ".join(f"{v} ({c})" for v, c in opening.most_common(30)))
open("reports/story-elements.md", "w").write("\n".join(md) + "\n")
print(f"{n} films, {entries} entries")
