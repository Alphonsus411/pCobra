import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import standard_library.logica as logica


def test_logica():
    assert logica.conjuncion(True, True) is True
    assert logica.conjuncion(True, False) is False
    assert logica.disyuncion(False, True) is True
    assert logica.disyuncion(False, False) is False
    assert logica.negacion(True) is False

