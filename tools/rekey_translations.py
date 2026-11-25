#!/usr/bin/env python3
"""
Keep French translations attached to the right paragraphs after English edits.

Run ids in data/translations.fr.json are positional (page#n). When you add or
remove a paragraph in an English page, every later id shifts. This script
compares each English page with its last committed version (git HEAD),
re-attaches every existing translation to the paragraph with the same English
text, and lists the paragraphs that are new and still need a French version.

    python tools/rekey_translations.py          # re-key and report
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n  # noqa: E402


def runs_of(text):
    _, body = i18n.split_front_matter(text)
    _, runs = i18n.find_runs(body)
    return [i18n.normalise(i18n.run_text(r[2])) for r in runs]


def main():
    mem = i18n.load_memory()
    old_runs = mem["runs"]
    new_runs = {k: v for k, v in old_runs.items() if k.split("#")[0] not in i18n.FR_PAGES}
    todo = []
    for page in i18n.FR_PAGES:
        try:
            old_text = subprocess.run(
                ["git", "show", f"HEAD:{page}"], cwd=i18n.HERE,
                capture_output=True, text=True, encoding="utf-8", check=True,
            ).stdout
        except subprocess.CalledProcessError:
            old_text = ""
        by_en = {}
        for n, en in enumerate(runs_of(old_text)):
            entry = old_runs.get(f"{page}#{n}")
            if entry:
                by_en.setdefault(en, entry)
        with open(os.path.join(i18n.HERE, page), encoding="utf-8") as fh:
            current = runs_of(fh.read())
        for n, en in enumerate(current):
            rid = f"{page}#{n}"
            if en in by_en:
                new_runs[rid] = dict(by_en[en])
            elif rid in old_runs and i18n.normalise(old_runs[rid].get("en", "")) == en:
                new_runs[rid] = dict(old_runs[rid])
            else:
                todo.append((rid, en))
    mem["runs"] = new_runs
    i18n.save_memory(mem)
    print(f"re-keyed; {len(todo)} paragraph(s) need a French translation")
    for rid, en in todo:
        print(f"  {rid:28s} {en[:80]}")


if __name__ == "__main__":
    main()
