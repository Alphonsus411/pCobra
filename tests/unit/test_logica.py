import sys
from importlib import util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

sys.modules.setdefault("httpx", ModuleType("httpx"))


def _cargar_logica() -> ModuleType:
    ruta = ROOT / "src" / "pcobra" / "standard_library" / "logica.py"
    spec = util.spec_from_file_location("standard_library.logica", ruta)
    modulo = util.module_from_spec(spec)
    if "standard_library" not in sys.modules:
        paquete = ModuleType("standard_library")
        paquete.__path__ = [str(ruta.parent)]
        sys.modules["standard_library"] = paquete
    sys.modules["standard_library.logica"] = modulo
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


logica = _cargar_logica()


def test_logica_tablas_de_verdad():
    casos = [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]
    for a, b in casos:
        assert logica.conjuncion(a, b) is (a and b)
        assert logica.disyuncion(a, b) is (a or b)
        assert logica.negacion(a) is (not a)
        assert logica.xor(a, b) is ((a and not b) or (not a and b))
        assert logica.nand(a, b) is (not (a and b))
        assert logica.nor(a, b) is (not (a or b))
        assert logica.implica(a, b) is ((not a) or b)
        assert logica.equivale(a, b) is (a is b)

    assert logica.xor_multiple(True, False, True) is False
    assert logica.xor_multiple(True, True, False, False) is False
    assert logica.xor_multiple(True, False, False, False) is True


def test_logica_colecciones():
    assert logica.todas([True, True, True]) is True
    assert logica.todas([True, False]) is False
    assert logica.alguna([False, False, True]) is True
    assert logica.alguna([False, False]) is False

    casos_coleccion = [
        ([False, False], True, False, 0, True),
        ([True, False], False, True, 1, False),
        ([True, True, False], False, False, 2, True),
        ([True, True, True], False, False, 3, False),
    ]
    for valores, ninguna_esperado, solo_uno_esperado, conteo_esperado, paridad_esperada in casos_coleccion:
        assert logica.ninguna(valores) is ninguna_esperado
        assert logica.solo_uno(*valores) is solo_uno_esperado
        assert logica.conteo_verdaderos(valores) == conteo_esperado
        assert logica.paridad(valores) is paridad_esperada

    assert logica.solo_uno(True, False, False, False) is True
    assert logica.solo_uno(False, False, False) is False


def test_logica_valida_entradas():
    with pytest.raises(TypeError):
        logica.conjuncion(1, True)
    with pytest.raises(TypeError):
        logica.disyuncion(True, "no bool")
    with pytest.raises(TypeError):
        logica.negacion("no bool")
    with pytest.raises(ValueError):
        logica.xor_multiple(True)
    with pytest.raises(TypeError):
        logica.xor_multiple(True, 0)
    with pytest.raises(TypeError):
        logica.todas([True, 1])
    with pytest.raises(TypeError):
        logica.alguna([False, None])
    with pytest.raises(ValueError):
        logica.solo_uno()
    with pytest.raises(TypeError):
        logica.solo_uno(True, 0)
    with pytest.raises(TypeError):
        logica.ninguna([True, 1])
    with pytest.raises(TypeError):
        logica.conteo_verdaderos([False, None])
    with pytest.raises(TypeError):
        logica.paridad([True, "no bool"])


def test_coalesce_predicado_por_defecto():
    assert logica.coalesce(None, False, 0, "dato") == "dato"
    assert logica.coalesce(None, "", None) is None


def test_coalesce_predicado_personalizado():
    assert logica.coalesce(1, 3, 4, predicado=lambda valor: valor % 2 == 0) == 4
    assert logica.coalesce("", "texto", predicado=lambda valor: len(valor) > 3) == "texto"


def test_coalesce_valida_predicado_y_argumentos():
    with pytest.raises(ValueError):
        logica.coalesce()

    with pytest.raises(TypeError):
        logica.coalesce(1, predicado="no callable")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        logica.coalesce(1, predicado=lambda _: "no bool")

