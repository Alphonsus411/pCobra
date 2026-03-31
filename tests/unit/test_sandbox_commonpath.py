import os
import pytest
from core.sandbox import validar_dependencias


def test_validar_dependencias_unidades_distintas(monkeypatch):
    def fake_commonpath(paths):
        raise ValueError("rutas en distintas unidades")

    monkeypatch.setattr(os.path, "commonpath", fake_commonpath)
    mod_info = {"mod": {"python": "D:\\mod.py"}}
    with pytest.raises(ValueError, match="Ruta no permitida"):
        validar_dependencias("python", mod_info)


def test_validar_dependencias_funciona_con_cwd_distinto(tmp_path, monkeypatch):
    raiz = tmp_path / "proyecto"
    raiz.mkdir()
    dep = raiz / "libs" / "dep.py"
    dep.parent.mkdir()
    dep.write_text("# dependencia\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    mod_info = {"mod": {"python": "libs/dep.py"}}
    validar_dependencias("python", mod_info, base_dir=str(raiz))


def test_validar_dependencias_rechaza_fuera_de_raiz(tmp_path):
    raiz = tmp_path / "proyecto"
    raiz.mkdir()
    fuera = tmp_path / "externo.py"
    fuera.write_text("# fuera\n", encoding="utf-8")
    mod_info = {"mod": {"python": "../externo.py"}}

    with pytest.raises(ValueError, match="Ruta no permitida"):
        validar_dependencias("python", mod_info, base_dir=str(raiz))


def test_validar_dependencias_inexistente_lanza_file_not_found(tmp_path):
    raiz = tmp_path / "proyecto"
    raiz.mkdir()
    mod_info = {"mod": {"python": "libs/falta.py"}}

    with pytest.raises(FileNotFoundError, match="Dependencia no encontrada"):
        validar_dependencias("python", mod_info, base_dir=str(raiz))
