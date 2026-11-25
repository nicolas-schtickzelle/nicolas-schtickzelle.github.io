#!/usr/bin/env python3
"""
Turn data/publications.csv into two markdown fragments that publications.qmd
includes:

    _includes/articles.md
    _includes/chapters.md

Run it whenever you edit the CSV:   python tools/build_publications.py
Then re-render the site:            quarto render
"""
import csv
import datetime as dt
import json
import html
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "data", "publications.csv")
OUT = os.path.join(HERE, "_includes")

# Your name is highlighted in every author list.
ME = "Schtickzelle N"


def authors_html(raw):
    return html.escape(raw).replace(ME, f'<span class="me">{ME}</span>')


def entry_html(row):
    bits = [authors_html(row["authors"]), f'<span class="title">{html.escape(row["title"])}</span>']
    venue = row["venue"].strip()
    if venue:
        vol = row["volume"].strip()
        pages = row["pages"].strip()
        tail = venue
        if vol:
            tail += f" {vol}"
        if pages == "in press":
            tail += ", in press"
        elif pages:
            tail += f": {pages}"
        bits.append(f'<span class="venue">{html.escape(tail)}</span>')
    doi = row["doi"].strip()
    if doi:
        bits.append(f'<a href="https://doi.org/{doi}">doi:{doi}</a>')
    return "  \n".join(bits)


def render(rows):
    by_year = OrderedDict()
    for r in sorted(rows, key=lambda x: int(x["year"]), reverse=True):
        by_year.setdefault(r["year"], []).append(r)
    out = []
    for year, items in by_year.items():
        out.append(f'::: pub-year\n{year}\n:::\n')
        out.append('<ol class="pubs">')
        for r in items:
            out.append(f"<li>{entry_html(r)}</li>")
        out.append("</ol>\n")
    return "\n".join(out)


MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]

BIBLIO_LABELS = {
    "en": ("peer-reviewed journal articles", "peer-reviewed book chapters",
           "citations, i.e. {mean} per publication on average", "h-index",
           "Source: [OpenAlex](https://openalex.org/authors/A5010883702), computed on the publications listed on this site. Updated {date}."),
    "fr": ("articles dans des revues à comité de lecture", "chapitres de livres à comité de lecture",
           "citations, soit {mean} par publication en moyenne", "h-index",
           "Source : [OpenAlex](https://openalex.org/authors/A5010883702), calculé sur les publications listées sur ce site. Mise à jour : {date}."),
}


def bibliometry_md(lang, b):
    d = dt.date.fromisoformat(b["updated"])
    date = (f"{MONTHS_EN[d.month - 1]} {d.year}" if lang == "en" else f"{MONTHS_FR[d.month - 1]} {d.year}")
    a, c, cit, h, src = BIBLIO_LABELS[lang]
    boxes = [(b["articles"], a), (b["chapters"], c), (b["citations"], cit.format(mean=b["mean_per_item"])), (b["h_index"], h)]
    out = ["::: figures"]
    for n, lab in boxes:
        out += ["::: figure-box", "::: n", str(n), ":::", "::: lab", lab, ":::", ":::", ""]
    out += [":::", "", "::: biblio-source", src.format(date=date), ":::", ""]
    return "\n".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    articles = [r for r in rows if r["kind"] == "article"]
    chapters = [r for r in rows if r["kind"] == "chapter"]
    for name, data in (("articles", articles), ("chapters", chapters)):
        with open(os.path.join(OUT, f"{name}.md"), "w", encoding="utf-8") as fh:
            fh.write(render(data))
    print(f"wrote {len(articles)} articles and {len(chapters)} book chapters")

    bj = os.path.join(HERE, "data", "bibliometry.json")
    if os.path.exists(bj):
        with open(bj, encoding="utf-8") as fh:
            b = json.load(fh)
        for lang in ("en", "fr"):
            with open(os.path.join(OUT, f"bibliometry.{lang}.md"), "w", encoding="utf-8") as fh:
                fh.write(bibliometry_md(lang, b))
        print("wrote bibliometry (en, fr)")


if __name__ == "__main__":
    main()
