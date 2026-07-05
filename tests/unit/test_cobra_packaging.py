import ast
import hashlib
import json
import stat
import zipfile
from pathlib import Path

import pytest

from pcobra.cobra.packaging import (
    MANIFEST_NAME,
    PackageManifest,
    construir_paquete,
    crear_paquete,
    extraer_paquete,
    inspeccionar_paquete,
    manifest_from_dict,
    manifest_to_dict,
    normalizar_nombre_paquete,
    validar_paquete,
    validar_version_paquete,
)


def test_package_manifest_minimo_compatible():
    data = {
        "format": "cobra-package-v1",
        "name": "demo",
        "version": "1.0.0",
        "files": [],
        "checksums": {},
    }

    manifest = manifest_from_dict(data)

    assert manifest == PackageManifest(
        format="cobra-package-v1",
        name="demo",
        version="1.0.0",
        files=[],
        checksums={},
    )
    assert manifest_to_dict(manifest) == data


def test_package_manifest_acepta_campos_extra_permitidos():
    data = {
        "format": "cobra-package-v1",
        "name": "demo",
        "version": "1.0.0",
        "files": [],
        "checksums": {},
        "description": "Paquete de prueba",
        "authors": ["Equipo Cobra"],
        "license": "MIT",
        "homepage": "https://example.test/demo",
        "dependencies": {"Std Lib": "1.2.3"},
    }

    manifest = manifest_from_dict(data)

    assert manifest.description == "Paquete de prueba"
    assert manifest.authors == ["Equipo Cobra"]
    assert manifest.license == "MIT"
    assert manifest.homepage == "https://example.test/demo"
    assert manifest.dependencies == {"std-lib": "1.2.3"}
    expected = {**data, "dependencies": {"std-lib": "1.2.3"}}
    assert manifest_to_dict(manifest) == expected


def test_package_manifest_normaliza_nombres_y_preserva_specs_de_dependencias():
    manifest = manifest_from_dict(
        {
            "format": "cobra-package-v1",
            "name": "demo",
            "version": "1.0.0",
            "files": [],
            "checksums": {},
            "dependencies": {
                "  Paquete Demo ": "^1.2.3",
                "util.core": 2,
            },
        }
    )

    assert manifest.dependencies == {
        "paquete-demo": "^1.2.3",
        "util.core": "2",
    }


@pytest.mark.parametrize(
    ("dependencies", "match"),
    [
        ({"demo/evil": "1.0.0"}, "Nombre de paquete inválido"),
        ([], "dependencies como objeto"),
    ],
)
def test_package_manifest_rechaza_dependencias_invalidas(dependencies, match):
    with pytest.raises(ValueError, match=match):
        manifest_from_dict(
            {
                "format": "cobra-package-v1",
                "name": "demo",
                "version": "1.0.0",
                "files": [],
                "checksums": {},
                "dependencies": dependencies,
            }
        )


def test_package_manifest_rechaza_formato_no_soportado():
    with pytest.raises(ValueError, match="Formato de paquete no soportado"):
        manifest_from_dict(
            {
                "format": "cobra-package-v0",
                "name": "demo",
                "version": "1.0.0",
                "files": [],
                "checksums": {},
            }
        )


def test_normalizar_nombre_paquete_aplica_politica_documentada():
    assert (
        normalizar_nombre_paquete("  Paquete Demo_1.Modulo  ")
        == "paquete-demo_1.modulo"
    )


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        "   ",
        "demo/evil",
        r"demo\evil",
        "demo..evil",
        ".demo",
        "demo.",
        "demo@evil",
        "démø",
    ],
)
def test_normalizar_nombre_paquete_rechaza_nombres_invalidos(nombre):
    with pytest.raises(ValueError, match="Nombre de paquete inválido"):
        normalizar_nombre_paquete(nombre)


def test_validar_version_paquete_acepta_semver_simple():
    assert validar_version_paquete(" 1.2.3 ") == "1.2.3"
    assert validar_version_paquete("1.2.3-beta.1+build.5") == "1.2.3-beta.1+build.5"


@pytest.mark.parametrize(
    "version",
    ["", "1", "1.2", "01.2.3", "1.2.3.4", "v1.2.3", "1.2.3 beta"],
)
def test_validar_version_paquete_rechaza_versiones_invalidas(version):
    with pytest.raises(ValueError, match="Versión de paquete inválida"):
        validar_version_paquete(version)


def test_crear_y_construir_paquete_normalizan_identidad_consistentemente(
    tmp_path: Path,
):
    proyecto = tmp_path / "demo"

    crear_paquete(proyecto, nombre="Paquete Demo", version="1.0.0")
    paquete = construir_paquete(proyecto, version="2.0.0")

    manifest = inspeccionar_paquete(paquete).manifest
    assert manifest["name"] == "paquete-demo"
    assert manifest["version"] == "2.0.0"
    assert paquete.name == "paquete-demo-2.0.0.co"


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
        if module
        in {"pcobra.cobra.core", "pcobra.cobra.core.lexer", "pcobra.cobra.core.parser"}
        or module.endswith((".lexer", ".parser"))
    }

    assert forbidden_modules == set()


def test_paquete_cobra_conserva_estructura_y_recursos(tmp_path: Path):
    proyecto = tmp_path / "demo"
    crear_paquete(proyecto, nombre="demo", version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    (proyecto / "src" / "helper.co").write_text(
        "funcion ayuda() {}\n", encoding="utf-8"
    )
    (proyecto / "README.md").write_text("# Demo\n", encoding="utf-8")
    (proyecto / "docs").mkdir()
    (proyecto / "docs" / "guia.md").write_text("# Guía\n", encoding="utf-8")
    (proyecto / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (proyecto / "assets" / "imagenes").mkdir(parents=True)
    (proyecto / "assets" / "imagenes" / "logo.bin").write_bytes(b"\x89PNG recurso")
    (proyecto / "resources" / "i18n").mkdir(parents=True)
    (proyecto / "resources" / "i18n" / "es.dat").write_bytes(b"hola=recurso")

    paquete = construir_paquete(proyecto, tmp_path / "demo.co")

    info = validar_paquete(paquete)
    assert info.manifest["format"] == "cobra-package-v1"
    assert MANIFEST_NAME in info.files
    assert "src/main.cobra" in info.files
    assert "src/helper.co" in info.files
    assert "README.md" in info.files
    assert "docs/guia.md" in info.files
    assert "Dockerfile" in info.files
    assert "assets/imagenes/logo.bin" in info.files
    assert "resources/i18n/es.dat" in info.files

    inspeccion = inspeccionar_paquete(paquete)
    assert inspeccion.checksum

    destino = extraer_paquete(paquete, tmp_path / "instalado")
    assert (destino / "src" / "main.cobra").read_text(
        encoding="utf-8"
    ) == "imprimir('hola')\n"
    assert (
        destino / "assets" / "imagenes" / "logo.bin"
    ).read_bytes() == b"\x89PNG recurso"
    assert (destino / "resources" / "i18n" / "es.dat").read_bytes() == b"hola=recurso"


def test_paquete_cobra_acepta_artefactos_mixtos_y_subcarpetas_anidadas(
    tmp_path: Path,
):
    proyecto = tmp_path / "artefactos"
    crear_paquete(proyecto, nombre="artefactos", version="1.0.0")
    archivos = {
        "src/main.cobra": "contenido de artefacto .cobra, no se parsea\n",
        "src/main.co": "contenido de artefacto .co, no se parsea\n",
        "README.md": "# Artefactos\n",
        "docs/guia.md": "# Guía de uso\n",
        "Dockerfile": "FROM scratch\n",
        "LICENSE.txt": "Licencia de prueba\n",
        "assets/logo.txt": "logo en texto\n",
        "assets/icons/nested/icon.txt": "icono anidado\n",
        "docs/referencia/api/v1/notas.md": "notas anidadas\n",
    }
    for relative_path, content in archivos.items():
        target = proyecto / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    paquete = construir_paquete(proyecto, tmp_path / "artefactos.co")

    info = validar_paquete(paquete)
    esperados = set(archivos)
    assert set(info.manifest["files"]) == esperados

    inspeccion = inspeccionar_paquete(paquete)
    assert set(inspeccion.files) == {MANIFEST_NAME, *esperados}

    destino = extraer_paquete(paquete, tmp_path / "instalado")
    for relative_path, content in archivos.items():
        assert (destino / relative_path).read_text(encoding="utf-8") == content
    assert (destino / "assets" / "icons" / "nested").is_dir()
    assert (destino / "docs" / "referencia" / "api" / "v1").is_dir()


def _crear_zip_con_manifest(
    tmp_path: Path, manifest: dict, files: dict[str, bytes] | None = None
) -> Path:
    paquete = tmp_path / "manual.co"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False))
        for name, content in (files or {}).items():
            zf.writestr(name, content)
    return paquete


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _crear_zip_moderno_con_infos(
    tmp_path: Path, entries: list[tuple[zipfile.ZipInfo | str, bytes]]
) -> Path:
    paquete = tmp_path / "manual-infos.co"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as zf:
        for info_or_name, content in entries:
            zf.writestr(info_or_name, content)
    return paquete


def _manifest_moderno(files: list[str], payloads: dict[str, bytes]) -> dict:
    return {
        "format": "cobra-package-v1",
        "name": "demo",
        "version": "1.0.0",
        "files": files,
        "checksums": {name: _sha256(payloads[name]) for name in files},
    }


def test_validar_paquete_moderno_rechaza_entrada_duplicada(tmp_path: Path):
    contenido = b"imprimir('hola')\n"
    manifest = _manifest_moderno(["src/main.cobra"], {"src/main.cobra": contenido})
    paquete = _crear_zip_moderno_con_infos(
        tmp_path,
        [
            (MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False).encode()),
            ("src/main.cobra", contenido),
            ("src/main.cobra", contenido),
        ],
    )

    with pytest.raises(ValueError, match="Entrada duplicada"):
        validar_paquete(paquete)


def test_validar_paquete_moderno_rechaza_symlink_por_external_attr(tmp_path: Path):
    link = zipfile.ZipInfo("src/link.co")
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    contenido = b"destino.co"
    manifest = _manifest_moderno(["src/link.co"], {"src/link.co": contenido})
    paquete = _crear_zip_moderno_con_infos(
        tmp_path,
        [
            (MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False).encode()),
            (link, contenido),
        ],
    )

    with pytest.raises(ValueError, match="Symlink no permitido"):
        validar_paquete(paquete)


def test_validar_paquete_moderno_rechaza_ruta_parent_traversal(tmp_path: Path):
    contenido = b"pwn"
    manifest = _manifest_moderno(["../evil.co"], {"../evil.co": contenido})
    paquete = _crear_zip_moderno_con_infos(
        tmp_path,
        [
            (MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False).encode()),
            ("../evil.co", contenido),
        ],
    )

    with pytest.raises(ValueError, match="Ruta insegura"):
        validar_paquete(paquete)


def test_validar_paquete_moderno_rechaza_ruta_absoluta(tmp_path: Path):
    contenido = b"pwn"
    manifest = _manifest_moderno(["/tmp/evil.co"], {"/tmp/evil.co": contenido})
    paquete = _crear_zip_moderno_con_infos(
        tmp_path,
        [
            (MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False).encode()),
            ("/tmp/evil.co", contenido),
        ],
    )

    with pytest.raises(ValueError, match="Ruta insegura"):
        validar_paquete(paquete)


def test_extraer_paquete_moderno_rechaza_ruta_windows_con_traversal(tmp_path: Path):
    contenido = b"pwn"
    ruta = r"src\..\evil.co"
    manifest = _manifest_moderno([ruta], {ruta: contenido})
    paquete = _crear_zip_moderno_con_infos(
        tmp_path,
        [
            (MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False).encode()),
            (ruta, contenido),
        ],
    )

    with pytest.raises(ValueError, match="Ruta insegura"):
        extraer_paquete(paquete, tmp_path / "destino")
    assert not (tmp_path / "evil.co").exists()


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

    with pytest.raises(
        ValueError, match="Checksum inválido para src/main\\.cobra: debe ser una cadena"
    ):
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

    with pytest.raises(
        ValueError,
        match="Checksum inválido para src/main\\.cobra: debe tener 64 caracteres",
    ):
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
    with (
        zipfile.ZipFile(original) as src,
        zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as dst,
    ):
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


def test_cli_paquete_verificar_integridad_falla_por_checksum_alterado(
    tmp_path: Path, capsys
):
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
