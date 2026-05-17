from types import ModuleType

from pcobra.core.usar_symbol_policy import (
    PoliticaSaneamientoUsar,
    normalizar_metadata_simbolo_usar,
    sanear_exportables_para_usar,
    sanear_simbolo_para_usar,
)


def test_rechaza_nombres_prohibidos_explicitos():
    for nombre in ("self", "append", "map", "filter", "unwrap", "expect"):
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True
        assert resultado.codigo in {"explicit_forbidden_name", "cobra_public_equivalent"}
        assert "Usa el nombre Cobra canónico" in (resultado.mensaje or "")


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
    assert r_dunder_python.codigo == "dunder_name"

    r_objeto_backend = sanear_simbolo_para_usar("backend", ModuleType("backend"))
    assert r_objeto_backend.rechazado is True
    assert r_objeto_backend.codigo == "backend_module_object"

    r_interno_no_publico = sanear_simbolo_para_usar("interno", 123)
    assert r_interno_no_publico.rechazado is True
    assert r_interno_no_publico.codigo == "non_callable_not_canonical_public_constant"

    r_backend_ingles = sanear_simbolo_para_usar("append", lambda: None)
    assert r_backend_ingles.rechazado is True
    assert r_backend_ingles.codigo in {"explicit_forbidden_name", "cobra_public_equivalent"}


def test_saneamiento_centralizado_aplica_todas_las_reglas():
    simbolos = [
        ("_interno", lambda: None),
        ("append", lambda: None),
        ("PI", 3.14159),
        ("publica", lambda: "ok"),
    ]

    permitidos, rechazos, warnings = sanear_exportables_para_usar(simbolos)

    assert [nombre for nombre, _ in permitidos] == ["PI", "publica"]
    assert {r.nombre for r in rechazos.rechazos_duros} == {"_interno", "append"}
    assert [w.nombre for w in warnings] == ["PI"]


def test_acepta_equivalentes_canonicos_en_espanol():
    for nombre in ("agregar", "mapear", "filtrar", "obtener_o_error", "esperar_valor"):
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is False
        assert resultado.codigo == "ok"


def test_rechaza_no_callable_que_no_es_constante_publica_canonica():
    resultado = sanear_simbolo_para_usar("valor_interno", 123)
    assert resultado.rechazado is True
    assert resultado.codigo == "non_callable_not_canonical_public_constant"

    resultado_ok = sanear_simbolo_para_usar("PI", 3.14159)
    assert resultado_ok.rechazado is False
    assert resultado_ok.warning is True
    assert resultado_ok.codigo == "public_constant"

def test_rechaza_todos_los_alias_ingleses_prohibidos():
    prohibidos = ("self", "append", "map", "filter", "reduce", "keys", "values", "len", "length", "unwrap", "expect")
    for nombre in prohibidos:
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True
        assert resultado.codigo in {"explicit_forbidden_name", "cobra_public_equivalent"}


def test_modo_estricto_cobra_facing_rechaza_nombres_no_canonicos():
    politica = PoliticaSaneamientoUsar(validar_nombre_canonico_espanol_en_cobra_facing=True)

    resultado = sanear_simbolo_para_usar(
        "procesar",
        lambda: None,
        politica=politica,
        modulo_cobra_facing=True,
    )

    assert resultado.rechazado is True
    assert resultado.codigo == "non_canonical_spanish_name"


def test_modo_estricto_cobra_facing_permite_nombres_canonicos():
    politica = PoliticaSaneamientoUsar(validar_nombre_canonico_espanol_en_cobra_facing=True)

    resultado = sanear_simbolo_para_usar(
        "procesar_datos",
        lambda: None,
        politica=politica,
        modulo_cobra_facing=True,
    )

    assert resultado.rechazado is False
    assert resultado.codigo == "ok"


def test_constantes_publicas_canonicas_explicitas_se_permiten():
    for nombre in ("PI", "E", "TAU", "INF", "NAN"):
        resultado = sanear_simbolo_para_usar(nombre, 1.0)
        assert resultado.rechazado is False
        assert resultado.codigo == "public_constant"
        assert resultado.warning is True


def test_rechazo_estricto_alias_backend_hacia_cobra():
    prohibidos = ("self", "append", "map", "filter", "unwrap", "expect", "keys", "values", "len", "lower", "upper")
    for nombre in prohibidos:
        resultado = sanear_simbolo_para_usar(nombre, lambda: None)
        assert resultado.rechazado is True
        assert resultado.codigo in {"explicit_forbidden_name", "cobra_public_equivalent"}


def test_objetos_envueltos_sdk_y_wrapped_se_bloquean_siempre():
    modulo_sdk = ModuleType("modulo_sdk")

    class WrapperConWrapped:
        __wrapped__ = modulo_sdk

    class WrapperConSdk:
        _sdk = modulo_sdk

    r_wrapped = sanear_simbolo_para_usar("wrapper", WrapperConWrapped())
    r_sdk = sanear_simbolo_para_usar("wrapper_sdk", WrapperConSdk())

    assert r_wrapped.rechazado is True
    assert r_wrapped.codigo == "backend_module_object"
    assert r_sdk.rechazado is True
    assert r_sdk.codigo == "backend_module_object"


def test_rechaza_nombre_holobit_sdk_explicito():
    resultado = sanear_simbolo_para_usar("holobit_sdk", lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "cobra_public_equivalent"


def test_rechaza_clase_interna_con_rastro_sdk_en_modulo():
    ClaseInterna = type("ClaseInterna", (), {})
    ClaseInterna.__module__ = "pcobra.adapters.holobit_sdk.wrapper"
    resultado = sanear_simbolo_para_usar("adaptador", ClaseInterna)
    assert resultado.rechazado is True
    assert resultado.codigo == "backend_module_object"


def test_normalizar_metadata_simbolo_usar_convierte_alias_legacy_y_derivados():
    raw = {
        "kind": "usar",
        "public_api": True,
        "backend_exposed": False,
        "callable": True,
    }
    normalizada = normalizar_metadata_simbolo_usar(raw, "texto", "formatear")
    assert normalizada["origin_kind"] == "usar"
    assert normalizada["module"] == "texto"
    assert normalizada["symbol"] == "formatear"
    assert normalizada["sanitized"] is True
    assert "kind" not in normalizada
