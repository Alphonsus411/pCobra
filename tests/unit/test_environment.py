from __future__ import annotations

import pytest

from pcobra.core.environment import Environment


def test_define_siempre_es_local() -> None:
    global_env = Environment(values={"x": 10})
    local_env = Environment(parent=global_env)

    local_env.define("x", 99)

    assert local_env.values["x"] == 99
    assert global_env.values["x"] == 10


def test_get_resuelve_en_ancestros() -> None:
    global_env = Environment(values={"base": 7})
    intermedio = Environment(parent=global_env)
    local_env = Environment(parent=intermedio)

    assert local_env.get("base") == 7


def test_set_actualiza_scope_mas_cercano_existente() -> None:
    global_env = Environment(values={"x": 100})
    padre = Environment(values={"x": 1}, parent=global_env)
    local_env = Environment(parent=padre)

    local_env.set("x", 2)

    assert padre.values["x"] == 2
    assert global_env.values["x"] == 100


def test_set_falla_si_variable_no_esta_declarada() -> None:
    global_env = Environment()
    local_env = Environment(parent=global_env)

    with pytest.raises(NameError, match="Variable no declarada: faltante"):
        local_env.set("faltante", 1)


def test_get_define_set_en_cadena_multinivel_actualiza_ancestro_mas_cercano() -> None:
    raiz = Environment(values={"x": "raiz", "solo_raiz": 1})
    medio = Environment(values={"x": "medio"}, parent=raiz)
    hoja = Environment(parent=medio)

    assert hoja.get("x") == "medio"
    assert hoja.get("solo_raiz") == 1

    hoja.define("x", "hoja")
    hoja.set("x", "hoja_actualizada")
    assert hoja.get("x") == "hoja_actualizada"
    assert medio.get("x") == "medio"

    hoja.set("solo_raiz", 9)
    assert raiz.get("solo_raiz") == 9
    assert "solo_raiz" not in hoja.values
    assert "solo_raiz" not in medio.values
