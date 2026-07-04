from pathlib import Path
from zipfile import ZipFile

import pytest

from pcobra.corelibs.compresion import crear_zip, extraer_zip, listar_zip


def test_crear_listar_y_extraer_zip(tmp_path: Path) -> None:
    base = tmp_path / "entrada"
    carpeta = base / "docs"
    carpeta.mkdir(parents=True)
    (carpeta / "uno.txt").write_text("uno", encoding="utf-8")
    (carpeta / "dos.txt").write_text("dos", encoding="utf-8")
    destino_zip = tmp_path / "salida" / "datos.zip"

    nombres = crear_zip(destino_zip, carpeta, base=base)

    assert nombres == ["docs/dos.txt", "docs/uno.txt"]
    assert listar_zip(destino_zip) == nombres

    destino = tmp_path / "extraido"
    rutas = extraer_zip(destino_zip, destino)

    assert sorted(Path(ruta).relative_to(destino).as_posix() for ruta in rutas) == nombres
    assert (destino / "docs" / "uno.txt").read_text(encoding="utf-8") == "uno"
    assert (destino / "docs" / "dos.txt").read_text(encoding="utf-8") == "dos"


def test_validar_rutas_a_comprimir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        crear_zip(tmp_path / "datos.zip", tmp_path / "no-existe.txt")


def test_validar_origen_para_listar_y_extraer(tmp_path: Path) -> None:
    origen = tmp_path / "no-existe.zip"

    with pytest.raises(FileNotFoundError):
        listar_zip(origen)
    with pytest.raises(FileNotFoundError):
        extraer_zip(origen, tmp_path / "destino")


@pytest.mark.parametrize(
    "nombre",
    [
        "../escape.txt",
        "..\\escape.txt",
        "docs/../escape.txt",
        "/tmp/escape.txt",
        "C:/escape.txt",
    ],
)
def test_extraer_zip_rechaza_path_traversal(tmp_path: Path, nombre: str) -> None:
    origen = tmp_path / "malicioso.zip"
    with ZipFile(origen, "w") as archivo_zip:
        archivo_zip.writestr(nombre, "peligro")

    with pytest.raises(ValueError):
        extraer_zip(origen, tmp_path / "destino")

    assert not (tmp_path / "escape.txt").exists()
