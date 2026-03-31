from __future__ import annotations

from pathlib import Path

from pcobra.core import import_utils
from pcobra.core.ast_nodes import NodoAsignacion, NodoClase, NodoFuncion


def _ast_falso_desde_archivo(ruta: str):
    nodos = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if linea.startswith("var:"):
            nombre = linea.split(":", 1)[1].strip()
            nodos.append(NodoAsignacion(nombre, 1))
        elif linea.startswith("func:"):
            nombre = linea.split(":", 1)[1].strip()
            nodos.append(NodoFuncion(nombre, [], []))
        elif linea.startswith("clase:"):
            nombre = linea.split(":", 1)[1].strip()
            nodos.append(NodoClase(nombre, []))
    return nodos


def test_obtener_simbolos_invalida_cache_si_cambia_archivo(tmp_path, monkeypatch):
    modulo = tmp_path / "modulo.co"
    modulo.write_text("func:saludar\n", encoding="utf-8")

    monkeypatch.setattr(import_utils, "MODULES_PATH", tmp_path)
    monkeypatch.setattr(import_utils, "IMPORT_WHITELIST", {tmp_path})
    import_utils._simbolos_modulo_cache.cache_clear()

    llamadas = {"n": 0}

    def fake_cargar_ast_modulo(ruta: str, **kwargs):
        llamadas["n"] += 1
        return _ast_falso_desde_archivo(ruta)

    monkeypatch.setattr(import_utils, "cargar_ast_modulo", fake_cargar_ast_modulo)

    simbolos_v1 = import_utils.obtener_simbolos_modulo(str(modulo))
    assert simbolos_v1 == {("saludar", "funcion")}

    modulo.write_text("clase:Persona\n", encoding="utf-8")
    simbolos_v2 = import_utils.obtener_simbolos_modulo(str(modulo))

    assert simbolos_v2 == {("Persona", "clase")}
    assert llamadas["n"] == 2


def test_obtener_simbolos_reintenta_si_archivo_cambia_entre_fingerprint_y_parseo(
    tmp_path, monkeypatch
):
    modulo = tmp_path / "modulo_race.co"
    modulo.write_text("var:uno\n", encoding="utf-8")

    monkeypatch.setattr(import_utils, "MODULES_PATH", tmp_path)
    monkeypatch.setattr(import_utils, "IMPORT_WHITELIST", {tmp_path})
    import_utils._simbolos_modulo_cache.cache_clear()

    llamadas = {"n": 0}

    def fake_cargar_ast_modulo(ruta: str, **kwargs):
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            Path(ruta).write_text("func:dos\n", encoding="utf-8")
            raise import_utils._ArchivoModuloInestableError("archivo cambió")
        return _ast_falso_desde_archivo(ruta)

    monkeypatch.setattr(import_utils, "cargar_ast_modulo", fake_cargar_ast_modulo)

    simbolos = import_utils.obtener_simbolos_modulo(str(modulo))

    assert simbolos == {("dos", "funcion")}
    assert llamadas["n"] == 2
