#!/usr/bin/env python3
"""Print a unified diff of what ``formatter`` would change for a file.

Useful for spot-checking the auto-formatter before applying it.

Usage::

    python3 -m cndocstyle.preview FILE.md [FILE.md ...]
"""

from __future__ import annotations

import difflib
import sys

from . import formatter as fmt


def preview(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        original = f.read()
    new = fmt.fix_text(original)
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=path + " (old)",
            tofile=path + " (new)",
        )
    )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    any_diff = False
    for path in argv:
        diff = preview(path)
        if diff:
            any_diff = True
            sys.stdout.write(diff)
    return 1 if any_diff else 0


if __name__ == "__main__":
    sys.exit(main())
