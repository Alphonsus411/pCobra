from pathlib import Path
import stat
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

import pcobra.corelibs.compresion as compresion
from pcobra.corelibs.compresion import crear_zip, extraer_zip, listar_zip


@pytest.fixture(autouse=True)
def _sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))


def _rel(tmp_path: Path, ruta: Path) -> Path:
    return ruta.relative_to(tmp_path)


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
    rutas = extraer_zip(_rel(tmp_path, destino_zip), _rel(tmp_path, destino))

    assert (
        sorted(Path(ruta).relative_to(destino).as_posix() for ruta in rutas) == nombres
    )
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
        extraer_zip(_rel(tmp_path, origen), "destino")


@pytest.mark.parametrize(
    "nombre",
    [
        "../escape.txt",
        "..\\escape.txt",
        "docs/../escape.txt",
        "/tmp/escape.txt",
        "C:/escape.txt",
        "C:\\escape.txt",
    ],
)
def test_extraer_zip_rechaza_path_traversal(tmp_path: Path, nombre: str) -> None:
    origen = tmp_path / "malicioso.zip"
    with ZipFile(origen, "w") as archivo_zip:
        archivo_zip.writestr(nombre, "peligro")

    with pytest.raises(ValueError):
        extraer_zip(_rel(tmp_path, origen), "destino")

    assert not (tmp_path / "escape.txt").exists()


def test_extraer_zip_rechaza_origen_y_destino_exteriores(tmp_path: Path) -> None:
    with ZipFile(tmp_path / "archivo.zip", "w"):
        pass
    with pytest.raises(ValueError):
        extraer_zip("../fuera.zip", "destino")
    with pytest.raises(ValueError):
        extraer_zip("archivo.zip", "../destino")
    with pytest.raises(ValueError):
        extraer_zip("/tmp/archivo.zip", "destino")
    with pytest.raises(ValueError):
        extraer_zip("C:\\archivo.zip", "destino")


def test_extraer_zip_rechaza_symlink_de_destino(tmp_path: Path) -> None:
    origen = tmp_path / "archivo.zip"
    with ZipFile(origen, "w") as archivo_zip:
        archivo_zip.writestr("dato.txt", "dato")
    exterior = tmp_path.parent / f"{tmp_path.name}-exterior"
    exterior.mkdir()
    (tmp_path / "enlace").symlink_to(exterior, target_is_directory=True)

    with pytest.raises(ValueError):
        extraer_zip("archivo.zip", "enlace")

    assert not (exterior / "dato.txt").exists()


def test_extraer_zip_rechaza_enlaces_y_tipos_especiales(tmp_path: Path) -> None:
    for tipo in (stat.S_IFLNK, stat.S_IFIFO):
        origen = tmp_path / f"tipo-{tipo}.zip"
        info = ZipInfo("entrada")
        info.create_system = 3
        info.external_attr = (tipo | 0o644) << 16
        with ZipFile(origen, "w") as archivo_zip:
            archivo_zip.writestr(info, "contenido")
        with pytest.raises(ValueError, match="Tipo"):
            extraer_zip(origen.name, f"destino-{tipo}")


def test_extraer_zip_aplica_limites_de_metadatos(tmp_path: Path, monkeypatch) -> None:
    casos = [
        ("_MAX_ENTRADAS", 2, [("a", b"1"), ("b", b"2"), ("c", b"3")]),
        ("_MAX_BYTES_ENTRADA", 2, [("grande", b"123")]),
        ("_MAX_BYTES_TOTALES", 3, [("a", b"12"), ("b", b"12")]),
    ]
    for indice, (limite, valor, entradas) in enumerate(casos):
        origen = tmp_path / f"limite-{indice}.zip"
        with ZipFile(origen, "w") as archivo_zip:
            for nombre, contenido in entradas:
                archivo_zip.writestr(nombre, contenido)
        monkeypatch.setattr(compresion, limite, valor)
        with pytest.raises(ValueError):
            extraer_zip(origen.name, f"destino-limite-{indice}")
        monkeypatch.undo()
        monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))


def test_extraer_zip_rechaza_ratio_extrema_y_miles_de_entradas(
    tmp_path: Path, monkeypatch
) -> None:
    bomba = tmp_path / "ratio.zip"
    with ZipFile(bomba, "w", ZIP_DEFLATED) as archivo_zip:
        archivo_zip.writestr("ceros", b"0" * 10_000)
    monkeypatch.setattr(compresion, "_MAX_RATIO_COMPRESION", 2)
    with pytest.raises(ValueError, match="ratio"):
        extraer_zip(bomba.name, "destino-ratio")

    multitud = tmp_path / "miles.zip"
    with ZipFile(multitud, "w") as archivo_zip:
        for indice in range(1_001):
            archivo_zip.writestr(f"{indice}.txt", b"")
    monkeypatch.setattr(compresion, "_MAX_ENTRADAS", 1_000)
    with pytest.raises(ValueError, match="cantidad"):
        extraer_zip(multitud.name, "destino-miles")


def test_error_no_publica_resultados_ni_borra_destino(
    tmp_path: Path, monkeypatch
) -> None:
    origen = tmp_path / "archivo.zip"
    with ZipFile(origen, "w") as archivo_zip:
        archivo_zip.writestr("primero.txt", b"12")
        archivo_zip.writestr("segundo.txt", b"34")
    destino = tmp_path / "destino"
    destino.mkdir()
    conservado = destino / "existente.txt"
    conservado.write_text("intacto", encoding="utf-8")
    monkeypatch.setattr(compresion, "_MAX_BYTES_TOTALES", 3)

    with pytest.raises(ValueError):
        extraer_zip(origen.name, destino.name)

    assert conservado.read_text(encoding="utf-8") == "intacto"
    assert not (destino / "primero.txt").exists()
    assert not any(ruta.name.startswith(".pcobra-zip-") for ruta in destino.iterdir())


def test_extraer_zip_rechaza_archivo_existente(tmp_path: Path) -> None:
    origen = tmp_path / "archivo.zip"
    with ZipFile(origen, "w") as archivo_zip:
        archivo_zip.writestr("dato.txt", "nuevo")
    destino = tmp_path / "destino"
    destino.mkdir()
    existente = destino / "dato.txt"
    existente.write_text("anterior", encoding="utf-8")

    with pytest.raises(FileExistsError):
        extraer_zip(origen.name, destino.name)

    assert existente.read_text(encoding="utf-8") == "anterior"
