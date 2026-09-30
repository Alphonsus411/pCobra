from pathlib import Path
from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.cobra.transpilers.common.utils import load_mapped_module
from pcobra.cobra.usar_loader import (
    obtener_cache_ast_import_cobra,
    canonicalizar_ruta_usar_proyecto,
    obtener_pila_carga_modulos_cobra_proyecto,
)
from pcobra.cobra.core.import_utils import cargar_ast_modulo
from pcobra.core.ast_nodes import NodoAST, NodoImport


def _cargar_ast_import_cobra(ruta_str):
    ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta_str)
    ast_cache = obtener_cache_ast_import_cobra()
    loading_stack = obtener_pila_carga_modulos_cobra_proyecto()

    if ruta_canonica not in ast_cache:
        # cargar_ast_modulo ya maneja la lectura del archivo y el parseo
        ast_cache[ruta_canonica] = cargar_ast_modulo(
            str(ruta_canonica),
            modules_path=str(ruta_canonica.parent),
            whitelist={ruta_canonica.parent},
            loading_stack=loading_stack,
        )
    return ruta_canonica, ast_cache[ruta_canonica]


def precargar_nombres_importados(self, nodos):
    """Reserva identificadores de todo el grafo ``import`` antes de emitirlo."""
    pendientes = list(nodos)
    visitados = set()

    while pendientes:
        actual = pendientes.pop()
        if actual is None or isinstance(actual, str):
            continue
        if isinstance(actual, (list, tuple)):
            pendientes.extend(actual)
            continue
        if isinstance(actual, NodoImport):
            _, ruta_str = load_mapped_module(actual.ruta, "python")
            if ruta_str.endswith(".cobra"):
                ruta_canonica, ast = _cargar_ast_import_cobra(ruta_str)
                if ruta_canonica in visitados:
                    continue
                visitados.add(ruta_canonica)
                self._nombres_identificadores.update(
                    self._recopilar_nombres_identificadores(ast)
                )
                pendientes.extend(ast)
            continue
        if isinstance(actual, NodoAST):
            pendientes.extend(vars(actual).values())


def visit_import(self, nodo):
    """Transpila una declaración de importación consultando el mapeo."""
    codigo, ruta_str = load_mapped_module(nodo.ruta, "python")

    if ruta_str.endswith(".cobra"):
        _, ast = _cargar_ast_import_cobra(ruta_str)
        self._nombres_identificadores.update(
            self._recopilar_nombres_identificadores(ast)
        )
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo += codigo + "\n"
