import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))

import standard_library.logica as logica


def test_logica():
    assert logica.conjuncion(True, True) is True
    assert logica.conjuncion(True, False) is False
    assert logica.disyuncion(False, True) is True
    assert logica.disyuncion(False, False) is False
    assert logica.negacion(True) is False

