#!/usr/bin/env python3
"""
Shared machinery for the English -> French pipeline.

The English .qmd files at the top level are the single source of truth. This
module knows how to chop one of them into "runs" — the pieces of prose that
actually need translating — while leaving structure (::: fences, image links,
shortcodes, raw HTML) untouched.

Each run gets a stable id of the form  <page>#<n>  e.g.  mentoring.qmd#12.
data/translations.fr.json maps those ids to {"en": ..., "fr": ...}. Storing the
English alongside the French is what lets us detect that you edited an English
paragraph and its translation is now stale.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY = os.path.join(HERE, "data", "translations.fr.json")

PAGES = [
    "index.qmd",
    "short-bio.qmd",
    "research-interests.qmd",
    "publications.qmd",
    "mentoring.qmd",
    "teaching.qmd",
    "outreach.qmd",
    "contact.qmd",
]

# Pages deliberately not published in French (none at the moment).
FR_SKIP = set()

FR_PAGES = [p for p in PAGES if p not in FR_SKIP]

# Lines that carry structure rather than prose.
RE_FENCE = re.compile(r"^\s*:::")
RE_SHORTCODE = re.compile(r"^\s*\{\{<")
RE_HTML = re.compile(r"^\s*<")
RE_IMAGE_ONLY = re.compile(r"^\s*\[?!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?(\]\([^)]*\)(\{[^}]*\})?)?\s*$")


def is_structure(line):
    return bool(
        RE_FENCE.match(line)
        or RE_SHORTCODE.match(line)
        or RE_HTML.match(line)
        or RE_IMAGE_ONLY.match(line)
    )


def split_front_matter(text):
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[: end + 4], text[end + 4 :]


def find_runs(body):
    """Yield (start_line, end_line_exclusive, [lines]) for every prose run."""
    lines = body.split("\n")
    runs, cur, start = [], [], None
    for i, line in enumerate(lines):
        if line.strip() and not is_structure(line):
            if start is None:
                start = i
            cur.append(line)
        else:
            if cur:
                runs.append((start, i, cur))
            cur, start = [], None
    if cur:
        runs.append((start, len(lines), cur))
    return lines, runs


def run_text(run_lines):
    return "\n".join(run_lines)


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def load_memory():
    if not os.path.exists(MEMORY):
        return {"_pages": {}, "runs": {}}
    with open(MEMORY, encoding="utf-8") as fh:
        return json.load(fh)


def save_memory(mem):
    with open(MEMORY, "w", encoding="utf-8") as fh:
        json.dump(mem, fh, ensure_ascii=False, indent=1, sort_keys=True)


def scan(page):
    """Return (front_matter, lines, runs, ids) for one English page."""
    with open(os.path.join(HERE, page), encoding="utf-8") as fh:
        text = fh.read()
    fm, body = split_front_matter(text)
    lines, runs = find_runs(body)
    ids = [f"{page}#{n}" for n in range(len(runs))]
    return fm, lines, runs, ids
