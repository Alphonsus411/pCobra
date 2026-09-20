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


def cargar_ast_import_cobra(nodo):
    """Resuelve y carga un import Cobra mediante la caché compartida existente."""
    codigo, ruta_str = load_mapped_module(nodo.ruta, "python")
    if not ruta_str.endswith(".cobra"):
        return codigo, None, None

    ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta_str)
    ast_cache = obtener_cache_ast_import_cobra()
    if ruta_canonica not in ast_cache:
        # cargar_ast_modulo ya maneja la lectura del archivo y el parseo.
        ast_cache[ruta_canonica] = cargar_ast_modulo(
            str(ruta_canonica),
            modules_path=str(ruta_canonica.parent),
            whitelist={ruta_canonica.parent},
            loading_stack=obtener_pila_carga_modulos_cobra_proyecto(),
        )
    return codigo, ruta_canonica, ast_cache[ruta_canonica]


def visit_import(self, nodo):
    """Transpila una declaración de importación consultando el mapeo."""
    codigo, ruta_canonica, ast = cargar_ast_import_cobra(nodo)

    if ruta_canonica is not None:
        rutas_en_emision = self._rutas_importacion_en_emision
        if ruta_canonica in rutas_en_emision:
            cadena = " -> ".join(
                str(ruta) for ruta in (*rutas_en_emision, ruta_canonica)
            )
            raise ImportError(f"Ciclo de módulos detectado en import: {cadena}")

        self._nombres_identificadores.update(
            self._recopilar_nombres_identificadores(ast)
        )
        rutas_en_emision.append(ruta_canonica)
        try:
            for subnodo in ast:
                subnodo.aceptar(self)
        finally:
            rutas_en_emision.pop()
    else:
        self.codigo += codigo + "\n"
