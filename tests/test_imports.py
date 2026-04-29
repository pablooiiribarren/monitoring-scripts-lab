# tests/test_imports.py
from pathlib import Path
import sys


# Ensure that the repo root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_imports() -> None:
    # Smoke test: only checks that the modules charge without crashing
    import app.config  # noqa: F401
    import app.logger  # noqa: F401
    import app.checks  # noqa: F401
    import app.monitor  # noqa: F401
