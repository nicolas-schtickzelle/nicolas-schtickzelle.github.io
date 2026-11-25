#!/usr/bin/env python3
"""
List OpenAlex works by Nicolas Schtickzelle that are NOT yet in
data/publications.csv and look like journal articles or book chapters.

    python tools/find_new_publications.py               # print candidates
    python tools/find_new_publications.py --markdown F  # also write a report (for the monthly pull request)
    python tools/find_new_publications.py --csv F       # write candidate rows in the CSV format
    python tools/find_new_publications.py --update-csv  # fill DOI/volume/pages of "in press" items now published

Nothing is added to the site automatically: candidates are proposed for review.
Skipped on purpose: conference abstracts, datasets, preprints, Peer Community In
recommendations/reviews, newspaper pieces, items older than the newest year - 3.
"""
import argparse
import csv
import json
import os
import re
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "data", "publications.csv")
AUTHOR_ID = "A5010883702"
API = "https://api.openalex.org/works"
MAILTO = "nicolas-schtickzelle@users.noreply.github.com"
KEEP = {"article": "article", "review": "article", "book-chapter": "chapter"}
SKIP_VENUE = re.compile(r"peer community in|biorxiv|preprints\.org|le soir|digital access to libraries|zenodo|dryad", re.I)
SKIP_TITLE = re.compile(r"^(recommendation of|review of|decision |reply to|correction|erratum)", re.I)


def norm(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def short_authors(w):
    names = []
    for a in w.get("authorships", []):
        parts = a["author"]["display_name"].split()
        if not parts:
            continue
        last, first = parts[-1], parts[:-1]
        names.append(f"{last} " + "".join(p[0] + "." for p in first if p[0].isalpha()))
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]


def fetch(since):
    works, cursor = [], "*"
    while cursor:
        qs = urllib.parse.urlencode({
            "filter": f"author.id:{AUTHOR_ID},from_publication_date:{since}-01-01",
            "per-page": 200, "cursor": cursor, "mailto": MAILTO,
            "select": "id,doi,title,publication_year,type,authorships,primary_location,biblio,cited_by_count",
        })
        with urllib.request.urlopen(f"{API}?{qs}", timeout=60) as r:
            page = json.load(r)
        works += page["results"]
        cursor = page["meta"].get("next_cursor") if page["results"] else None
    return works


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--markdown")
    ap.add_argument("--csv")
    ap.add_argument("--update-csv", action="store_true")
    args = ap.parse_args()
    with open(CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    known_ids = {r.get("openalex", "").strip() for r in rows}
    known_doi = {r["doi"].lower().strip() for r in rows if r["doi"].strip()}
    known_title = {norm(r["title"]) for r in rows}
    newest = max(int(r["year"]) for r in rows)
    pending = {norm(r["title"]): r for r in rows if not r.get("openalex", "").strip()}
    cands, updated = [], []
    for w in fetch(newest - 3):
        wid = w["id"].rsplit("/", 1)[-1]
        row = pending.get(norm(w["title"]))
        if row is not None and w["type"] in KEEP:
            b = w.get("biblio") or {}
            pg = b.get("first_page") or ""
            if b.get("last_page") and b["last_page"] != pg:
                pg += "–" + b["last_page"]
            row.update(openalex=wid, doi=(w.get("doi") or "").replace("https://doi.org/", ""),
                       volume=b.get("volume") or "", pages=pg, year=str(w["publication_year"]))
            updated.append(row["title"])
            continue
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        if w["type"] not in KEEP or wid in known_ids or (doi and doi in known_doi) \
                or norm(w["title"]) in known_title or SKIP_VENUE.search(src) or SKIP_TITLE.search(w["title"] or ""):
            continue
        b = w.get("biblio") or {}
        pages = b.get("first_page") or ""
        if b.get("last_page") and b["last_page"] != pages:
            pages += "–" + b["last_page"]
        cands.append({
            "kind": KEEP[w["type"]], "year": str(w["publication_year"]), "authors": short_authors(w),
            "title": (w["title"] or "").replace("‐", "-"), "venue": src, "volume": b.get("volume") or "",
            "pages": pages, "doi": doi, "openalex": wid,
        })
    if args.update_csv and updated:
        with open(CSV, "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(rows)
    print(f"{len(updated)} in-press item(s) now published: {updated}")
    print(f"{len(cands)} candidate(s)")
    for c in cands:
        print(f"- {c['year']} {c['title']} — {c['venue']} (doi:{c['doi']})")
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(cands)
    if args.markdown:
        with open(args.markdown, "w", encoding="utf-8") as fh:
            if updated:
                fh.write("## In-press items now published (DOI and pages filled in)\n\n")
                fh.writelines(f"- {t}\n" for t in updated)
                fh.write("\n")
            fh.write(f"## {len(cands)} possible new publication(s) found in OpenAlex\n\n")
            for c in cands:
                fh.write(f"- **{c['title']}** ({c['year']})  \n  {c['authors']}  \n  *{c['venue']}* "
                         f"{c['volume']} {c['pages']} — https://doi.org/{c['doi']}\n")
            fh.write("\nMerging this pull request adds them to data/publications.csv and the website. "
                     "Delete any line that is not yours before merging.\n")
    return 0


if __name__ == "__main__":
    main()
