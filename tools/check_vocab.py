# Check reference/vocab/<dim>.tsv against reference/vocab/input/<dim>.tsv: every input value appears exactly once,
# and every row has a kind and a fear. Usage: python3 tools/check_vocab.py [dims]
import csv, sys
DIMS = sys.argv[1:] or ["threat", "origin", "wants", "wrong", "trigger", "rules", "who_suffers", "ending", "images"]
for d in DIMS:
    want = [r["value"] for r in csv.DictReader(open(f"reference/vocab/input/{d}.tsv"), delimiter="\t")]
    try: got = list(csv.DictReader(open(f"reference/vocab/{d}.tsv"), delimiter="\t"))
    except FileNotFoundError: print(d, "missing"); continue
    seen = {}
    bad = [r for r in got if not r.get("kind", "").strip() or not r.get("fear", "").strip()]
    for r in got: seen[r["value"]] = seen.get(r["value"], 0) + 1
    miss = [v for v in want if v not in seen]; dup = [v for v, n in seen.items() if n > 1]; extra = [v for v in seen if v not in set(want)]
    fears = {r["fear"] for r in got}; kinds = {(r["fear"], r["kind"]) for r in got}
    ok = not (miss or dup or extra or bad)
    print(f"{d}: {'OK' if ok else 'PROBLEMS'} · {len(got)}/{len(want)} values · {len(fears)} fears · {len(kinds)} kinds"
          + (f" · missing {len(miss)} e.g. {miss[:3]}" if miss else "") + (f" · duplicated {len(dup)} e.g. {dup[:3]}" if dup else "")
          + (f" · unknown {len(extra)} e.g. {extra[:3]}" if extra else "") + (f" · {len(bad)} rows without kind/fear" if bad else ""))
