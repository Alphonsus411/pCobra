import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import standard_library.archivo as archivo


def test_archivo(tmp_path):
    ruta = tmp_path / "f.txt"
    archivo.escribir(ruta, "hola")
    assert archivo.existe(ruta)
    archivo.adjuntar(ruta, " mundo")
    assert archivo.leer(ruta) == "hola mundo"
    os.remove(ruta)
    assert not archivo.existe(ruta)

