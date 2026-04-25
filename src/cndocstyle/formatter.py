#!/usr/bin/env python3
"""Auto-format Chinese Markdown docs per cn-doc-style-guide.

What it does (safe transformations only):

- Insert a half-width space between CJK (Han) and ASCII letters/digits.
- Replace half-width punctuation directly after a Han character with the
  corresponding full-width form: ``, -> ，``  ``: -> ：``  ``; -> ；``
  ``? -> ？``  ``! -> ！``. Colon preceding ``//`` (e.g. ``http://``) is
  preserved.
- Replace ASCII parentheses adjacent to a Han character with full-width
  ``（`` / ``）``.
- Collapse multiple spaces between Han characters into a single space.
- Skip fenced code blocks (```...``` / ~~~...~~~), inline code (`` `...` ``),
  the URL part of Markdown links/images ``](...)``, and HTML tags.

What it does NOT do (to avoid false positives):

- It does not convert ``"`` to curly quotes. ``"`` is often part of code
  snippets, URLs, or English phrases. Convert them by hand when needed.
- It does not touch the period ``.``. File names / version numbers would be
  corrupted.

Usage::

    # Dry run (default): print files that WOULD change.
    python3 -m cndocstyle.formatter PATH [PATH ...]

    # Apply in place.
    python3 -m cndocstyle.formatter --apply PATH [PATH ...]

``PATH`` may be a ``.md`` file or a directory (recursively scanned).
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HAN = r"[\u4e00-\u9fff]"

INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
# Only protect the URL/path part of links/images (the parenthesised part).
# The link TEXT between ``[]`` is deliberately left exposed so that CJK/ASCII
# spacing rules still apply inside link labels.
LINK_URL_RE = re.compile(r"(?<=\])\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>\n]+>")

PLACEHOLDER_FMT = "\x00PH{}\x00"
_PLACEHOLDER_RE = re.compile(r"\x00PH(\d+)\x00")


def _protect(text: str) -> tuple[str, list[str]]:
    """Replace protected spans with placeholders; return (text, restore)."""
    restore: list[str] = []

    def sub(m: re.Match) -> str:
        restore.append(m.group(0))
        return PLACEHOLDER_FMT.format(len(restore) - 1)

    text = INLINE_CODE_RE.sub(sub, text)
    text = LINK_URL_RE.sub(sub, text)
    text = HTML_TAG_RE.sub(sub, text)
    return text, restore


def _restore(text: str, restore: list[str]) -> str:
    def sub(m: re.Match) -> str:
        return restore[int(m.group(1))]

    # Loop because a restored span may itself contain placeholders (e.g. a
    # link whose URL contained inline-code-like characters).
    while _PLACEHOLDER_RE.search(text):
        text = _PLACEHOLDER_RE.sub(sub, text)
    return text


# Explicit compiled regexes - avoid re.escape pitfalls inside f-strings.
_RE_COLON = re.compile(rf"({HAN}):(?!//)")
_RE_COMMA = re.compile(rf"({HAN}),")
_RE_SEMI = re.compile(rf"({HAN});")
_RE_QMARK = re.compile(rf"({HAN})\?")
_RE_EXCL = re.compile(rf"({HAN})!")
_RE_LPAREN = re.compile(rf"({HAN})\(")
_RE_RPAREN = re.compile(rf"\)({HAN})")


def _fix_punct(text: str) -> str:
    text = _RE_COLON.sub(lambda m: m.group(1) + "：", text)
    text = _RE_COMMA.sub(lambda m: m.group(1) + "，", text)
    text = _RE_SEMI.sub(lambda m: m.group(1) + "；", text)
    text = _RE_QMARK.sub(lambda m: m.group(1) + "？", text)
    text = _RE_EXCL.sub(lambda m: m.group(1) + "！", text)
    text = _RE_LPAREN.sub(lambda m: m.group(1) + "（", text)
    text = _RE_RPAREN.sub(lambda m: "）" + m.group(1), text)
    return text


_RE_HAN_ASCII = re.compile(rf"({HAN})([A-Za-z0-9])")
_RE_ASCII_HAN = re.compile(rf"([A-Za-z0-9])({HAN})")
_RE_MULTI_SPACE = re.compile(rf"({HAN}) {{2,}}({HAN})")


def _fix_spacing(text: str) -> str:
    text = _RE_HAN_ASCII.sub(r"\1 \2", text)
    text = _RE_ASCII_HAN.sub(r"\1 \2", text)
    text = _RE_MULTI_SPACE.sub(r"\1 \2", text)
    return text


def fix_line(line: str) -> str:
    """Return the style-normalised form of a single markdown line."""
    protected, restore = _protect(line)
    protected = _fix_punct(protected)
    protected = _fix_spacing(protected)
    return _restore(protected, restore)


_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def fix_text(text: str) -> str:
    """Return the style-normalised form of a full markdown document."""
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines(keepends=True):
        m = _FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        out.append(fix_line(line))
    return "".join(out)


def fix_file(path: str, apply: bool = False) -> bool:
    """Format one file. Return True if content would change."""
    with open(path, encoding="utf-8") as f:
        original = f.read()
    new = fix_text(original)
    if new == original:
        return False
    if apply:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return True


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
        "--apply", action="store_true", help="rewrite files in place (default is dry run)"
    )
    args = ap.parse_args(argv)

    changed = 0
    total = 0
    for p in _iter_md_files(args.paths):
        total += 1
        if fix_file(p, apply=args.apply):
            changed += 1
            print(("FIX " if args.apply else "DRY "), p)
    print(
        f"{changed}/{total} file(s) {'changed' if args.apply else 'would change'}", file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
