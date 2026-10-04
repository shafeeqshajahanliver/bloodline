# Train a graph model on the film-fear network and write what it learns to reference/model/.
# The network: 497 films joined to the fears (and archetypes) they carry, from record/site/patterns.json.
# The model: LightGCN (He et al., 2020), a graph neural network that learns a position for every film and fear by
# passing information along the links, trained to rank a film's real fears above ones it doesn't carry (BPR loss).
# Written in plain numpy so it runs anywhere and reproduces exactly (fixed seeds).
# Usage: PYTHONPATH=tools python3 tools/build_patterns.py && PYTHONPATH=tools python3 tools/graph_model.py
import csv, datetime, json, os
import numpy as np

DIM, LAYERS, EPOCHS, LR, REG, NEG = (float(os.environ.get(k, d)) for k, d in [("DIM", 48), ("LAYERS", 1), ("EPOCHS", 250), ("LR", .02), ("REG", 1e-4), ("NEG", 4)])
DIM, LAYERS, EPOCHS, NEG = int(DIM), int(LAYERS), int(EPOCHS), int(NEG)
P = json.load(open("record/site/patterns.json"))
films = P["films"]
DROP = set(filter(None, os.environ.get("DROP", "archetypes,nightmares").split(",")))   # default: learn from the bottom-up fears alone; the top-down archetypes are kept out and compared after, and the nightmares (this model's own output) are never fed back in
fears = sorted({(d, f) for x in films for d, v in x["g"].items() for f in v["f"] if d not in DROP})
fi = {k: i for i, k in enumerate(fears)}
NF, NX = len(films), len(fears)
edges = sorted({(u, fi[(d, f)]) for u, x in enumerate(films) for d, v in x["g"].items() for f in v["f"] if d not in DROP})

# extra context nodes the model can pass information through (they are never predicted, only learned from):
# people (director, writer, composer, camera, top-billed cast), place (region, country), time (decade),
# subject (Wikidata subjects, settings, genres) and wording (the reading's original phrase, before grouping into fears)
EXTRA = [e for e in os.environ.get("EXTRA", "").split(",") if e]
def extra_links():
    import csv
    rows = {r["id"]: r for r in csv.DictReader(open("films.csv"))}
    vocab = {}
    for d in {d for d, _ in fears}:
        if os.path.exists(f"reference/vocab/{d}.tsv"):
            vocab[d] = {r["value"]: r["fear"].strip() for r in csv.DictReader(open(f"reference/vocab/{d}.tsv"), delimiter="\t") if r.get("fear")}
    got, fear_of = {}, {}
    for u, x in enumerate(films):
        keys = set()
        if "people" in EXTRA or "subject" in EXTRA:
            w = json.load(open(f"films/{x['id']}/wikidata.json")) if os.path.exists(f"films/{x['id']}/wikidata.json") else {}
            if "people" in EXTRA:
                for role in ("directors", "screenwriters", "composers", "cinematographers"): keys |= {"p|" + p["id"] for p in w.get(role) or [] if p.get("id")}
                keys |= {"p|" + p["id"] for p in (w.get("cast") or [])[:5] if p.get("id")}
            if "subject" in EXTRA:
                for k in ("main_subjects", "narrative_locations", "genres"): keys |= {"s|" + p["id"] for p in w.get(k) or [] if isinstance(p, dict) and p.get("id")}
        if "place" in EXTRA: keys |= {"r|" + x["r"]} | {"c|" + c.strip() for c in rows[x["id"]]["country"].split(",") if c.strip()}
        if "time" in EXTRA: keys.add(f"t|{x['y'] // 10 * 10}")
        if "wording" in EXTRA:
            se = json.load(open(f"films/{x['id']}/story_elements.json"))
            for d, es in se["dimensions"].items():
                for e in es:
                    f = vocab.get(d, {}).get(e["value"])
                    if f and (d, f) in fi: k = f"w|{d}|{e['value']}"; keys.add(k); fear_of[k] = fi[(d, f)]
        for k in keys: got.setdefault(k, set()).add(u)
    K = sorted(k for k, us in got.items() if len(us) >= 2)   # a node seen in one film carries nothing across films
    ki = {k: j for j, k in enumerate(K)}
    return K, sorted((u, ki[k]) for k in K for u in got[k]), np.array([fear_of.get(k, -1) for k in K])
XK, XL, XFEAR = extra_links() if EXTRA else ([], [], np.array([], int))
NE = len(XK)
print(f"network: {NF} films, {NX} fears, {len(edges)} links · context nodes {NE} ({', '.join(EXTRA) or 'none'}), {len(XL)} links")


def context_for(test):
    """Context links usable when some film-fear links are hidden: drop wording that would give a hidden fear away."""
    return [(u, k) for u, k in XL if XFEAR[k] < 0 or (u, int(XFEAR[k])) not in test]


def propagator(E, C):
    """Mean of A^0..A^L, where A is the symmetrically normalised adjacency of training links E plus context links C."""
    N = NF + NX + NE; A = np.zeros((N, N))
    for u, i in E: A[u, NF + i] = A[NF + i, u] = 1
    for u, k in C: A[u, NF + NX + k] = A[NF + NX + k, u] = 1
    d = A.sum(1); d[d == 0] = 1; A = A / np.sqrt(d)[:, None] / np.sqrt(d)[None, :]
    Pm, Ak = np.eye(N), np.eye(N)
    for _ in range(LAYERS): Ak = Ak @ A; Pm = Pm + Ak
    return Pm / (LAYERS + 1)


def train(E, C, seed=0):
    rng = np.random.default_rng(seed)
    Pm = propagator(E, C); E0 = rng.normal(0, .1, (NF + NX + NE, DIM))
    M = np.zeros((NF, NX), bool)
    for u, i in E: M[u, i] = True
    Eu = np.array([u for u, _ in E]); Ei = np.array([i for _, i in E])
    m, v = np.zeros_like(E0), np.zeros_like(E0)  # Adam
    for t in range(1, EPOCHS + 1):
        Z = Pm @ E0
        u = np.repeat(Eu, NEG); i = np.repeat(Ei, NEG); j = rng.integers(0, NX, len(u))
        ok = ~M[u, j]; u, i, j = u[ok], i[ok], j[ok]
        zu, zi, zj = Z[u], Z[NF + i], Z[NF + j]
        x = (zu * (zi - zj)).sum(1); g = -1 / (1 + np.exp(x))  # d(-log sigmoid x)/dx
        G = np.zeros_like(Z)
        np.add.at(G, u, g[:, None] * (zi - zj)); np.add.at(G, NF + i, g[:, None] * zu); np.add.at(G, NF + j, -g[:, None] * zu)
        G = Pm.T @ (G / len(u)) + REG * E0
        m = .9 * m + .1 * G; v = .999 * v + .001 * G * G
        E0 -= LR * (m / (1 - .9 ** t)) / (np.sqrt(v / (1 - .999 ** t)) + 1e-8)
    return Pm @ E0


def scores_model(Z): return Z[:NF] @ Z[NF:NF + NX].T


def scores_popularity(E):
    c = np.zeros(NX)
    for _, i in E: c[i] += 1
    return np.tile(c, (NF, 1))


def scores_cooccur(E):
    """The non-learned baseline: score a fear by how often it appears alongside the film's other fears (cosine)."""
    M = np.zeros((NF, NX))
    for u, i in E: M[u, i] = 1
    S = M.T @ M; n = np.sqrt(np.diag(S)); n[n == 0] = 1; S = S / n[:, None] / n[None, :]; np.fill_diagonal(S, 0)
    return M @ S


def evaluate(S, train_E, test_E, k=10):
    """Hide links, ask each method to rank the fears a film doesn't (visibly) carry, check where the hidden ones land."""
    tr, te = {}, {}
    for u, i in train_E: tr.setdefault(u, set()).add(i)
    for u, i in test_E: te.setdefault(u, set()).add(i)
    hits = tot = 0; aucs = []
    for u, hid in te.items():
        cand = np.array([i for i in range(NX) if i not in tr.get(u, ())]); s = S[u, cand]
        top = set(cand[np.argsort(-s, kind="stable")[:k]]); hits += len(top & hid); tot += len(hid)
        isp = np.isin(cand, list(hid)); sp, sn = s[isp], s[~isp]
        aucs.append(((sp[:, None] > sn[None, :]).mean() + .5 * (sp[:, None] == sn[None, :]).mean()))
    return {"recall_at_10": round(hits / tot, 3), "auc": round(float(np.mean(aucs)), 3)}


# ---- 1. test: hide 15% of each film's links, train on the rest, see what is recovered (3 different splits)
results = {"model": [], "co-occurrence": [], "popularity": []}
for split in range(int(os.environ.get("SPLITS", 3))):
    rng = np.random.default_rng(int(os.environ.get("SEED0", 200)) + split); by = {}  # settings were tuned on seed 100; the reported test uses fresh splits
    for u, i in edges: by.setdefault(u, []).append(i)
    test = set()
    for u, its in by.items():
        if len(its) >= 5:
            for i in rng.choice(its, max(1, round(.15 * len(its))), replace=False): test.add((u, int(i)))
    tr = [e for e in edges if e not in test]; te = sorted(test)
    results["model"].append(evaluate(scores_model(train(tr, context_for(test), seed=split)), tr, te))
    results["co-occurrence"].append(evaluate(scores_cooccur(tr), tr, te))
    results["popularity"].append(evaluate(scores_popularity(tr), tr, te))
    print(f"split {split}: " + " · ".join(f"{k} {v[-1]}" for k, v in results.items()))
summary = {k: {m: round(float(np.mean([r[m] for r in v])), 3) for m in ("recall_at_10", "auc")} for k, v in results.items()}
print("mean:", summary)

if os.environ.get("EVAL_ONLY"): raise SystemExit
# ---- 2. train on every link and write what the model sees
Z = train(edges, XL, seed=7); S = scores_model(Z)
have = {}
for u, i in edges: have.setdefault(u, set()).add(i)
unit = Z / np.linalg.norm(Z, axis=1, keepdims=True)
F, X = unit[:NF], unit[NF:NF + NX]
name = lambda i: {"lens": fears[i][0], "fear": fears[i][1]}

# fears each film probably also carries (strongest five it is not tagged with): a review queue, not facts
suggest = {}
for u, x in enumerate(films):
    cand = [i for i in np.argsort(-S[u], kind="stable") if i not in have[u]][:5]
    pct = lambda i: round(float((S[u] < S[u, i]).mean()), 3)
    suggest[x["id"]] = [dict(name(i), rank_among_all_fears=pct(i)) for i in cand]

# each film's closest films by learned position (the model's bloodline)
FF = F @ F.T; np.fill_diagonal(FF, -1)
kin = {x["id"]: [{"id": films[v]["id"], "sim": round(float(FF[u, v]), 3)} for v in np.argsort(-FF[u], kind="stable")[:10]] for u, x in enumerate(films)}

# fears that travel together
XX = X @ X.T; np.fill_diagonal(XX, -1)
travel = {f"{fears[i][0]}|{fears[i][1]}": [dict(name(j), sim=round(float(XX[i, j]), 3)) for j in np.argsort(-XX[i], kind="stable")[:8]] for i in range(NX)}

# families of films: k-means on the learned positions (fixed seed, k-means++ start)
def kmeans(D, k, seed=11, iters=100):
    rng = np.random.default_rng(seed); C = [D[rng.integers(len(D))]]
    for _ in range(k - 1):
        d = np.min([((D - c) ** 2).sum(1) for c in C], 0); C.append(D[rng.choice(len(D), p=d / d.sum())])
    C = np.array(C)
    for _ in range(iters):
        lab = np.argmin(((D[:, None] - C[None]) ** 2).sum(2), 1)
        C2 = np.array([D[lab == c].mean(0) if (lab == c).any() else C[c] for c in range(k)])
        if np.allclose(C, C2): break
        C = C2
    return lab, C
lab, C = kmeans(F, 12)
fams = []
for c in range(12):
    mem = [u for u in range(NF) if lab[u] == c]
    if not mem: continue
    cn = C[c] / np.linalg.norm(C[c])
    # the fears that define the family: carried far more often inside it than across the archive
    inside = np.zeros(NX); base = np.zeros(NX)
    for u, i in edges:
        base[i] += 1
        if lab[u] == c: inside[i] += 1
    lift = (inside / len(mem)) / (base / NF)
    top = [i for i in np.argsort(-(lift * (inside >= max(3, .25 * len(mem)))), kind="stable")[:6]]
    core = sorted(mem, key=lambda u: -float(F[u] @ cn))
    fams.append({"films": len(mem), "defining_fears": [dict(name(i), share_inside=round(inside[i] / len(mem), 2), share_overall=round(base[i] / NF, 2)) for i in top],
                 "core_films": [films[u]["id"] for u in core[:8]], "members": [films[u]["id"] for u in core],
                 "regions": {r: sum(films[u]["r"] == r for u in mem) for r in sorted({films[u]["r"] for u in mem})},
                 "decades": {d: sum(films[u]["y"] // 10 * 10 == d for u in mem) for d in sorted({films[u]["y"] // 10 * 10 for u in mem})}})
fams.sort(key=lambda f: -f["films"])
# how the families found from the bottom up line up with the top-down archetypes tagged on the same films
import csv
ARCH = {r["code"]: r["name"] for r in csv.DictReader(open("archetypes.csv"))}
prim = {r["id"]: ARCH.get(r["archetype_primary"], "") for r in csv.DictReader(open("films.csv"))}
for f in fams:
    c = {}
    for i in f["members"]: c[prim[i]] = c.get(prim[i], 0) + 1
    top = sorted(c.items(), key=lambda x: (-x[1], x[0]))[:3]
    f["archetypes_inside"] = [{"archetype": a, "share": round(n / f["films"], 2)} for a, n in top if a]

OUT = os.environ.get("OUT", "reference/model"); os.makedirs(OUT, exist_ok=True)
meta = {"method": "LightGCN graph neural network (He et al., 2020), BPR loss, numpy implementation in tools/graph_model.py",
        "settings": {"dimensions": DIM, "layers": LAYERS, "epochs": EPOCHS, "learning_rate": LR, "negatives": NEG},
        "network": {"films": NF, "fears": NX, "links": len(edges), "left_out": sorted(DROP)},
        "tuning": "on one validation split (seed 100): depth 1 beat 0, 2 and 3 layers (3 layers collapsed to popularity); adding people, place, time, subject or original-wording nodes did not help (recall@10 0.264 to 0.267 vs 0.270 without)",
        "test": "fresh splits (seeds 200-202), 15% of each film's links hidden (films with 5+ links), mean of 3 splits; recall@10 = share of hidden fears ranked in the film's top 10 of the fears it doesn't visibly carry",
        "results": summary, "trained": datetime.date.today().isoformat(),
        "status": "first pass: model output from first-pass tags, unreviewed. Suggestions are a review queue, not facts."}
for fn, obj in [("meta", meta), ("suggestions", suggest), ("kin", kin), ("fears_travel", travel), ("families", fams)]:
    json.dump(obj, open(f"{OUT}/{fn}.json", "w"), ensure_ascii=False, indent=1 if fn in ("meta", "families") else None, separators=None if fn in ("meta", "families") else (",", ":"))
print(f"wrote {OUT}/ · {len(fams)} families")

# ---- 3. a plain-English report
if OUT == "reference/model":
    titles = {r["id"]: f"{r['title']} ({r['year']})" for r in csv.DictReader(open("films.csv"))}
    m, c, p = summary["model"], summary["co-occurrence"], summary["popularity"]
    L = ["# Graph model", "", f"Generated by `tools/graph_model.py` on {meta['trained']}. Status: {meta['status']}", "",
         "## What it is", "",
         f"A graph neural network (LightGCN) trained on the network of {NF} films and the {NX} bottom-up fears they carry ({len(edges):,} links). "
         "It learns a position for every film and fear so that films sit near the fears they carry. The 27 top-down archetypes are kept out of training and compared afterwards.", "",
         "## How well it works", "",
         "Test: hide 15% of each film's fears, train on the rest, and see whether the hidden fears come back near the top of each film's list (fresh splits, never used for tuning).", "",
         "| Method | Hidden fears found in the top 10 | Ranking quality (AUC) |", "|---|---|---|",
         f"| Graph model | {m['recall_at_10']:.0%} | {m['auc']:.2f} |", f"| Fears that appear together (no learning) | {c['recall_at_10']:.0%} | {c['auc']:.2f} |",
         f"| Most common fears | {p['recall_at_10']:.0%} | {p['auc']:.2f} |", f"| Random guess | {10 / NX:.0%} | 0.50 |", "",
         "The model edges out the simpler methods but not by much. Most of what can be predicted is carried by which fears appear together; "
         "adding people, place, decade, subject or the original wording did not help. Its strength is the map it learns: families of films and each film's nearest kin.", "",
         "## Families of films it found", ""]
    for n, f in enumerate(fams, 1):
        L += [f"**{n}. {', '.join(x['fear'] for x in f['defining_fears'][:3])}** ({f['films']} films)", "",
              f"Core films: {', '.join(titles[i] for i in f['core_films'][:6])}.", "",
              "Defining fears (share inside the family vs across all films): " + "; ".join(f"{x['fear']} {x['share_inside']:.0%} vs {x['share_overall']:.0%}" for x in f["defining_fears"][:5]) + ".", "",
              "Top-down archetypes inside: " + "; ".join(f"{a['archetype']} {a['share']:.0%}" for a in f["archetypes_inside"]) + ".", ""]
    L += ["## Caveats", "", "- It learns from first-pass, unreviewed tags, so it inherits their gaps and biases. The de-bias pass has not been run.",
          "- Suggested fears (`suggestions.json`) lean towards common fears; treat them as a review queue, never as facts.",
          "- Family boundaries depend on asking for 12 families; the core films are stable, the edges less so."]
    open("reports/graph-model.md", "w").write("\n".join(L) + "\n")
    print("wrote reports/graph-model.md")
