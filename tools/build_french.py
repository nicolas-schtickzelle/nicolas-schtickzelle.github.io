#!/usr/bin/env python3
"""
Generate the French pages in fr/ from the English pages + data/translations.fr.json.

    python tools/build_french.py --dump     # list every translatable run + its id
    python tools/build_french.py --status   # what is missing or stale
    python tools/build_french.py            # write fr/*.qmd

NEVER edit fr/*.qmd by hand — this script overwrites them. Edit the English page
(for structure and English wording) or data/translations.fr.json (for the French
wording).
"""
import argparse
import os
import re
import shutil
import sys

import i18n  # noqa: E402  (same directory)

HERE = i18n.HERE
FR = os.path.join(HERE, "fr")

BANNER = (
    "<!-- GENERATED FILE — do not edit.\n"
    "     Source: ../{page} + ../data/translations.fr.json\n"
    "     Regenerate with: python tools/build_french.py -->\n"
)


def rewrite_paths(text):
    """French pages live one level down, so asset paths gain a ../"""
    text = text.replace("](assets/", "](../assets/")
    text = text.replace('="assets/', '="../assets/')
    text = text.replace("url('assets/", "url('../assets/")
    text = text.replace('url("assets/', 'url("../assets/')
    text = text.replace("_includes/bibliometry.en.md", "_includes/bibliometry.fr.md")
    return text


def french_front_matter(fm, page, mem):
    over = mem.get("_pages", {}).get(page, {})
    out = fm
    for key, val in over.items():
        pattern = re.compile(rf'^{key}:.*$', re.MULTILINE)
        line = f'{key}: "{val}"'
        out = pattern.sub(line, out) if pattern.search(out) else out.replace(
            "---\n", f"---\n{line}\n", 1
        )
    return out


def build_page(page, mem, report):
    """Splice French text in place of each English run, keeping all structure."""
    fm, lines, runs, ids = i18n.scan(page)
    out, cursor = [], 0
    for (start, end, run_lines), rid in zip(runs, ids):
        out.extend(lines[cursor:start])
        cursor = end
        en = i18n.run_text(run_lines)
        entry = mem["runs"].get(rid)
        if entry and not entry.get("en"):
            # First time we see this pair: stamp the English so that a later
            # edit to the English can be detected as "stale".
            entry["en"] = i18n.normalise(en)
            report["stamped"] += 1
        if not entry:
            report["missing"].append((rid, i18n.normalise(en)[:70]))
            out.extend(run_lines)
        elif i18n.normalise(entry.get("en", "")) != i18n.normalise(en):
            report["stale"].append((rid, i18n.normalise(en)[:70]))
            out.extend(run_lines)
        else:
            out.extend(entry["fr"].split("\n"))
    out.extend(lines[cursor:])
    return french_front_matter(fm, page, mem) + rewrite_paths("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true", help="list run ids and English previews")
    ap.add_argument("--status", action="store_true", help="report missing/stale translations only")
    args = ap.parse_args()

    mem = i18n.load_memory()

    if args.dump:
        for page in i18n.PAGES:
            _, _, runs, ids = i18n.scan(page)
            print(f"\n### {page}")
            for (_, _, rl), rid in zip(runs, ids):
                n = rid.split("#")[1]
                print(f"{n:>3}  {i18n.normalise(i18n.run_text(rl))[:88]}")
        return

    report = {"missing": [], "stale": [], "stamped": 0}
    os.makedirs(FR, exist_ok=True)
    rendered = {}
    for page in i18n.FR_PAGES:
        rendered[page] = build_page(page, mem, report)

    if args.status:
        print(f"missing: {len(report['missing'])}   stale: {len(report['stale'])}")
        for rid, prev in report["missing"]:
            print(f"  MISSING {rid:32s} {prev}")
        for rid, prev in report["stale"]:
            print(f"  STALE   {rid:32s} {prev}")
        return

    for page, text in rendered.items():
        with open(os.path.join(FR, page), "w", encoding="utf-8") as fh:
            fh.write(BANNER.format(page=page) + text)

    # The French project is a Quarto project of its own, so it needs its own
    # copy of the stylesheet (Quarto cannot reach outside the project folder).
    shutil.copy2(os.path.join(HERE, "styles.scss"), os.path.join(FR, "styles.scss"))

    src_inc = os.path.join(HERE, "_includes")
    if os.path.isdir(src_inc):
        dst_inc = os.path.join(FR, "_includes")
        os.makedirs(dst_inc, exist_ok=True)
        for name in os.listdir(src_inc):
            shutil.copy2(os.path.join(src_inc, name), os.path.join(dst_inc, name))

    if report["stamped"]:
        i18n.save_memory(mem)

    n = len(i18n.FR_PAGES)
    print(f"wrote {n} French pages to fr/")
    if report["missing"] or report["stale"]:
        print(
            f"  {len(report['missing'])} run(s) untranslated, "
            f"{len(report['stale'])} stale — those stayed in English.",
            file=sys.stderr,
        )
        print("  Run with --status to see which.", file=sys.stderr)


if __name__ == "__main__":
    main()
