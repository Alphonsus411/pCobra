import importlib
import json
from argparse import Namespace
from pathlib import Path
from io import StringIO
from unittest.mock import patch

import pytest
import yaml

from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands import modules_cmd
from pcobra.cobra.cli.commands.crear_cmd import CrearCommand
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def _load_mapping(source):
    raw = source.read() if hasattr(source, "read") else source
    return json.loads(raw) if raw else {}


def _dump_mapping(data, stream=None):
    serialized = json.dumps(data)
    if stream is not None:
        stream.write(serialized)
        return None
    return serialized


@pytest.mark.timeout(5)
def test_cli_ejecutar_imprime(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("var x = 3\nimprimir(x)")
    with (
        patch.object(cli_module, "resolve_command_profile", return_value="development"),
        patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ExecuteCommand]),
        patch("sys.stdout", new_callable=StringIO) as out,
    ):
        cli_module.main(["ejecutar", str(archivo)])
    assert out.getvalue().strip() == "3"


@pytest.mark.timeout(5)
def test_cli_ejecutar_flag_no_seguro(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("imprimir(1)")
    command = ExecuteCommand()
    with patch.object(command._service, "run", return_value=0) as run_service:
        result = command.run(
            Namespace(archivo=str(archivo), seguro=False, extra_validators=None)
        )

    assert result == 0
    request = run_service.call_args.args[0]
    assert request.archivo == str(archivo)
    assert request.seguro is False


@pytest.mark.timeout(5)
def test_cli_validadores_extra(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("imprimir(1)")
    ruta = tmp_path / "vals.py"
    ruta.write_text("VALIDADORES_EXTRA = []\n")
    command = ExecuteCommand()
    with patch.object(command._service, "run", return_value=0) as run_service:
        result = command.run(
            Namespace(archivo=str(archivo), seguro=True, extra_validators=str(ruta))
        )

    assert result == 0
    request = run_service.call_args.args[0]
    assert request.archivo == str(archivo)
    assert request.seguro is True
    assert request.extra_validators == str(ruta)


@pytest.mark.timeout(5)
def test_cli_modulos_comandos(tmp_path, monkeypatch):
    monkeypatch.setattr(yaml, "safe_load", _load_mapping)
    monkeypatch.setattr(yaml, "safe_dump", _dump_mapping)
    monkeypatch.setattr(
        cli_module, "resolve_command_profile", lambda: "development"
    )
    monkeypatch.setattr(
        cli_module.AppConfig,
        "BASE_COMMAND_CLASSES",
        [modules_cmd.ModulesCommand],
    )
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", mods_dir)
    mod_file = tmp_path / "module_map.toml"
    py_out = tmp_path / "m.py"
    js_out = tmp_path / "m.js"
    rust_out = tmp_path / "m.rs"
    py_out.write_text("d = 1\n")
    js_out.write_text("const d = 1;\n")
    rust_out.write_text("let d = 1;\n")
    mod_mapping = {
        "m.co": {
            "version": "0.1.0",
            "python": str(py_out),
            "javascript": str(js_out),
            "rust": str(rust_out),
        },
        "lock": {},
    }
    mod_file.write_text(yaml.safe_dump(mod_mapping))
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", mod_file)

    modulo = tmp_path / "m.co"
    modulo.write_text("var d = 1")

    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "listar"])
    assert "No hay módulos instalados" in out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "instalar", str(modulo)])
    destino = mods_dir / modulo.name
    assert destino.exists()
    assert f"Módulo instalado en {destino}" in out.getvalue().strip()
    data = yaml.safe_load(mod_file.read_text())
    assert data["lock"][modulo.name] == "0.1.0"

    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "listar"])
    assert modulo.name in out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "remover", modulo.name])
    assert not destino.exists()
    assert f"Módulo {modulo.name} eliminado" in out.getvalue().strip()
    data = yaml.safe_load(mod_file.read_text())
    assert modulo.name not in data["lock"]

    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "listar"])
    assert "No hay módulos instalados" in out.getvalue().strip()


@pytest.mark.timeout(5)
def test_modulos_import_en_entorno_solo_lectura(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    with patch.object(Path, "mkdir", side_effect=PermissionError("readonly")) as mocked:
        importlib.reload(modules_cmd)

    esperado = home / ".cobra" / "modules"
    assert modules_cmd.MODULES_PATH == esperado
    mocked.assert_not_called()

    monkeypatch.undo()
    importlib.reload(modules_cmd)


@pytest.mark.timeout(5)
def test_modulos_operan_en_directorio_de_usuario(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    importlib.reload(modules_cmd)

    modules_dir = modules_cmd.MODULES_PATH
    assert modules_dir == home / ".cobra" / "modules"
    assert not modules_dir.exists()
    lock_path = Path(modules_cmd.LOCK_FILE)
    assert lock_path.parent == modules_dir.parent

    modulo = tmp_path / "demo.co"
    modulo.write_text("var x = 1")

    ret = modules_cmd.ModulesCommand._instalar_modulo(str(modulo))

    assert ret == 0
    destino = modules_dir / modulo.name
    assert destino.exists()

    ret = modules_cmd.ModulesCommand._remover_modulo(modulo.name)
    assert ret == 0
    assert not destino.exists()

    monkeypatch.undo()
    importlib.reload(modules_cmd)


@pytest.mark.timeout(5)
def test_cli_modulo_version_invalida(tmp_path, monkeypatch):
    monkeypatch.setattr(yaml, "safe_load", _load_mapping)
    monkeypatch.setattr(yaml, "safe_dump", _dump_mapping)
    monkeypatch.setattr(
        cli_module, "resolve_command_profile", lambda: "development"
    )
    monkeypatch.setattr(
        cli_module.AppConfig,
        "BASE_COMMAND_CLASSES",
        [modules_cmd.ModulesCommand],
    )
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", mods_dir)
    mod_file = tmp_path / "module_map.toml"
    bad_py = tmp_path / "bad.py"
    bad_js = tmp_path / "bad.js"
    bad_rust = tmp_path / "bad.rs"
    bad_py.write_text("d = 1\n")
    bad_js.write_text("const d = 1;\n")
    bad_rust.write_text("let d = 1;\n")
    mod_mapping = {
        "bad.co": {
            "version": "abc",
            "python": str(bad_py),
            "javascript": str(bad_js),
            "rust": str(bad_rust),
        },
        "lock": {},
    }
    mod_file.write_text(yaml.safe_dump(mod_mapping))
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", mod_file)
    modulo = tmp_path / "bad.co"
    modulo.write_text("var d = 1")
    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["modulos", "instalar", str(modulo)])
    assert "inválida" in out.getvalue().lower()

@pytest.mark.timeout(5)
def test_cli_crear_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cli_module, "resolve_command_profile", lambda: "development"
    )
    monkeypatch.setattr(
        cli_module.AppConfig, "BASE_COMMAND_CLASSES", [CrearCommand]
    )
    ruta = tmp_path / "nuevo"
    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["crear", "archivo", str(ruta)])
    assert (tmp_path / "nuevo.co").exists()
    assert f"Archivo creado: {ruta}.co" in out.getvalue().strip()


@pytest.mark.timeout(5)
def test_cli_crear_proyecto(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cli_module, "resolve_command_profile", lambda: "development"
    )
    monkeypatch.setattr(
        cli_module.AppConfig, "BASE_COMMAND_CLASSES", [CrearCommand]
    )
    ruta = tmp_path / "proj"
    with patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["crear", "proyecto", str(ruta)])
    assert (ruta / "main.co").exists()
    assert "Proyecto Cobra creado" in out.getvalue()
