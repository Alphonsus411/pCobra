from .base import ValidadorBase
from ..ast_nodes import NodoLlamadaFuncion, NodoHilo, NodoLlamadaMetodo
from ..usar_symbol_policy import validate_usar_symbol_metadata


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
        """Registra un símbolo público de ``usar`` con metadata canónica validada.

        Este método **solo** acepta metadata canónica ya validada por el contrato
        de ``usar`` (normalmente construida con
        :func:`pcobra.core.usar_symbol_policy.make_usar_symbol_metadata`).
        """
        if metadata is None:
            raise ValueError(
                "Metadata inválida para símbolo usar: se requiere metadata canónica preconstruida"
            )
        metadata_validada = validate_usar_symbol_metadata(nombre, metadata)
        if metadata_validada.get("module") != modulo:
            raise ValueError(
                f"Metadata inválida para símbolo usar '{nombre}': module no coincide con registro"
            )
        self._simbolos_publicos_usar.add((modulo, nombre))
        self._metadata_simbolos_usar[nombre] = dict(metadata_validada)

    def _es_wrapper_publico_permitido(self, nodo: NodoLlamadaFuncion) -> tuple[bool, str | None]:
        # Contrato de seguridad: No basta el nombre del símbolo.
        # Contrato de seguridad: Solo metadata canónica de `usar` + API pública sanitizada.
        if nodo.nombre != "existe":
            return False, "solo existe puede habilitarse desde usar"
        if ("archivo", "existe") not in self._simbolos_publicos_usar:
            return False, "existe no fue registrado por usar archivo"

        metadata = self._metadata_simbolos_usar.get(nodo.nombre)
        if metadata is None:
            return False, "metadata de usar inexistente"

        # Única puerta de validación del contrato canónico.
        try:
            metadata_validada = validate_usar_symbol_metadata(nodo.nombre, metadata)
        except ValueError as exc:
            return False, str(exc)

        # Restricción semántica adicional del validador (no reemplaza la validación canónica).
        if metadata_validada.get("module") != "archivo":
            return False, "metadata.module debe ser 'archivo'"
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
