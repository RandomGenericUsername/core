# Root conftest.py — anchors pytest rootdir for the uv workspace.
# Adds each package's src/ directory to sys.path so that workspace-wide
# test invocations can import all packages regardless of which package's
# pyproject.toml is active.
import sys
from pathlib import Path

_root = Path(__file__).parent
for _pkg_src in [
    "packages/logging/src",
    "packages/pipeline/src",
    "packages/package-manager/src",
    "packages/container-manager/src",
]:
    _p = str(_root / _pkg_src)
    if _p not in sys.path:
        sys.path.insert(0, _p)
