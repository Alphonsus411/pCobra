from .base import ValidadorBase
from ..ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo
from ..usar_symbol_policy import make_usar_symbol_metadata, validate_usar_symbol_metadata


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
        metadata_base = make_usar_symbol_metadata(
            module_name=modulo,
            symbol_name=nombre,
            callable_obj=object(),
        )
        if metadata is not None:
            metadata_base = dict(metadata)
        validate_usar_symbol_metadata(nombre, metadata_base)
        clave_metadata = nombre
        if metadata_base.get("module") == modulo and metadata_base.get("symbol") == nombre:
            clave_metadata = str(metadata_base.get("symbol"))
        self._metadata_simbolos_usar[clave_metadata] = metadata_base

    def _es_wrapper_publico_permitido(self, nodo: NodoLlamadaFuncion) -> tuple[bool, str | None]:
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        if nodo.nombre != "existe":
            return False, "solo existe puede habilitarse desde usar"
        if ("archivo", "existe") not in self._simbolos_publicos_usar:
            return False, "existe no fue registrado por usar archivo"

        metadata = self._metadata_simbolos_usar.get(nodo.nombre)
        # Rechazo por defecto si metadata falta o no es dict.
        if not isinstance(metadata, dict):
            return False, "metadata de usar inexistente o inválida"

        # Validación explícita de contrato unificado para `existe`.
        if metadata.get("origin_kind") != "usar":
            return False, "metadata.origin_kind debe ser 'usar'"
        if metadata.get("module") != "archivo":
            return False, "metadata.module debe ser 'archivo'"
        if metadata.get("symbol") != "existe":
            return False, "metadata.symbol debe ser 'existe'"
        if metadata.get("sanitized") is not True:
            return False, "metadata.sanitized debe ser True"
        if metadata.get("public_api") is not True:
            return False, "metadata.public_api debe ser True"
        if metadata.get("backend_exposed") is not False:
            return False, "metadata.backend_exposed debe ser False"
        return True, None

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        permitido, motivo_rechazo = self._es_wrapper_publico_permitido(nodo)
        if nodo.nombre in self.PRIMITIVAS_PELIGROSAS and not permitido:
            detalle = ""
            if isinstance(self._metadata_simbolos_usar.get(nodo.nombre), dict) and motivo_rechazo is not None:
                detalle = f" (metadata usar inválida: {motivo_rechazo})"
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre}'{detalle}"
            )
        self.generic_visit(nodo)

    def visit_hilo(self, nodo: NodoHilo):
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        permitido, motivo_rechazo = self._es_wrapper_publico_permitido(nodo.llamada)
        if nodo.llamada.nombre in self.PRIMITIVAS_PELIGROSAS and not permitido:
            detalle = ""
            if isinstance(self._metadata_simbolos_usar.get(nodo.llamada.nombre), dict) and motivo_rechazo is not None:
                detalle = f" (metadata usar inválida: {motivo_rechazo})"
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.llamada.nombre}'{detalle}"
            )
        nodo.llamada.aceptar(self)

    def visit_llamada_metodo(self, nodo: NodoLlamadaMetodo):
        # No abrir bypass alternativo por método: también requiere ruta canónica autorizada.
        if nodo.nombre_metodo in self.PRIMITIVAS_PELIGROSAS:
            raise PrimitivaPeligrosaError(
                f"Uso de primitiva peligrosa: '{nodo.nombre_metodo}'"
            )
        self.generic_visit(nodo)
