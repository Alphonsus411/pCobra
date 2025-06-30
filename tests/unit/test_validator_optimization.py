import importlib
from unittest.mock import patch

from src.core.semantic_validators import construir_cadena, ValidadorPrimitivaPeligrosa


def test_construir_cadena_reutiliza_instancias():
    contador = 0

    original_init = ValidadorPrimitivaPeligrosa.__init__

    def cuenta_init(self):
        nonlocal contador
        contador += 1
        original_init(self)

    with patch.object(ValidadorPrimitivaPeligrosa, "__init__", cuenta_init):
        construir_cadena()  # Primera vez crea la cadena
        construir_cadena()  # Debe reutilizarla

    assert contador == 1


def test_construir_cadena_sin_reutilizar(monkeypatch):
    contador = 0
    original_init = ValidadorPrimitivaPeligrosa.__init__

    def cuenta_init(self):
        nonlocal contador
        contador += 1
        original_init(self)

    with patch.object(ValidadorPrimitivaPeligrosa, "__init__", cuenta_init):
        import src.core.semantic_validators as sv
        monkeypatch.setattr(sv, "_CADENA_DEFECTO", None)
        construir_cadena()
        monkeypatch.setattr(sv, "_CADENA_DEFECTO", None)
        construir_cadena()

    assert contador == 2
