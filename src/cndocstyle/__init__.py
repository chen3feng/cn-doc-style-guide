"""cndocstyle - tools for enforcing the cn-doc-style-guide on Markdown docs.

Public submodules:

- ``check``     : scan Markdown for style-guide violations.
- ``formatter`` : apply safe auto-fixes.
- ``preview``   : print a unified diff of what ``formatter`` would change.

The package intentionally exposes no top-level API; import submodules
directly.
"""

from __future__ import annotations

__all__ = ["check", "formatter", "preview"]
