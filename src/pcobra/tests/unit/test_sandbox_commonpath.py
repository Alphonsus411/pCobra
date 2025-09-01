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
