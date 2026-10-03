# Source files a film's corrections.json marks as unusable (commentary tracks, wrong film, empty or garbled scans).
# use "none": never read it; use "quotes_only": a few clean lines may be quoted, but measures from it are invalid.
import json, os
def unusable(fid):
    p = f"films/{fid}/corrections.json"
    if not os.path.exists(p): return {}
    return {u["file"]: u["use"] for u in json.load(open(p)).get("unusable_sources", [])}
