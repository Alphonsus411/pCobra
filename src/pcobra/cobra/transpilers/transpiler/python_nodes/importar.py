from pathlib import Path
from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.cobra.transpilers.common.utils import load_mapped_module
from pcobra.cobra.usar_loader import obtener_cache_ast_import_co, canonicalizar_ruta_usar_proyecto, obtener_pila_carga_modulos_cobra_proyecto
from pcobra.core.import_utils import cargar_ast_modulo


def visit_import(self, nodo):
    """Transpila una declaración de importación consultando el mapeo."""
    codigo, ruta_str = load_mapped_module(nodo.ruta, "python")

    if ruta_str.endswith(".co"):
        ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta_str)
        ast_cache = obtener_cache_ast_import_co()
        loading_stack = obtener_pila_carga_modulos_cobra_proyecto()

        if ruta_canonica in ast_cache:
            ast = ast_cache[ruta_canonica]
        else:
            # cargar_ast_modulo ya maneja la lectura del archivo y el parseo
            ast = cargar_ast_modulo(str(ruta_canonica), loading_stack=loading_stack)
            ast_cache[ruta_canonica] = ast

        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo += codigo + "\n"
