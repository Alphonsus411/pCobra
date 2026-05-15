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
        metadata_base = {
            "module": "archivo",
            "exported_name": nombre,
            "is_sanitized_wrapper": True,
            "public_api": True,
            "introduced_by_usar": True,
            # Alias históricos requeridos por compatibilidad.
            "origen_modulo": "archivo",
            "canonical_module": "archivo",
            "origin_module": "archivo",
        }
        if metadata:
            metadata_base.update(dict(metadata))
        self._metadata_simbolos_usar[nombre] = metadata_base

    def _es_wrapper_publico_permitido(self, nodo: NodoLlamadaFuncion) -> bool:
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
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
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        if nodo.nombre in self.PRIMITIVAS_PELIGROSAS and not self._es_wrapper_publico_permitido(nodo):
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre}'"
            )
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        if (
            nodo.llamada.nombre in self.PRIMITIVAS_PELIGROSAS
            and not self._es_wrapper_publico_permitido(nodo.llamada)
        ):
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.llamada.nombre}'"
            )
        nodo.llamada.aceptar(self)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        # No abrir bypass alternativo por método: también requiere ruta canónica autorizada.
        if nodo.nombre_metodo in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre_metodo}'"
            )
        self.generic_visit(nodo)
