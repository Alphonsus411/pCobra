import json
from io import StringIO
import zipfile
from unittest.mock import patch

from cobra.cli.cli import main
from cobra.cli.commands import modules_cmd


def _crear_fuente(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    modulo = src / "m.co"
    modulo.write_text("var x = 1", encoding="utf-8")
    return src, modulo


def _leer_manifest(paquete):
    with zipfile.ZipFile(paquete) as zf:
        return json.loads(zf.read("cobra.pkg.json").decode("utf-8"))


def test_paquete_crear_instalar_flujo_moderno_co(tmp_path, monkeypatch):
    src, _modulo = _crear_fuente(tmp_path)
    pkg = tmp_path / "demo.co"

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "crear", str(src), str(pkg), "--nombre=demo"])

    assert pkg.exists()
    data = _leer_manifest(pkg)
    assert data["format"] == "cobra-package-v1"
    assert data["name"] == "demo"
    assert data["version"] == "0.1.0"
    assert data["files"] == ["README.md", "m.co"]
    assert set(data["checksums"]) == {"README.md", "m.co"}
    assert all(data["checksums"].values())

    mods_dir = tmp_path / "mods"
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", mods_dir)

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "instalar", str(pkg), "--destino", str(mods_dir)])

    assert (mods_dir / "m.co").exists()


def test_paquete_crear_instalar_alias_legacy_cobra(tmp_path, monkeypatch):
    src, _modulo = _crear_fuente(tmp_path)
    pkg = tmp_path / "demo.cobra"

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "crear", str(src), str(pkg), "--nombre=demo"])

    assert pkg.exists()
    data = _leer_manifest(pkg)
    assert data["format"] == "cobra-package-v1"
    assert data["name"] == "demo"
    assert data["version"] == "0.1.0"
    assert data["files"] == ["README.md", "m.co"]
    assert set(data["checksums"]) == {"README.md", "m.co"}

    mods_dir = tmp_path / "mods-legacy"
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", mods_dir)

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "instalar", str(pkg), "--destino", str(mods_dir)])

    assert (mods_dir / "m.co").exists()


def test_paquete_validar_construir_inspeccionar_extraer_formato_moderno(tmp_path):
    src, _modulo = _crear_fuente(tmp_path)
    pkg = tmp_path / "demo.co"

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "construir", str(src), str(pkg), "--nombre=demo"])

    data = _leer_manifest(pkg)
    assert data["format"] == "cobra-package-v1"
    assert data["name"] == "demo"
    assert data["version"] == "0.1.0"
    assert data["files"] == ["m.co"]
    assert set(data["checksums"]) == {"m.co"}

    with patch("sys.stdout", new_callable=StringIO) as stdout:
        main(["paquete", "validar", str(pkg)])
    assert "Paquete válido" in stdout.getvalue()

    with patch("sys.stdout", new_callable=StringIO) as stdout:
        main(["paquete", "inspeccionar", str(pkg)])
    salida = stdout.getvalue()
    assert "Paquete: demo 0.1.0" in salida
    assert "- m.co" in salida
    assert "SHA256:" in salida

    destino = tmp_path / "extraido"
    with patch("sys.stdout", new_callable=StringIO) as stdout:
        main(["paquete", "extraer", str(pkg), str(destino)])
    assert "Paquete extraído" in stdout.getvalue()
    assert (destino / "m.co").read_text(encoding="utf-8") == "var x = 1"


def test_paquete_help_documenta_verificar_e_integridad_legacy(capsys):
    with patch("sys.stdout", new_callable=StringIO) as stdout:
        codigo = main(["paquete", "--help"])

    assert codigo == 0
    salida = stdout.getvalue()
    assert "verificar" in salida
    assert "integridad" in salida


def test_paquete_verificar_help_expone_alias_integridad(capsys):
    with patch("sys.stdout", new_callable=StringIO) as stdout:
        codigo = main(["paquete", "verificar", "--help"])

    assert codigo == 0
    salida = stdout.getvalue()
    assert "verificar" in salida
    assert "integridad" in salida
    assert "paquete" in salida
