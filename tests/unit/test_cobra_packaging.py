import ast
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from pcobra.cobra.packaging import (
    MANIFEST_NAME,
    construir_paquete,
    crear_paquete,
    extraer_paquete,
    inspeccionar_paquete,
    validar_paquete,
)


def test_packaging_no_importa_lexer_parser():
    import pcobra.cobra.packaging as packaging

    tree = ast.parse(Path(packaging.__file__).read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )

    forbidden_modules = {
        module
        for module in imported_modules
        if module in {"pcobra.cobra.core", "pcobra.cobra.core.lexer", "pcobra.cobra.core.parser"}
        or module.endswith((".lexer", ".parser"))
    }

    assert forbidden_modules == set()


def test_paquete_cobra_conserva_estructura_y_recursos(tmp_path: Path):
    proyecto = tmp_path / "demo"
    crear_paquete(proyecto, nombre="demo", version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    (proyecto / "README.md").write_text("# Demo\n", encoding="utf-8")
    (proyecto / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (proyecto / "assets").mkdir()
    (proyecto / "assets" / "dato.txt").write_text("recurso", encoding="utf-8")

    paquete = construir_paquete(proyecto, tmp_path / "demo.co")

    info = validar_paquete(paquete)
    assert info.manifest["format"] == "cobra-package-v1"
    assert MANIFEST_NAME in info.files
    assert "src/main.cobra" in info.files
    assert "Dockerfile" in info.files
    assert "assets/dato.txt" in info.files

    inspeccion = inspeccionar_paquete(paquete)
    assert inspeccion.checksum

    destino = extraer_paquete(paquete, tmp_path / "instalado")
    assert (destino / "src" / "main.cobra").read_text(encoding="utf-8") == "imprimir('hola')\n"


def _crear_zip_con_manifest(tmp_path: Path, manifest: dict, files: dict[str, bytes] | None = None) -> Path:
    paquete = tmp_path / "manual.co"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False))
        for name, content in (files or {}).items():
            zf.writestr(name, content)
    return paquete


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validar_paquete_rechaza_manifest_incompleto(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": _sha256(contenido)},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(ValueError, match="version"):
        validar_paquete(paquete)


def test_validar_paquete_rechaza_archivo_extra_no_declarado(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": _sha256(contenido)},
        },
        {"src/main.cobra": contenido, "extra.txt": b"sobrante"},
    )

    with pytest.raises(ValueError, match="Archivos no declarados"):
        validar_paquete(paquete)


def test_validar_paquete_rechaza_checksum_ausente(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(ValueError, match="Faltan checksums"):
        validar_paquete(paquete)


def test_validar_paquete_rechaza_checksum_no_string(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": 123},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(ValueError, match="Checksum inválido para src/main\\.cobra: debe ser una cadena"):
        validar_paquete(paquete)


def test_validar_paquete_rechaza_checksum_demasiado_corto(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": "abc123"},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(ValueError, match="Checksum inválido para src/main\\.cobra: debe tener 64 caracteres"):
        validar_paquete(paquete)


def test_validar_paquete_rechaza_checksum_no_hexadecimal(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": "g" * 64},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(
        ValueError,
        match="Checksum inválido para src/main\\.cobra: debe contener solo caracteres hexadecimales",
    ):
        validar_paquete(paquete)


def test_validar_paquete_acepta_checksum_valido(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": _sha256(contenido)},
        },
        {"src/main.cobra": contenido},
    )

    info = validar_paquete(paquete)

    assert info.manifest["checksums"]["src/main.cobra"] == _sha256(contenido)


def test_validar_paquete_rechaza_formato_invalido(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    paquete = _crear_zip_con_manifest(
        tmp_path,
        {
            "format": "cobra-package-v0",
            "name": "demo",
            "version": "1.0.0",
            "files": ["src/main.cobra"],
            "checksums": {"src/main.cobra": _sha256(contenido)},
        },
        {"src/main.cobra": contenido},
    )

    with pytest.raises(ValueError, match="Formato de paquete no soportado"):
        validar_paquete(paquete)


def test_es_paquete_cobra_rechaza_co_fuente_texto(tmp_path: Path):
    fuente = tmp_path / "programa.co"
    fuente.write_text("imprimir('hola')\n", encoding="utf-8")

    from pcobra.cobra.packaging import es_paquete_cobra

    assert es_paquete_cobra(fuente) is False


def test_es_paquete_cobra_rechaza_zip_sin_manifest(tmp_path: Path):
    paquete = tmp_path / "sin-manifest.co"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("src/main.cobra", "imprimir('hola')\n")

    from pcobra.cobra.packaging import es_paquete_cobra

    assert es_paquete_cobra(paquete) is False


def test_es_paquete_cobra_acepta_zip_con_manifest(tmp_path: Path):
    paquete = tmp_path / "con-manifest.co"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps({"format": "cobra-package-v1"}))
        zf.writestr("src/main.cobra", "imprimir('hola')\n")

    from pcobra.cobra.packaging import es_paquete_cobra

    assert es_paquete_cobra(paquete) is True


def _corromper_contenido_paquete(paquete: Path, nombre: str, contenido: bytes) -> None:
    original = paquete.with_suffix(".tmp.co")
    paquete.rename(original)
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == nombre:
                data = contenido
            dst.writestr(item, data)
    original.unlink()


def test_cli_paquete_verificar_integridad_exitosa(tmp_path: Path, capsys):
    from argparse import Namespace

    from pcobra.cobra.cli.commands.package_cmd import PaqueteCommand

    proyecto = tmp_path / "demo"
    crear_paquete(proyecto, nombre="demo", version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    paquete = construir_paquete(proyecto, tmp_path / "demo.co")

    codigo = PaqueteCommand().run(Namespace(accion="verificar", paquete=paquete))

    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Integridad válida" in salida


def test_cli_paquete_verificar_integridad_falla_por_checksum_alterado(tmp_path: Path, capsys):
    from argparse import Namespace

    from pcobra.cobra.cli.commands.package_cmd import PaqueteCommand

    proyecto = tmp_path / "demo"
    crear_paquete(proyecto, nombre="demo", version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    paquete = construir_paquete(proyecto, tmp_path / "demo.co")
    _corromper_contenido_paquete(paquete, "src/main.cobra", b"imprimir('adios')\n")

    codigo = PaqueteCommand().run(Namespace(accion="verificar", paquete=paquete))

    salida = capsys.readouterr().out
    assert codigo == 1
    assert "Integridad fallida" in salida
