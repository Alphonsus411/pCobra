from __future__ import annotations

import hashlib
from pathlib import Path
from types import ModuleType

import pytest

from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import USAR_RUNTIME_EXPORT_OVERRIDES
from pcobra.core import usar_symbol_policy
from pcobra.cobra import usar_loader as cobra_usar_loader


def _nodo(modulo: str):
    class _NodoUsar:
        pass

    _NodoUsar.modulo = modulo
    return _NodoUsar()


def test_holobit_export_only_runtime_override(monkeypatch):
    mod = ModuleType("holobit")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["holobit"], "holobit_sdk", "_to_sdk_holobit"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.holobit_sdk = object()
    mod._to_sdk_holobit = lambda *_: None
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/holobit.py"

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"holobit": "holobit"})
    interp.ejecutar_usar(_nodo("holobit"))

    simbolos = set(interp.contextos[-1].values)
    assert set(USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]).issubset(simbolos)
    assert "holobit_sdk" not in simbolos
    assert "_to_sdk_holobit" not in simbolos
    assert all("__" not in name for name in simbolos)


def test_holobit_runtime_override_exporta_exclusivamente_api_publica():
    assert tuple(USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]) == (
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    )


def test_sanear_exportables_clasifica_y_rechaza_wrappers_backend():
    modulo_sdk = ModuleType("holobit_sdk")

    class WrapperConWrapped:
        __wrapped__ = modulo_sdk

    class WrapperConSdk:
        _sdk = modulo_sdk

    simbolos = [
        ("crear_holobit", lambda valores: valores),
        ("holobit_sdk", modulo_sdk),
        ("wrapper", WrapperConWrapped()),
        ("wrapper_sdk", WrapperConSdk()),
    ]
    permitidos, clasificacion, _warnings = usar_symbol_policy.sanear_exportables_para_usar(simbolos)

    assert [nombre for nombre, _ in permitidos] == ["crear_holobit"]
    codigos = {rechazo.nombre: rechazo.codigo for rechazo in clasificacion.rechazos_duros}
    assert codigos["holobit_sdk"] == "cobra_public_equivalent"
    assert codigos["wrapper"] == "backend_module_object"
    assert codigos["wrapper_sdk"] == "backend_module_object"


def test_rechaza_numpy_en_repl_estricto_sin_inyeccion(monkeypatch):
    monkeypatch.setattr(
        "pcobra.core.usar_loader.obtener_modulo_cobra_oficial",
        lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"módulo fuera del catálogo público|modulo_fuera_catalogo_publico") as exc:
        interp.ejecutar_usar(_nodo("numpy"))

    assert estado_pre == interp.contextos[-1].values
    assert "numpy" not in interp.contextos[-1].values
    assert "numpy" not in interp.variables


def test_texto_simbolo_existente_fuera_de_override_falla_como_no_declarado(monkeypatch):
    mod = ModuleType("texto")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["texto"], "normalizar_unicode"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["texto"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.normalizar_unicode = lambda texto, forma="NFC": texto
    mod.__file__ = "/workspace/pCobra/src/pcobra/standard_library/texto.py"

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.ejecutar_usar(_nodo("texto"))

    assert "normalizar_unicode" not in interp.contextos[-1].values
    with pytest.raises(NameError, match=r"^Variable no declarada: normalizar_unicode$"):
        interp.contextos[-1].get("normalizar_unicode")


def test_regresion_texto_detecta_mapeo_interno_incompleto_y_filtra_fuera_de_api_publica():
    mod = ModuleType("texto")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["texto"], "normalizar_unicode"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["texto"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.normalizar_unicode = lambda texto, forma="NFC": texto

    from pcobra.core.usar_loader import sanitizar_exports_publicos

    mapa_limpio, conflictos = sanitizar_exports_publicos(mod, "texto")

    assert "normalizar_unicode" not in mapa_limpio
    assert any(
        conflicto.get("symbol") == "normalizar_unicode" and conflicto.get("code") == "outside_public_api"
        for conflicto in conflictos
    )


def test_usar_datos_expone_longitud(monkeypatch):
    mod = ModuleType("datos")
    mod.__all__ = ["longitud"]
    mod.longitud = lambda valores: len(valores)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})
    interp.ejecutar_usar(_nodo("datos"))

    assert "longitud" in interp.contextos[-1].values
    assert interp.contextos[-1].get("longitud")([1, 2, 3]) == 3


def test_usar_texto_expone_recortar_repetir_quitar_acentos(monkeypatch):
    mod = ModuleType("texto")
    mod.__all__ = ["recortar", "repetir", "quitar_acentos"]
    mod.recortar = lambda texto: str(texto).strip()
    mod.repetir = lambda texto, veces=2: str(texto) * int(veces)
    mod.quitar_acentos = lambda texto: str(texto).translate(str.maketrans("áéíóú", "aeiou"))
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.ejecutar_usar(_nodo("texto"))

    simbolos = set(interp.contextos[-1].values)
    assert {"recortar", "repetir", "quitar_acentos"}.issubset(simbolos)


def test_regresion_usar_texto_superficie_ligera_y_sin_importerror():
    modulo = cobra_usar_loader.obtener_modulo_cobra_oficial("texto")
    mapa_limpio, conflictos = cobra_usar_loader.sanitizar_exports_publicos(modulo, "texto")

    assert not any(conflicto.get("code") == "missing_export_attr" for conflicto in conflictos)
    assert set(USAR_RUNTIME_EXPORT_OVERRIDES["texto"]).issubset(set(mapa_limpio))
    for simbolo in ("mayusculas", "minusculas", "prefijo_comun", "sufijo_comun", "recortar", "repetir", "quitar_acentos"):
        assert callable(mapa_limpio[simbolo])


def test_usar_numero_mantiene_es_finito_y_signo(monkeypatch):
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "signo"]
    mod.es_finito = lambda valor: valor not in (float("inf"), float("-inf"))
    mod.signo = lambda valor: -1 if valor < 0 else (1 if valor > 0 else 0)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.ejecutar_usar(_nodo("numero"))

    simbolos = set(interp.contextos[-1].values)
    assert "es_finito" in simbolos
    assert "signo" in simbolos


def test_usar_archivo_carga_existe_sin_error_metadata():
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"archivo": "archivo"})
    interp.ejecutar_usar(_nodo("archivo"))

    existe = interp.contextos[-1].get("existe")
    assert callable(existe)
    assert isinstance(existe("README.md"), bool)


def test_usar_carga_modulos_publicos_datos_numero_texto():
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos", "numero": "numero", "texto": "texto"})
    interp.ejecutar_usar(_nodo("datos"))
    interp.ejecutar_usar(_nodo("numero"))
    interp.ejecutar_usar(_nodo("texto"))

    simbolos = set(interp.contextos[-1].values.keys())
    assert "longitud" in simbolos
    assert "es_finito" in simbolos
    assert "recortar" in simbolos


def test_repl_funcional_minimo_datos_numero_archivo_via_runtime():
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos", "numero": "numero", "archivo": "archivo"})

    interp.ejecutar_usar(_nodo("datos"))
    assert interp.contextos[-1].get("longitud")([1, 2, 3]) == 3

    interp.ejecutar_usar(_nodo("numero"))
    assert interp.contextos[-1].get("es_finito")(10) is True

    interp.ejecutar_usar(_nodo("archivo"))
    assert isinstance(interp.contextos[-1].get("existe")("README.md"), bool)


def test_integridad_estatica_lexer_y_parser_sin_diff_inesperado():
    hashes_esperados = {
        "src/pcobra/core/lexer.py": "fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e",
        "src/pcobra/core/parser.py": "656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b",
        "src/pcobra/cobra/core/lexer.py": "fa65759ee1f0345e7ac3c48f1aa9d7d8f907916246c2d7f5f9151198c5a11887",
        "src/pcobra/cobra/core/parser.py": "578cea52a6cab8bccb0e41a895ed7664e4950a15cdaf49f059000200f352d41d",
    }
    for ruta, hash_esperado in hashes_esperados.items():
        contenido = Path(ruta).read_bytes()
        assert hashlib.sha256(contenido).hexdigest() == hash_esperado, f"Hash inesperado en {ruta}"
