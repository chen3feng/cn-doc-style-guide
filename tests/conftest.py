"""Pytest shared fixtures.

The ``src`` directory is added to ``sys.path`` declaratively via
``[tool.pytest.ini_options].pythonpath`` in ``pyproject.toml``, so tests
can simply ``from cndocstyle import check`` regardless of where pytest is
invoked from. This file is kept to reserve a place for future fixtures.
"""

from __future__ import annotations

import os
import sys

_TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
