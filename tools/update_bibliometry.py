#!/usr/bin/env python3
"""
Recompute the bibliometry figures shown on the home page from YOUR curated list
(data/publications.csv), using citation counts from OpenAlex (free, no key).

    python tools/update_bibliometry.py      # writes data/bibliometry.json

Only items in the CSV are counted: OpenAlex's own author totals also include
conference abstracts, datasets and preprints, which would inflate the figures.
Run monthly by .github/workflows/monthly-update.yml.
"""
import csv
import datetime as dt
import json
import os
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "data", "publications.csv")
OUT = os.path.join(HERE, "data", "bibliometry.json")
API = "https://api.openalex.org/works"
MAILTO = "nicolas-schtickzelle@users.noreply.github.com"


def citations(ids):
    counts = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        qs = urllib.parse.urlencode({
            "filter": "openalex:" + "|".join(chunk),
            "per-page": 50, "select": "id,cited_by_count", "mailto": MAILTO,
        })
        with urllib.request.urlopen(f"{API}?{qs}", timeout=60) as r:
            for w in json.load(r)["results"]:
                counts[w["id"].rsplit("/", 1)[-1]] = w["cited_by_count"]
    return counts


def main():
    with open(CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["openalex"].strip() for r in rows if r.get("openalex", "").strip()]
    counts = citations(ids)
    arts = [r for r in rows if r["kind"] == "article"]
    chaps = [r for r in rows if r["kind"] == "chapter"]
    cites_all = sorted((counts.get(r.get("openalex", "").strip(), 0) for r in rows), reverse=True)
    h = sum(1 for k, c in enumerate(cites_all, 1) if c >= k)
    total = sum(cites_all)
    data = {
        "articles": len(arts),
        "chapters": len(chaps),
        "citations": total,
        "mean_per_item": round(total / max(len(arts) + len(chaps), 1)),
        "h_index": h,
        "source": "OpenAlex",
        "updated": dt.date.today().isoformat(),
        "missing_openalex_id": [r["title"][:60] for r in rows if not r.get("openalex", "").strip()],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
