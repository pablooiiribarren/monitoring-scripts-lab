# tests/test_imports.py
from pathlib import Path
import sys


# Asegurar que la raíz del repo está en sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_imports() -> None:
    # Test de humo: solo comprueba que los módulos cargan sin petar
    import app.config  # noqa: F401
    import app.logger  # noqa: F401
    import app.checks  # noqa: F401
    import app.monitor  # noqa: F401
