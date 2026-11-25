#!/usr/bin/env python3
"""
Refresh data/publications.csv from OpenAlex (https://openalex.org), a free and
open bibliographic database — no API key needed.

    python tools/update_publications.py            # preview, writes nothing
    python tools/update_publications.py --write    # overwrite the CSV

The OpenAlex author record used is:
    Nicolas Schtickzelle — https://openalex.org/A5010883702
    ORCID 0000-0001-7829-5361

OpenAlex is comprehensive but not curated: it will pick up preprints, conference
abstracts and the occasional mis-attributed paper. So the intended workflow is:

    1. run this with --write into a scratch copy,
    2. diff it against data/publications.csv,
    3. keep what is genuinely yours,
    4. run tools/build_publications.py and re-render.

Your curated CSV stays the source of truth for the website.
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request

AUTHOR_ID = "A5010883702"
API = "https://api.openalex.org/works"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "data", "publications.csv")

ARTICLE_TYPES = {"article", "review"}
CHAPTER_TYPES = {"book-chapter", "book"}


def short_authors(work):
    names = []
    for a in work.get("authorships", []):
        full = a["author"]["display_name"].strip().split()
        last = full.pop() if full else ""
        initials = "".join(p[0] for p in full if p and p[0].isalpha())
        names.append(f"{last} {initials}".strip())
    return ", ".join(names)


def clean(text):
    return re.sub(r"<[^>]+>", "", text or "").replace("\n", " ").strip()


def fetch():
    works, page = [], 1
    fields = "id,doi,title,publication_year,type,authorships,primary_location,biblio"
    while page <= 5:
        qs = urllib.parse.urlencode(
            {"filter": f"author.id:{AUTHOR_ID}", "per-page": 100, "page": page, "select": fields}
        )
        req = urllib.request.Request(
            f"{API}?{qs}", headers={"User-Agent": "nicolas-schtickzelle.net (mailto:nicolas.schtickzelle@uclouvain.be)"}
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r).get("results", [])
        works.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return works


def to_rows(works):
    rows, seen = [], set()
    for w in works:
        if w["type"] in ARTICLE_TYPES:
            kind = "article"
        elif w["type"] in CHAPTER_TYPES:
            kind = "chapter"
        else:
            continue
        title = clean(w.get("title"))
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        biblio = w.get("biblio") or {}
        pages = "-".join(p for p in (biblio.get("first_page"), biblio.get("last_page")) if p)
        source = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        rows.append(
            {
                "kind": kind,
                "year": w.get("publication_year") or "",
                "authors": short_authors(w),
                "title": title,
                "venue": source,
                "volume": biblio.get("volume") or "",
                "pages": pages,
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            }
        )
    rows.sort(key=lambda r: (r["kind"], -int(r["year"] or 0)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="overwrite data/publications.csv")
    args = ap.parse_args()

    rows = to_rows(fetch())
    n_art = sum(r["kind"] == "article" for r in rows)
    n_chap = len(rows) - n_art
    print(f"OpenAlex returned {n_art} articles and {n_chap} book chapters", file=sys.stderr)

    if not args.write:
        print("(preview only — re-run with --write to overwrite the CSV)", file=sys.stderr)
        for r in rows[:10]:
            print(f"  {r['year']}  {r['title'][:80]}", file=sys.stderr)
        return

    with open(CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["kind", "year", "authors", "title", "venue", "volume", "pages", "doi"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {CSV}", file=sys.stderr)


if __name__ == "__main__":
    main()
