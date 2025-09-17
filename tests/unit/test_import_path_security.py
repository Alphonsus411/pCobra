import os
import builtins

import pytest

from core.ast_nodes import NodoImport
from core.interpreter import InterpretadorCobra, _ruta_import_permitida
from core.semantic_validators.import_seguro import ValidadorImportSeguro
from core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError


def _configurar_imports(monkeypatch, modules_dir, whitelist=None):
    import core.interpreter as interpreter_mod

    lista = set() if whitelist is None else set(whitelist)
    monkeypatch.setattr(interpreter_mod, "MODULES_PATH", str(modules_dir))
    monkeypatch.setattr(interpreter_mod, "IMPORT_WHITELIST", lista)


def test_ruta_permitida_dentro_de_modules(tmp_path, monkeypatch):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    archivo = modules_dir / "seguro.co"
    archivo.write_text("var seguro = 1")

    _configurar_imports(monkeypatch, modules_dir)

    assert _ruta_import_permitida(str(archivo))


def test_ruta_permitida_por_lista_blanca(tmp_path, monkeypatch):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    archivo = tmp_path / "externo.co"
    archivo.write_text("var externo = 1")

    _configurar_imports(monkeypatch, modules_dir, {str(archivo)})

    assert _ruta_import_permitida(str(archivo))


def test_interpreter_bloquea_prefijo_modules_fake(tmp_path, monkeypatch):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    ruta_evasion = tmp_path / "modules_fake" / "malicioso.co"
    ruta_evasion.parent.mkdir()
    ruta_evasion.write_text("var trampa = 1")

    _configurar_imports(monkeypatch, modules_dir)

    original_open = builtins.open

    def _abrir_no_permitido(path, *args, **kwargs):
        try:
            if os.path.realpath(path) == os.path.realpath(ruta_evasion):
                raise AssertionError("open() no debe ejecutarse para rutas bloqueadas")
        except TypeError:
            pass
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _abrir_no_permitido)

    interp = InterpretadorCobra()

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_import(NodoImport(str(ruta_evasion)))


def test_interpreter_bloquea_symlink_fuera_de_modules(tmp_path, monkeypatch):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    directorio_fuera = tmp_path / "fuera"
    directorio_fuera.mkdir()
    archivo_real = directorio_fuera / "malicioso.co"
    archivo_real.write_text("var x = 0")
    enlace = modules_dir / "atajo.co"
    os.symlink(archivo_real, enlace)

    _configurar_imports(monkeypatch, modules_dir)

    original_open = builtins.open

    def _abrir_no_permitido(path, *args, **kwargs):
        try:
            if os.path.realpath(path) == os.path.realpath(archivo_real):
                raise AssertionError("open() no debe ejecutarse para rutas bloqueadas")
        except TypeError:
            pass
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _abrir_no_permitido)

    interp = InterpretadorCobra()

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_import(NodoImport(str(enlace)))


def test_validador_detecta_symlink(tmp_path, monkeypatch):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    directorio_fuera = tmp_path / "trampa"
    directorio_fuera.mkdir()
    archivo_real = directorio_fuera / "malicioso.co"
    archivo_real.write_text("var x = 1")
    enlace = modules_dir / "atajo.co"
    os.symlink(archivo_real, enlace)

    _configurar_imports(monkeypatch, modules_dir)

    nodo = NodoImport(str(enlace))
    validator = ValidadorImportSeguro()

    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)
