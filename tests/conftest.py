import sys
from pathlib import Path

# Agrega el directorio backend/src para simplificar los imports en las pruebas
ROOT = Path(__file__).resolve().parents[1]
backend_src = ROOT / "backend" / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if backend_src.exists() and str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Carga el paquete backend para registrar sus submódulos en "src"
try:  # nosec B001
    import backend  # noqa: F401
except Exception:
    pass
