from .base import ValidadorBase
from ..ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo


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

    def _es_wrapper_publico_permitido(self, nodo: NodoLlamadaFuncion) -> bool:
        # Único escape permitido para primitivas peligrosas:
        # usar archivo.existe con metadata de sanitización de API pública.
        if nodo.nombre != "existe":
            return False
        if ("archivo", "existe") not in self._simbolos_publicos_usar:
            return False
        metadata = self._metadata_simbolos_usar.get(nodo.nombre)
        if not isinstance(metadata, dict):
            return False

        if metadata.get("module") != "archivo":
            return False
        if metadata.get("exported_name") != "existe":
            return False
        if metadata.get("is_sanitized_wrapper") is not True:
            return False
        if metadata.get("public_api") is not True:
            return False
        return True

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        # Contrato: permitido solo si metadata canónica de usar+sanitización API pública.
        if nodo.nombre in self.PRIMITIVAS_PELIGROSAS and not self._es_wrapper_publico_permitido(nodo):
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre}'"
            )
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        if (
            nodo.llamada.nombre in self.PRIMITIVAS_PELIGROSAS
            and not self._es_wrapper_publico_permitido(nodo.llamada)
        ):
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.llamada.nombre}'"
            )
        nodo.llamada.aceptar(self)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        if nodo.nombre_metodo in self.PRIMITIVAS_PELIGROSAS and nodo.nombre_metodo != "existe":
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre_metodo}'"
            )
        self.generic_visit(nodo)
