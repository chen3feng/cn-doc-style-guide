#!/usr/bin/env python3
"""Scan Chinese Markdown docs for style-guide violations.

Reports, for each ``.md`` file, any occurrences of the following patterns,
with file / line / column / offending snippet::

    han+ascii     Han character immediately followed by ASCII letter/digit.
    ascii+han     ASCII letter/digit immediately followed by a Han character.
    han,          Han character immediately followed by half-width ``,``.
    han:          Han character immediately followed by half-width ``:``
                  (``://`` is ignored to avoid URL false positives).
    han;          Han character immediately followed by half-width ``;``.
    han?          Han character immediately followed by half-width ``?``.
    han!          Han character immediately followed by half-width ``!``.
    han()         Han character adjacent to ASCII parenthesis.
    multi-space   Two or more spaces between two Han characters.
    ascii-quote   Han character adjacent to ASCII ``"``.

Fenced code blocks, inline code and the URL part of Markdown links are
blanked out before matching, so false positives from code / URLs are rare.
Note that ``multi-space`` around inline code is a known benign false
positive (after the code is blanked, normal single spaces look doubled).

Usage::

    python3 -m cndocstyle.check PATH [PATH ...]

Exit code is non-zero when any issue is found.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HAN = r"[\u4e00-\u9fff]"

INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK_URL = re.compile(r"(?<=\])\([^)]*\)")

PATTERNS = [
    ("han+ascii", re.compile(rf"{HAN}[A-Za-z0-9]")),
    ("ascii+han", re.compile(rf"[A-Za-z0-9]{HAN}")),
    ("han,", re.compile(rf"{HAN},")),
    ("han:", re.compile(rf"{HAN}:(?!//)")),
    ("han;", re.compile(rf"{HAN};")),
    ("han?", re.compile(rf"{HAN}\?")),
    ("han!", re.compile(rf"{HAN}!")),
    ("han()", re.compile(rf"{HAN}\(|\){HAN}")),
    ("multi-space", re.compile(rf"{HAN} {{2,}}{HAN}")),
    ("ascii-quote", re.compile(rf'{HAN}"|"{HAN}')),
]

_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _blank(m):
    return " " * len(m.group(0))


def scan_line(line: str):
    stripped = INLINE_CODE.sub(_blank, line)
    stripped = LINK_URL.sub(_blank, stripped)
    for name, pat in PATTERNS:
        for m in pat.finditer(stripped):
            yield name, m.start(), m.group(0)


def scan_file(path: str):
    out = []
    in_fence = False
    fence_marker = ""
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            m = _FENCE_RE.match(line)
            if m:
                marker = m.group(1)
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_fence = False
                    fence_marker = ""
                continue
            if in_fence:
                continue
            text = line.rstrip("\n")
            for name, col, _snip in scan_line(text):
                out.append((i, col, name, text))
    return out


def _iter_md_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".md"):
                yield p
        elif os.path.isdir(p):
            for dp, _, fs in os.walk(p):
                for name in sorted(fs):
                    if name.endswith(".md"):
                        yield os.path.join(dp, name)
        else:
            print(f"warning: path not found: {p}", file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="markdown files or directories")
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="NAME",
        help="skip a rule (may be repeated), e.g. --exclude multi-space",
    )
    args = ap.parse_args(argv)

    exclude = set(args.exclude)
    total = 0
    for path in _iter_md_files(args.paths):
        issues = [x for x in scan_file(path) if x[2] not in exclude]
        if not issues:
            continue
        print(f"===== {path} ({len(issues)}) =====")
        for ln, col, name, text in issues:
            print(f"  L{ln}:{col} [{name}] {text}")
        total += len(issues)
    print(f"TOTAL: {total}", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
