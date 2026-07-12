from types import ModuleType

import pytest

from pcobra.core.ast_nodes import NodoUsar
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.cobra import usar_loader
from pcobra.cobra.usar_policy import (
    REPL_COBRA_MODULE_MAP,
    USAR_COBRA_ALLOWLIST,
    USAR_COBRA_FACING_MODULE_FLAGS,
)
core_usar_loader = usar_loader


def _interp_con_alias(alias_map: dict[str, str]) -> InterpretadorCobra:
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)
    return interp


def test_no_regresion_ajuste_texto_usar_runtime_numero_expone_solo_api_espanola(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_numero)
    interp = _interp_con_alias({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "es_finito" in interp.variables
    assert "es_par" in interp.variables
    assert "isfinite" not in interp.variables


def test_usar_runtime_texto_expone_solo_api_espanola(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_texto)
    interp = _interp_con_alias({"texto": "texto"})
    interp.ejecutar_nodo(NodoUsar("texto"))

    assert "a_snake" in interp.variables
    assert "to_snake_case" not in interp.variables


def test_usar_runtime_datos_expone_filtrar_mapear_reducir(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_datos)
    interp = _interp_con_alias({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    assert {"filtrar", "mapear", "reducir"}.issubset(interp.variables)


@pytest.mark.parametrize("nombre", ["numpy", "pandas", "torch", "node-fetch", "serde"])
def test_usar_runtime_rechaza_numpy_y_similares(nombre):
    with pytest.raises(PermissionError) as exc:
        usar_loader.validar_nombre_modulo_usar(nombre)
    mensaje = str(exc.value)
    assert "Importación no permitida en 'usar'" in mensaje
    assert nombre in mensaje
    assert "backend_" not in mensaje


def test_usar_runtime_holobit_expone_solo_api_cobra_facing(monkeypatch):
    import pcobra.corelibs.holobit as modulo_holobit

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_holobit)
    interp = _interp_con_alias({"holobit": "holobit"})
    interp.ejecutar_nodo(NodoUsar("holobit"))

    assert "crear_holobit" in interp.variables
    assert "proyectar" in interp.variables
    assert "_to_sdk_holobit" not in interp.variables
    assert "_require_holobit_sdk" not in interp.variables
    assert "Holobit" not in interp.variables


def test_usar_runtime_no_exporta_simbolos_con_doble_guion_bajo(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_numero)
    interp = _interp_con_alias({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert all("__" not in nombre for nombre in interp.variables)


def test_usar_runtime_no_exporta_simbolos_bloqueados(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_datos)
    interp = _interp_con_alias({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    for prohibido in ("self", "append", "map", "filter", "unwrap", "expect"):
        assert prohibido not in interp.variables


def test_usar_runtime_numero_expone_e_inyecta_desviacion_estandar(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    mapa_limpio, conflictos = usar_loader.sanitizar_exports_publicos(
        modulo_numero,
        "numero",
    )

    assert "desviacion_estandar" in mapa_limpio
    assert not any(
        conflicto.get("symbol") == "desviacion_estandar"
        for conflicto in conflictos
    )

    monkeypatch.setattr(
        usar_loader,
        "obtener_modulo",
        lambda _nombre, **_kwargs: modulo_numero,
    )

    interp = _interp_con_alias({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "desviacion_estandar" in interp.variables


def test_usar_runtime_colision_warn_diagnostico_y_sin_overwrite(monkeypatch):
    modulo = ModuleType("texto")
    setattr(modulo, "__all__", ["a_snake", "a_camel"])
    setattr(modulo, "a_snake", lambda txt: f"nuevo:{txt}")
    setattr(modulo, "a_camel", lambda txt: txt)
    setattr(
        modulo,
        "__file__",
        "/workspace/pCobra/src/pcobra/corelibs/texto.py",
    )

    monkeypatch.setattr(usar_loader, "obtener_modulo", lambda _n, **_k: modulo)

    interp = _interp_con_alias({"texto": "texto"})
    interp.configurar_politica_colision_usar("warn_alias_required")
    valor_prev = lambda txt: f"previo:{txt}"
    interp.contextos[-1].define("a_snake", valor_prev)

    with pytest.warns(
        RuntimeWarning,
        match=r"Conflicto de nombres en `usar`",
    ):
        with pytest.raises(NameError, match=r"colisión estructurada="):
            interp.ejecutar_nodo(NodoUsar("texto"))

    assert interp.contextos[-1].get("a_snake") is valor_prev


def test_usar_runtime_reimport_idempotente_logica_no_falla(monkeypatch):
    import pcobra.corelibs.logica as modulo_logica

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_logica)
    interp = _interp_con_alias({"logica": "logica"})

    interp.ejecutar_nodo(NodoUsar("logica"))
    interp.ejecutar_nodo(NodoUsar("logica"))

    assert "conjuncion" in interp.variables


def test_usar_runtime_reimport_idempotente_numero_no_falla(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_numero)
    interp = _interp_con_alias({"numero": "numero"})

    interp.ejecutar_nodo(NodoUsar("numero"))
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "es_finito" in interp.variables


def test_usar_runtime_colision_variable_usuario_sigue_fallando(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_numero)
    interp = _interp_con_alias({"numero": "numero"})
    interp.contextos[-1].define("es_finito", "soy_usuario")

    with pytest.raises(NameError, match=r"colisión estructurada="):
        interp.ejecutar_nodo(NodoUsar("numero"))


def test_usar_runtime_holobit_no_expone_objetos_sdk_internos(monkeypatch):
    import pcobra.corelibs.holobit as modulo_holobit

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_holobit)
    interp = _interp_con_alias({"holobit": "holobit"})
    interp.ejecutar_nodo(NodoUsar("holobit"))

    for interno in ("holobit_sdk", "_SDKHolobit", "Holobit", "_to_sdk_holobit"):
        assert interno not in interp.variables


def test_usar_holobit_regresion_no_expone_simbolos_internos_por_introspeccion(monkeypatch):
    import pcobra.corelibs.holobit as modulo_holobit

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_holobit)
    interp = _interp_con_alias({"holobit": "holobit"})
    interp.ejecutar_nodo(NodoUsar("holobit"))

    namespace = set(interp.variables)
    assert set(modulo_holobit.__all__) == {
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    }
    for interno in ("_SDKHolobit", "_AdaptadorInternoHolobit", "EQUIVALENCIAS_SEMANTICAS_HOLOBIT"):
        assert interno not in namespace


def test_usar_runtime_allowlist_y_flags_mantienen_contrato_estricto():
    canonicos = tuple(REPL_COBRA_MODULE_MAP.keys())
    assert tuple(REPL_COBRA_MODULE_MAP.values()) == canonicos
    assert tuple(USAR_COBRA_FACING_MODULE_FLAGS.keys()) == canonicos
    assert all(USAR_COBRA_FACING_MODULE_FLAGS.values())
    assert set(canonicos) == set(USAR_COBRA_ALLOWLIST)


def test_validar_nombre_modulo_usar_exige_allowlist_estricta():
    assert usar_loader.validar_nombre_modulo_usar("numero") == "numero"
    with pytest.raises(PermissionError):
        usar_loader.validar_nombre_modulo_usar("mi_modulo_privado")


def test_validar_nombre_modulo_usar_numpy_devuelve_error_corto_fuera_catalogo_publico():
    with pytest.raises(PermissionError) as exc:
        usar_loader.validar_nombre_modulo_usar("numpy")
    assert "modulo_fuera_catalogo_publico" in str(exc.value)


def test_obtener_modulo_delega_validacion_inicial_sin_forzar_allowlist(monkeypatch):
    parametros: dict[str, object] = {}

    def _validador(nombre, *, require_allowlist=True):
        parametros["nombre"] = nombre
        parametros["require_allowlist"] = require_allowlist
        return "numero"

    monkeypatch.setattr(usar_loader, "validar_nombre_modulo_usar", _validador)
    monkeypatch.setattr(
        usar_loader,
        "_obtener_modulo_cobra_oficial_compat",
        lambda _nombre: ModuleType("numero"),
    )

    usar_loader.obtener_modulo("numero")

    assert parametros["nombre"] == "numero"
    assert parametros["require_allowlist"] is False


def test_sanitizar_exports_publicos_descarta_simbolos_fuera_del_contrato_canonico_y_backend():
    modulo = ModuleType("numero")

    setattr(
        modulo,
        "__all__",
        [
            "es_par",
            "sumar",
            "pathlib",
            "os",
            "_interno_sdk",
            "sdk_client",
        ],
    )

    simbolos = {
        "es_par": lambda n: n % 2 == 0,
        "sumar": lambda a, b: a + b,
        "pathlib": object(),
        "os": object(),
        "_interno_sdk": object(),
        "sdk_client": object(),
    }

    for nombre, valor in simbolos.items():
        setattr(modulo, nombre, valor)

    mapa_limpio, conflictos = usar_loader.sanitizar_exports_publicos(
        modulo,
        "numero",
    )

    assert set(mapa_limpio) == {"es_par"}

    rechazados = {
        (conflicto.get("symbol"), conflicto.get("code"))
        for conflicto in conflictos
    }

    assert ("pathlib", "outside_public_api") in rechazados
    assert ("os", "outside_public_api") in rechazados
    assert ("_interno_sdk", "outside_public_api") in rechazados
    assert ("sdk_client", "outside_public_api") in rechazados
    assert ("sumar", "outside_public_api") in rechazados


@pytest.mark.parametrize(
    ("nombre_interno", "tipo_error", "fragmento"),
    (
        (
            "holobit_sdk",
            PermissionError,
            "Importación no permitida en 'usar'",
        ),
        (
            "holobit_sdk.core",
            ValueError,
            "no es seguro para 'usar'",
        ),
        (
            "holobit_sdk.visualization",
            ValueError,
            "no es seguro para 'usar'",
        ),
        (
            "pcobra.corelibs.holobit",
            ValueError,
            "no es seguro para 'usar'",
        ),
    ),
)
def test_usar_runtime_rechaza_import_directo_de_internals_holobit(
    nombre_interno,
    tipo_error,
    fragmento,
):
    with pytest.raises(tipo_error) as exc:
        usar_loader.validar_nombre_modulo_usar(nombre_interno)

    mensaje = str(exc.value)
    assert fragmento in mensaje
    assert nombre_interno in mensaje
    assert "backend_" not in mensaje


def test_usar_runtime_error_usuario_sin_detalle_en_modo_normal(monkeypatch):
    modulo = ModuleType("texto")
    setattr(modulo, "__all__", ["a_snake"])
    setattr(modulo, "a_snake", lambda txt: txt)
    setattr(
        modulo,
        "__file__",
        "/workspace/pCobra/src/pcobra/corelibs/texto.py",
    )

    monkeypatch.setattr(usar_loader, "obtener_modulo", lambda _n, **_k: modulo)

    interp = _interp_con_alias({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda txt: f"previo:{txt}")

    with pytest.raises(NameError) as exc:
        interp.ejecutar_nodo(NodoUsar("texto"))

    mensaje = str(exc.value)
    assert "colisión estructurada=" in mensaje
    assert "'code': 'symbol_collision'" in mensaje
    assert "'symbol': 'a_snake'" in mensaje


def test_usar_runtime_error_usuario_con_detalle_en_debug(monkeypatch):
    modulo = ModuleType("texto")
    setattr(modulo, "__all__", ["a_snake"])
    setattr(modulo, "a_snake", lambda txt: txt)
    setattr(
        modulo,
        "__file__",
        "/workspace/pCobra/src/pcobra/corelibs/texto.py",
    )

    monkeypatch.setattr(usar_loader, "obtener_modulo", lambda _n, **_k: modulo)
    monkeypatch.setenv("PCOBRA_DEBUG_TRACES", "1")

    interp = _interp_con_alias({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda txt: f"previo:{txt}")

    with pytest.raises(NameError) as exc:
        interp.ejecutar_nodo(NodoUsar("texto"))

    mensaje = str(exc.value)
    assert "colisión estructurada=" in mensaje
    assert "'code': 'symbol_collision'" in mensaje
    assert "'symbol': 'a_snake'" in mensaje
