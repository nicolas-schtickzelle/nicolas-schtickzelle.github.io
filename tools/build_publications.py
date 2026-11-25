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
        if pages:
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


if __name__ == "__main__":
    main()
