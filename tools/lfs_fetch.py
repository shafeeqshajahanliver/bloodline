# Replace Git LFS pointer files with the real images when a host clones without LFS (e.g. Vercel).
# Downloads each from GitHub's media server for this commit. Only stills and the author photo are needed to build the app.
# Usage: python3 tools/lfs_fetch.py
import glob, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
REPO = os.environ.get("LFS_REPO", "shafeeqshajahanliver/bloodline")
REF = os.environ.get("VERCEL_GIT_COMMIT_SHA") or os.environ.get("LFS_REF", "claude/loving-lovelace-8awtad")
files = glob.glob("films/*/visuals/stills/*.jpg") + ["record/author.jpg"]
def is_pointer(p):
    try:
        with open(p, "rb") as f: return f.read(40).startswith(b"version https://git-lfs")
    except OSError: return False
todo = [p for p in files if is_pointer(p)]
print(f"{len(todo)} of {len(files)} images are LFS pointers; fetching", flush=True)
def get(p):
    url = f"https://media.githubusercontent.com/media/{REPO}/{REF}/{p}"
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r: data = r.read()
            if not data.startswith(b"version https://git-lfs"):
                open(p, "wb").write(data); return True
        except Exception: pass
    return False
with ThreadPoolExecutor(32) as ex: ok = sum(ex.map(get, todo))
print(f"fetched {ok} of {len(todo)}")
