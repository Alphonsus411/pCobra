import os
from pathlib import Path

import pytest

from pcobra.corelibs import ruta


def test_superficie_publica_ruta() -> None:
    assert ruta.__all__ == [
        "unir",
        "normalizar",
        "nombre",
        "extension",
        "padre",
        "existe",
        "es_absoluta",
        "absoluta",
        "relativa",
    ]


def test_operaciones_basicas_de_ruta(tmp_path: Path) -> None:
    archivo = tmp_path / "datos" / "entrada.txt"
    archivo.parent.mkdir()
    archivo.write_text("cobra", encoding="utf-8")

    assert ruta.unir(tmp_path, "datos", "entrada.txt") == str(archivo)
    assert ruta.normalizar(f"datos{os.sep}.{os.sep}entrada.txt") == os.path.join(
        "datos", "entrada.txt"
    )
    assert ruta.nombre(archivo) == "entrada.txt"
    assert ruta.extension(archivo) == ".txt"
    assert ruta.padre(archivo) == str(archivo.parent)
    assert ruta.existe(archivo) is True
    assert ruta.es_absoluta(archivo) is True
    assert ruta.absoluta(".") == str(Path(".").absolute())
    assert ruta.relativa(archivo, tmp_path) == os.path.join("datos", "entrada.txt")


def test_argumentos_invalidos_generan_mensajes_deterministas() -> None:
    with pytest.raises(ValueError, match="partes debe contener al menos una ruta"):
        ruta.unir()

    with pytest.raises(ValueError, match=r"partes\[1\] no puede estar vacía"):
        ruta.unir("base", "")

    with pytest.raises(ValueError, match="ruta no puede estar vacía"):
        ruta.normalizar("")

    with pytest.raises(ValueError, match="base no puede estar vacía"):
        ruta.relativa("archivo.txt", "")

    with pytest.raises(
        TypeError, match="ruta debe ser una ruta de texto o compatible con os.PathLike"
    ):
        ruta.nombre(123)
