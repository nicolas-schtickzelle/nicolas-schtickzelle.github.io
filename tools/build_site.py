#!/usr/bin/env python3
"""
Build the whole bilingual site in one command:

    python tools/build_site.py

Steps, in order:
  1. data/publications.csv  ->  _includes/*.md
  1b. data/mentees.csv      ->  _includes/mentees_map.*.md
  1c. data/contact_places.csv ->  _includes/contact_map.*.md
  2. English .qmd + data/translations.fr.json  ->  fr/*.qmd
  3. quarto render          (English -> _site/)
  4. quarto render in fr/   (French  -> _site/fr/)

Anything untranslated or stale is reported but does not stop the build — those
blocks simply stay in English on the French pages.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(HERE, "tools")


def run(cmd, cwd, label):
    print(f"\n=== {label}")
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"FAILED: {label}", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    py = sys.executable
    run([py, "build_publications.py"], TOOLS, "publications.csv -> _includes/")
    run([py, "build_mentees_map.py"], TOOLS, "mentees.csv -> _includes/mentees_map.*.md")
    run([py, "build_contact_map.py"], TOOLS, "contact_places.csv -> _includes/contact_map.*.md")
    run([py, "build_french.py"], TOOLS, "English + translations -> fr/")
    run("quarto render", HERE, "render English -> _site/")
    run("quarto render", os.path.join(HERE, "fr"), "render French -> _site/fr/")
    print("\nDone. Open _site/index.html")


if __name__ == "__main__":
    main()
