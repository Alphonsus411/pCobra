from types import ModuleType

from pcobra.core.usar_symbol_policy import sanear_exportables_para_usar, sanear_simbolo_para_usar


def test_rechaza_nombres_prohibidos_explicitos():
    for nombre in ("self", "append", "map"):
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True


def test_rechaza_doble_guion_bajo_y_modulo_backend():
    r_privado = sanear_simbolo_para_usar("__danger__", lambda: None)
    assert r_privado.rechazado is True

    r_modulo = sanear_simbolo_para_usar("sdk", ModuleType("sdk"))
    assert r_modulo.rechazado is True


def test_reglas_de_saneamiento_por_caso_especifico():
    r_prefijo_privado = sanear_simbolo_para_usar("_interno", lambda: None)
    assert r_prefijo_privado.rechazado is True
    assert r_prefijo_privado.codigo == "private_prefix"

    r_doble_guion_bajo = sanear_simbolo_para_usar("a__b", lambda: None)
    assert r_doble_guion_bajo.rechazado is True
    assert r_doble_guion_bajo.codigo == "dunder_pattern"

    r_dunder_python = sanear_simbolo_para_usar("__name__", lambda: None)
    assert r_dunder_python.rechazado is True
    assert r_dunder_python.codigo == "private_prefix"

    r_objeto_backend = sanear_simbolo_para_usar("backend", ModuleType("backend"))
    assert r_objeto_backend.rechazado is True
    assert r_objeto_backend.codigo == "backend_module_object"

    r_interno_no_publico = sanear_simbolo_para_usar("interno", 123)
    assert r_interno_no_publico.rechazado is True
    assert r_interno_no_publico.codigo == "non_callable_not_canonical_public_constant"

    r_backend_ingles = sanear_simbolo_para_usar("append", lambda: None)
    assert r_backend_ingles.rechazado is True
    assert r_backend_ingles.codigo == "explicit_forbidden_name"


def test_saneamiento_centralizado_aplica_todas_las_reglas():
    simbolos = [
        ("_interno", lambda: None),
        ("append", lambda: None),
        ("PI", 3.14159),
        ("publica", lambda: "ok"),
    ]

    permitidos, rechazos, warnings = sanear_exportables_para_usar(simbolos)

    assert [nombre for nombre, _ in permitidos] == ["PI", "publica"]
    assert {r.nombre for r in rechazos} == {"_interno", "append"}
    assert [w.nombre for w in warnings] == ["PI"]
