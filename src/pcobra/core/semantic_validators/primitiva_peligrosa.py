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
        if ("archivo", nodo.nombre) not in self._simbolos_publicos_usar:
            return False
        metadata = self._metadata_simbolos_usar.get(nodo.nombre)
        if not isinstance(metadata, dict) or not metadata:
            return False
        origen_modulo = metadata.get("origen_modulo") or metadata.get("origin_module")
        origen_canonico = metadata.get("canonical_module")
        origen_backend = metadata.get("python_module")
        origen_tipo = metadata.get("origen_tipo")
        fue_introducido_por_usar = (
            metadata.get("introduced_by_usar") is True
            or metadata.get("introduced_by") == "usar"
        )
        es_publico = (
            metadata.get("is_public_export") is True
            or metadata.get("public_api") is True
        )
        es_wrapper_sanitizado = (
            metadata.get("is_sanitized_wrapper") is True
            or metadata.get("safe_wrapper") is True
        )
        if origen_modulo != "archivo" or origen_canonico != "archivo":
            return False
        if not fue_introducido_por_usar:
            return False
        if origen_tipo != "public_wrapper":
            return False
        if origen_backend not in self.WRAPPERS_PYTHON_MODULES_PERMITIDOS:
            return False
        if not es_publico or not es_wrapper_sanitizado:
            return False
        return metadata.get("exported_name") == "existe"

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
