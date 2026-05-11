from pathlib import PurePosixPath
import re

from .base import ValidadorBase
from ..ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo, NodoValor


class PrimitivaPeligrosaError(Exception):
    """Se lanza cuando se utiliza una primitiva peligrosa."""

    pass


class ValidadorPrimitivaPeligrosa(ValidadorBase):
    """Validador que detecta llamadas a primitivas peligrosas."""

    WRAPPERS_PYTHON_MODULES_PERMITIDOS = frozenset({
        "pcobra.standard_library.archivo",
        "cobra.standard_library.archivo",
    })

    PRIMITIVAS_PELIGROSAS = {
        "leer_archivo",
        "escribir_archivo",
        "obtener_url",
        "hilo",
        "leer",
        "escribir",
        "existe",
        "eliminar",
        "enviar_post",
        "ejecutar",
        "listar_dir",
    }



    def __init__(self):
        super().__init__()
        self._simbolos_publicos_usar: set[tuple[str, str]] = set()
        self._metadata_simbolos_usar: dict[str, dict[str, object]] = {}

    def registrar_simbolo_publico_usar(
        self,
        nombre: str,
        modulo: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self._simbolos_publicos_usar.add((modulo, nombre))
        if metadata:
            self._metadata_simbolos_usar[nombre] = dict(metadata)

    @staticmethod
    def _ruta_permitida_en_wrapper(argumentos) -> bool:
        if not argumentos:
            return False
        primer_arg = argumentos[0]
        if not isinstance(primer_arg, NodoValor) or not isinstance(primer_arg.valor, str):
            return False
        ruta = primer_arg.valor.strip()
        if not ruta:
            return False
        if re.match(r"^[a-zA-Z]:[\\/]", ruta):
            return False
        if ruta.startswith("\\"):
            return False
        path = PurePosixPath(ruta)
        if path.is_absolute():
            return False
        if ".." in path.parts:
            return False
        return True

    def _es_wrapper_publico_permitido(self, nodo: NodoLlamadaFuncion) -> bool:
        if nodo.nombre != "existe":
            return False
        if ("archivo", nodo.nombre) not in self._simbolos_publicos_usar:
            return False
        metadata = self._metadata_simbolos_usar.get(nodo.nombre, {})
        origen_modulo = metadata.get("origen_modulo", metadata.get("module"))
        origen_canonico = metadata.get("canonical_module")
        origen_backend = metadata.get("python_module")
        origen_tipo = metadata.get("origen_tipo")
        es_publico = metadata.get("is_public_export") is True
        es_wrapper_sanitizado = metadata.get("is_sanitized_wrapper") is True
        if origen_modulo != "archivo" or origen_canonico != "archivo":
            return False
        if origen_tipo is not None and origen_tipo != "public_wrapper":
            return False
        if origen_backend not in self.WRAPPERS_PYTHON_MODULES_PERMITIDOS:
            return False
        if not es_publico or not es_wrapper_sanitizado:
            return False
        return self._ruta_permitida_en_wrapper(nodo.argumentos)

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        if nodo.nombre in self.PRIMITIVAS_PELIGROSAS and not self._es_wrapper_publico_permitido(nodo):
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre}'"
            )
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        if nodo.llamada.nombre in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.llamada.nombre}'"
            )
        nodo.llamada.aceptar(self)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        if nodo.nombre_metodo in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre_metodo}'"
            )
        self.generic_visit(nodo)
