import sys
from pathlib import Path

# Añade el directorio ``src`` al ``PYTHONPATH`` para simplificar los imports en las pruebas
ROOT = Path(__file__).resolve().parents[1]
src_path = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Carga opcionalmente el paquete ``backend`` para mantener compatibilidad
try:  # nosec B001
    import backend  # noqa: F401
except Exception:
    pass
