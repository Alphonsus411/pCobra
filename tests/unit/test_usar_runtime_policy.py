from types import ModuleType

import pytest

from core.ast_nodes import NodoUsar
from core.interpreter import InterpretadorCobra
from pcobra.cobra import usar_loader
from pcobra.cobra.usar_policy import (
    REPL_COBRA_MODULE_MAP,
    USAR_COBRA_ALLOWLIST,
    USAR_COBRA_FACING_MODULE_FLAGS,
)
from core import usar_loader as core_usar_loader


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

    assert "holobit" in interp.variables
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


def test_usar_runtime_numero_filtra_simbolo_fuera_de_api_publica_y_no_lo_inyecta(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    mapa_limpio, _conflictos = usar_loader.sanitizar_exports_publicos(modulo_numero, "numero")
    assert "desviacion_estandar" not in mapa_limpio

    simbolos_inyectados: list[str] = []
    inyeccion_real = InterpretadorCobra._inyectar_simbolos_usar_en_contexto

    def _inyectar_con_espia(self, simbolos_saneados, *, modulo, permitir_sobrescritura=False):
        simbolos_inyectados.extend(nombre for nombre, _ in simbolos_saneados)
        return inyeccion_real(
            self,
            simbolos_saneados,
            modulo=modulo,
            permitir_sobrescritura=permitir_sobrescritura,
        )

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_numero)
    monkeypatch.setattr(InterpretadorCobra, "_inyectar_simbolos_usar_en_contexto", _inyectar_con_espia)

    interp = _interp_con_alias({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "desviacion_estandar" not in simbolos_inyectados


def test_usar_runtime_colision_warn_diagnostico_y_sin_overwrite(monkeypatch, caplog):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake", "a_camel"]
    modulo.a_snake = lambda txt: f"nuevo:{txt}"
    modulo.a_camel = lambda txt: txt
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _n: modulo)

    interp = _interp_con_alias({"texto": "texto"})
    interp.configurar_politica_colision_usar("warn_alias_required")
    valor_prev = lambda txt: f"previo:{txt}"
    interp.contextos[-1].define("a_snake", valor_prev)

    with pytest.raises(NameError, match=r"Requiere alias explícito"):
        interp.ejecutar_nodo(NodoUsar("texto"))

    assert interp.contextos[-1].resolver("a_snake") is valor_prev
    assert "usar_collision" in caplog.text


def test_usar_runtime_reimport_idempotente_logica_no_falla(monkeypatch):
    import pcobra.corelibs.logica as modulo_logica

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _n, **_k: modulo_logica)
    interp = _interp_con_alias({"logica": "logica"})

    interp.ejecutar_nodo(NodoUsar("logica"))
    interp.ejecutar_nodo(NodoUsar("logica"))

    assert "y_logico" in interp.variables


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

    with pytest.raises(NameError, match="conflicto de símbolos"):
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


@pytest.mark.parametrize(
    "nombre_interno",
    (
        "holobit_sdk",
        "holobit_sdk.core",
        "holobit_sdk.visualization",
        "pcobra.corelibs.holobit",
    ),
)
def test_usar_runtime_rechaza_import_directo_de_internals_holobit(nombre_interno):
    with pytest.raises(PermissionError) as exc:
        usar_loader.validar_nombre_modulo_usar(nombre_interno)
    mensaje = str(exc.value)
    assert "Importación no permitida en 'usar'" in mensaje
    assert nombre_interno in mensaje
    assert "backend_" not in mensaje


def test_usar_runtime_error_usuario_sin_detalle_en_modo_normal(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake"]
    modulo.a_snake = lambda txt: txt
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _n: modulo)

    interp = _interp_con_alias({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda txt: f"previo:{txt}")

    with pytest.raises(NameError) as exc:
        interp.ejecutar_nodo(NodoUsar("texto"))

    mensaje = str(exc.value)
    assert "conflicto de símbolos" in mensaje
    assert "detalle=" not in mensaje
    assert "[" not in mensaje


def test_usar_runtime_error_usuario_con_detalle_en_debug(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake"]
    modulo.a_snake = lambda txt: txt
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _n: modulo)
    monkeypatch.setenv("PCOBRA_DEBUG_TRACES", "1")

    interp = _interp_con_alias({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda txt: f"previo:{txt}")

    with pytest.raises(NameError) as exc:
        interp.ejecutar_nodo(NodoUsar("texto"))

    mensaje = str(exc.value)
    assert "conflicto de símbolos" in mensaje
    assert "detalle=" in mensaje
