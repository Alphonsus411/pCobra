from io import StringIO
from unittest.mock import patch
import pytest

from cli.cli import main
from cobra.transpilers import module_map


@pytest.mark.timeout(5)
def test_compilar_dependencia_invalida_python(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    prog = tmp_path / "p.co"
    prog.write_text(f"import '{mod}'\nimprimir(x)")
    mapping = {str(mod): {"python": str(tmp_path / 'no.py')}}
    monkeypatch.setattr(module_map, "get_toml_map", lambda: mapping)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(prog)])
    assert "dependencia" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_compilar_dependencia_invalida_js(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    prog = tmp_path / "p.co"
    prog.write_text(f"import '{mod}'\nimprimir(x)")
    mapping = {str(mod): {"js": str(tmp_path / 'no.js')}}
    monkeypatch.setattr(module_map, "get_toml_map", lambda: mapping)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(prog), "--tipo=js"])
    assert "dependencia" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_compilar_dependencia_invalida_cpp(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    prog = tmp_path / "p.co"
    prog.write_text(f"import '{mod}'\nimprimir(x)")
    mapping = {str(mod): {"cpp": str(tmp_path / 'no.cpp')}}
    monkeypatch.setattr(module_map, "get_toml_map", lambda: mapping)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(prog), "--tipo=cpp"])
    assert "dependencia" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_ejecutar_dependencia_invalida(tmp_path, monkeypatch):
    prog = tmp_path / "p.co"
    prog.write_text("imprimir(1)")
    mapping = {"x": {"python": str(tmp_path / 'no.py')}}
    monkeypatch.setattr(module_map, "get_toml_map", lambda: mapping)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(prog)])
    assert "dependencia" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_interactive_dependencia_invalida(monkeypatch):
    mapping = {"x": {"python": "/no/dep.py"}}
    monkeypatch.setattr(module_map, "get_toml_map", lambda: mapping)
    with patch("builtins.input", return_value="salir()"), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(["interactive"])
    assert "dependencia" in out.getvalue().lower()
