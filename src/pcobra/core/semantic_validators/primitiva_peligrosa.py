from pathlib import PurePosixPath

from .base import ValidadorBase
from ..ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo, NodoValor


class PrimitivaPeligrosaError(Exception):
    """Se lanza cuando se utiliza una primitiva peligrosa."""

    pass


class ValidadorPrimitivaPeligrosa(ValidadorBase):
    """Validador que detecta llamadas a primitivas peligrosas."""

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

    def registrar_simbolo_publico_usar(self, nombre: str, modulo: str) -> None:
        self._simbolos_publicos_usar.add((modulo, nombre))

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
