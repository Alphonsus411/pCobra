"""Implementación del intérprete del lenguaje Cobra."""

import ast
import logging
import os
import hashlib
import inspect
import math
import multiprocessing
import threading
import warnings
from pathlib import Path
from typing import Any, Mapping, Optional
from pcobra.cobra.usar_loader import ModuloFueraCatalogoPublicoError, usar_modulo
from pcobra.cobra.usar_policy import USAR_COBRA_PUBLIC_MODULES

from .lexer import (
    Token,
    TipoToken,
)
from .optimizations import (
    optimize_constants,
    remove_dead_code,
    inline_functions,
    eliminate_common_subexpressions,
)
from .type_utils import (
    verificar_sumables,
    verificar_numeros,
    verificar_comparables,
    verificar_booleanos,
    verificar_booleano,
)
from .ast_nodes import (
    NodoAsignacion,
    NodoBloque,
    NodoCondicional,
    NodoBucleMientras,
    NodoPara,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoHolobit,
    NodoHilo,
    NodoClase,
    NodoInstancia,
    NodoAtributo,
    NodoIdentificador,
    NodoValor,
    NodoImprimir,
    NodoLista,
    NodoRetorno,
    NodoYield,
    NodoEsperar,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoTryCatch,
    NodoThrow,
    NodoImport,
    NodoUsar,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoWith,
    NodoImportDesde,
    NodoExport,
    NodoAST,
    NodoRomper,
    NodoContinuar,
)
from .memoria.gestor_memoria import GestorMemoriaGenetico
from .internal_ir import InternalIRModule, build_internal_ir
from .semantic_validators import (
    construir_cadena,
    PrimitivaPeligrosaError,
)
from .semantic_validators.base import ValidadorBase
from .semantico import AnalizadorSemantico
from .cobra_config import limite_nodos
from .import_utils import (
    MODULES_PATH as _DEFAULT_MODULES_PATH,
    IMPORT_WHITELIST,
    ruta_import_permitida,
    cargar_ast_modulo,
)
from .utils import validar_ast_estructural, ErrorEstructuraAST
from .errors import CondicionNoBooleanaError
from .usar_symbol_policy import (
    build_and_validate_usar_symbol_metadata,
    normalizar_metadata_simbolo_usar,
    validate_usar_symbol_metadata,
)
from .environment import Environment
from pcobra.corelibs.datos import longitud
from pcobra.cobra.usar_loader import descubrir_raiz_proyecto

MODULES_PATH = _DEFAULT_MODULES_PATH
REPL_USAR_EXTERNAL_MODULE_ERROR = "usar_error[modulo_no_permitido]: módulo externo no permitido en REPL estricto (solo alias oficiales Cobra)"


def _usar_modulo_con_estado_aislado(
    nombre: str,
    *,
    project_root: Path,
    current_file: Path | None,
    module_cache: dict[Path, dict[str, object]],
    loading_stack: list[Path],
    contexto_proyecto_verificado: bool,
    safe_mode: bool,
) -> Mapping[str, object]:
    """Llama a ``usar_modulo`` pasando estado aislado si la función lo soporta."""

    parametros = inspect.signature(usar_modulo).parameters
    kwargs: dict[str, Any] = {
        "project_root": project_root,
        "current_file": current_file,
    }
    if any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in parametros.values()
    ) or ("module_cache" in parametros and "loading_stack" in parametros):
        kwargs["module_cache"] = module_cache
        kwargs["loading_stack"] = loading_stack
    if any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in parametros.values()
    ) or ("contexto_proyecto_verificado" in parametros):
        kwargs["contexto_proyecto_verificado"] = contexto_proyecto_verificado
    if (
        any(
            param.kind == inspect.Parameter.VAR_KEYWORD for param in parametros.values()
        )
        or "safe_mode" in parametros
    ):
        kwargs["safe_mode"] = safe_mode
    return usar_modulo(nombre, **kwargs)


USAR_DIRECT_BACKEND_IMPORT_ERROR = (
    "usar_error[backend_import_directo]: import directo de backend no permitido en usar"
)
USAR_NON_CANONICAL_MODULE_ERROR = "usar_error[modulo_no_canonico]: el módulo solicitado no es canónico; use el alias oficial Cobra"
USAR_NON_PUBLIC_MODULE_ERROR = "usar_error[modulo_fuera_catalogo_publico]: el módulo solicitado está fuera de USAR_COBRA_PUBLIC_MODULES"
USAR_NON_FACING_MODULE_ERROR = "usar_error[modulo_no_cobra_facing]: el módulo solicitado no está marcado como Cobra-facing"
USAR_INVALID_EXPORT_ERROR = "usar_error[export_invalido]"
USAR_SYMBOL_CONFLICT_ERROR = "usar_error[conflicto_simbolo]"
USAR_MODULE_NOT_FOUND_ERROR = "usar_error[modulo_no_encontrado]"
USAR_MODULE_LOAD_ERROR = "usar_error[carga_modulo_error]"
USAR_COLLISION_STRICT_ERROR = "strict_error"
USAR_COLLISION_WARN_ALIAS_REQUIRED = "warn_alias_required"
_USAR_COLLISION_POLICIES = frozenset(
    {USAR_COLLISION_STRICT_ERROR, USAR_COLLISION_WARN_ALIAS_REQUIRED}
)


def formatear_error_usar_usuario(
    codigo: str, modulo: str, contexto_minimo: str | None = None
) -> str:
    """Devuelve errores cortos y legibles para la salida de usuario en `usar`."""
    codigos = {
        "conflicto_simbolo": USAR_SYMBOL_CONFLICT_ERROR,
        "export_invalido": USAR_INVALID_EXPORT_ERROR,
        "modulo_no_encontrado": USAR_MODULE_NOT_FOUND_ERROR,
        "carga_modulo_error": USAR_MODULE_LOAD_ERROR,
    }
    mensajes = {
        "modulo_fuera_catalogo": f"No se puede usar '{modulo}': módulo fuera del catálogo público.",
        "conflicto_simbolo": f"No se puede usar '{modulo}': hay conflicto de símbolos en el contexto actual.",
        "export_invalido": f"No se puede usar '{modulo}': no hay símbolos exportables válidos.",
        "modulo_no_encontrado": f"No se puede usar '{modulo}': módulo no encontrado.",
        "carga_modulo_error": f"No se puede usar '{modulo}': error al cargar el módulo.",
    }
    base = mensajes.get(codigo, f"No se puede usar '{modulo}'.")
    if codigo in codigos:
        codigo_publico = codigos[codigo].split(":", 1)[0]
        base = f"{codigo_publico}: {base}"
    if contexto_minimo:
        return f"{base} {contexto_minimo}"
    return base


def _usar_error_esperado(exc: Exception) -> bool:
    """Identifica errores esperados del contrato de `usar`."""
    return isinstance(exc, (PermissionError, NameError, ImportError, ValueError))


_ERRORES_USUARIO_ELEMENTO: dict[type[Exception], set[str]] = {
    IndexError: {"índice fuera de rango"},
    TypeError: {"índice debe ser entero", "objeto no indexable"},
}


def _usar_detalle_habilitado() -> bool:
    """Determina si `usar` puede exponer detalles extendidos en salida de error."""
    return _runtime_debug_enabled() or InterpretadorCobra._debug_trazas_habilitadas()


def _resumir_modulos_permitidos_usar(limite: int = 10) -> str:
    """Devuelve una lista corta de módulos públicos para errores de usuario."""

    return ", ".join(USAR_COBRA_PUBLIC_MODULES[:limite])


def _error_usuario_modulo_fuera_catalogo(
    modulo: str,
    detalle: Exception,
    *,
    repl_estricto: bool,
    incluir_detalle: bool,
) -> PermissionError:
    """Crea el error público según el contrato directo o del REPL."""

    if repl_estricto:
        mensaje = (
            f"Importación no permitida en 'usar': '{modulo}'. Es un módulo "
            "backend/no canónico y no forma parte de la API pública. "
            f"{REPL_USAR_EXTERNAL_MODULE_ERROR}. "
            f"Módulos permitidos: {_resumir_modulos_permitidos_usar()}."
        )
    else:
        mensaje = formatear_error_usar_usuario("modulo_fuera_catalogo", modulo)

    codigo_publico = USAR_NON_PUBLIC_MODULE_ERROR.split(":", 1)[0]
    mensaje = f"{mensaje} {codigo_publico}"
    if incluir_detalle:
        detalle_publico = USAR_NON_PUBLIC_MODULE_ERROR.split(":", 1)[1].strip()
        mensaje = f"{mensaje}: {detalle_publico}. {detalle}"
    return PermissionError(mensaje)


def _runtime_debug_enabled() -> bool:
    """Habilita diagnóstico puntual de runtime vía entorno."""
    return os.getenv("PCOBRA_DEBUG_RUNTIME", "").strip() == "1"


def _resumen_conflictos_usar(conflictos: list[object]) -> str:
    """Devuelve un resumen compacto de conflictos para logs no verbosos."""
    if not conflictos:
        return "count=0"
    muestra = ",".join(str(conflicto) for conflicto in conflictos[:3])
    resto = len(conflictos) - 3
    sufijo = f",+{resto}" if resto > 0 else ""
    return f"count={len(conflictos)} sample=[{muestra}{sufijo}]"


def _ruta_import_permitida(ruta: str) -> bool:
    """Indica si una ruta está autorizada para importarse."""

    _sincronizar_config_import()
    return ruta_import_permitida(ruta, MODULES_PATH, IMPORT_WHITELIST)


def _sincronizar_config_import() -> None:
    """Mantiene sincronizados los valores compartidos con :mod:`import_utils`."""

    from . import import_utils as _import_utils

    _import_utils.MODULES_PATH = MODULES_PATH
    _import_utils.IMPORT_WHITELIST = IMPORT_WHITELIST


class ExcepcionCobra(Exception):
    def __init__(self, valor):
        super().__init__(valor)
        self.valor = valor


class _ControlRomper(Exception):
    """Señal interna para cortar la ejecución del bucle actual."""


class _ControlContinuar(Exception):
    """Señal interna para avanzar a la siguiente iteración del bucle."""


class _ControlRetorno(Exception):
    """Señal interna que transporta el valor devuelto por una función."""

    def __init__(self, valor):
        super().__init__()
        self.valor = valor


class _EstadoEjecucion(threading.local):
    """Estado mutable que pertenece exclusivamente a una ejecución/hilo.

    Inventario: las pilas de scopes y de bloques de memoria locales,
    ``call_depth``, el conjunto temporal de evaluación recursiva y la
    profundidad de aislamiento del worker. Las señales de control
    (``_ControlRetorno``, ``_ControlRomper`` y ``_ControlContinuar``), junto
    con ``visitados`` y demás temporales de evaluación, viajan por la pila de
    Python y por tanto ya son locales a cada llamada.

    El entorno global se conserva por referencia: los workers crean scopes
    locales cuyo padre léxico apunta a él. Cuando una llamada necesita aislar
    los bindings capturados se usa una copia *superficial* de ``values`` para
    preservar las referencias léxicas a objetos compartidos.
    """

    def __init__(self) -> None:
        self.contextos: list[Environment] | None = None
        self.mem_contextos: list[dict[str, tuple[int, int]]] | None = None
        self.call_depth = 0
        self.eval_stack: set[tuple[int, int]] = set()
        self.thread_isolation_depth = 0


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""

    @staticmethod
    def _debug_trazas_habilitadas() -> bool:
        """Indica si las trazas internas de depuración están activadas."""
        return os.getenv("PCOBRA_DEBUG_TRACES", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    def _trace_debug(self, mensaje: str) -> None:
        """Imprime trazas internas solo cuando el modo debug está activo."""
        if self.in_execution() and self._debug_trazas_habilitadas():
            print(mensaje)

    @staticmethod
    def _valor_literal(valor: Any) -> Any:
        """Convierte representaciones textuales válidas de cadenas a runtime."""
        if not isinstance(valor, str) or len(valor) < 2:
            return valor
        if valor[0] not in {"'", '"'} or valor[-1] != valor[0]:
            return valor
        try:
            normalizado = ast.literal_eval(valor)
        except (SyntaxError, ValueError):
            return valor
        return normalizado if isinstance(normalizado, str) else valor

    @staticmethod
    def _registrar_auditoria_validador(
        ruta_real: str,
        resultado: str,
        razon: str | None = None,
        *,
        hash_corto: str | None = None,
        fase: str | None = None,
    ) -> None:
        """Registra eventos de auditoría durante la carga de validadores extra."""
        payload = {
            "evento": "validador_extra",
            "ruta_real": ruta_real,
            "resultado": resultado,
        }
        if razon:
            payload["razon"] = razon
        if hash_corto:
            payload["hash_corto"] = hash_corto
        if fase:
            payload["fase"] = fase
        logging.warning("Auditoria validador extra: %s", payload)

    @staticmethod
    def _cargar_validadores(ruta):
        """Carga descriptores en un worker aislado y construye clases admitidas."""

        ruta_abs = os.path.abspath(ruta)
        if not _ruta_import_permitida(ruta_abs):
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_abs, "rechazado", "fuera_whitelist"
            )
            raise ImportError(f"Módulo fuera de la lista blanca: {ruta}")
        ruta_real = os.path.realpath(ruta_abs)

        try:
            with open(ruta_real, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real, "rechazado", "archivo_no_encontrado"
            )
            raise FileNotFoundError(
                f"No se encontró el archivo de validadores: {ruta}"
            ) from e
        hash_corto = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]

        from .validator_worker import run_validator_worker

        context = multiprocessing.get_context("spawn")
        parent, child = context.Pipe(duplex=False)
        process = context.Process(
            target=run_validator_worker,
            args=(child, {"source": source, "filename": ruta_real}),
        )
        process.start()
        child.close()
        timeout = float(os.getenv("PCOBRA_VALIDATOR_TIMEOUT", "2"))
        response = None
        try:
            if parent.poll(timeout):
                response = parent.recv()
            else:
                process.terminate()
                process.join(0.5)
                if process.is_alive():
                    process.kill()
                InterpretadorCobra._registrar_auditoria_validador(
                    ruta_real,
                    "rechazado",
                    "timeout",
                    hash_corto=hash_corto,
                    fase="worker",
                )
                raise ImportError("El validador adicional superó el tiempo permitido.")
        except EOFError:
            response = None
        finally:
            if process.is_alive():
                process.terminate()
            process.join()
            parent.close()

        if not isinstance(response, dict) or response.get("estado") != "ok":
            codigo = (
                response.get("codigo")
                if isinstance(response, dict)
                else "worker_terminado"
            )
            if (
                response is None
                and process.exitcode is not None
                and process.exitcode < 0
            ):
                codigo = "cpu_excedida"
            mensajes = {
                "import_no_permitido": "No se permiten importaciones en validadores adicionales.",
                "atributo_magico_no_permitido": "Se detectó un atributo mágico no permitido.",
                "introspeccion_no_permitida": "Se detectó introspección no permitida.",
                "memoria_excedida": "El validador adicional excede los límites de memoria permitidos.",
                "cpu_excedida": "El validador adicional superó el tiempo permitido.",
                "resultado_no_serializable": "El resultado del validador no es serializable.",
                "descriptor_invalido": "El validador adicional devolvió un descriptor inválido.",
                "worker_terminado": "El proceso del validador terminó sin resultado.",
                "sintaxis_invalida": "El validador adicional contiene sintaxis inválida.",
                "error_en_ejecucion": "El validador adicional falló durante su ejecución aislada.",
            }
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                str(codigo),
                hash_corto=hash_corto,
                fase="worker",
            )
            raise ImportError(
                mensajes.get(
                    codigo, "No se pudo cargar el validador adicional de forma segura."
                )
            )

        from .semantic_validators import (
            ValidadorImportSeguro,
            ValidadorPrimitivaPeligrosa,
            ValidadorProhibirReflexion,
            ValidadorSistemaArchivos,
        )

        registry = {
            "import_seguro": ValidadorImportSeguro,
            "primitiva_peligrosa": ValidadorPrimitivaPeligrosa,
            "reflexion_segura": ValidadorProhibirReflexion,
            "sistema_archivos": ValidadorSistemaArchivos,
        }
        validators = []
        for descriptor in response.get("validadores", []):
            validator_class = registry.get(descriptor["nombre"])
            if validator_class is None:
                raise ImportError(
                    "El descriptor solicita un validador no preautorizado."
                )
            try:
                validators.append(validator_class(**descriptor["parametros"]))
            except (TypeError, ValueError) as exc:
                raise ImportError(
                    "Parámetros inválidos para el validador preautorizado."
                ) from exc
        InterpretadorCobra._registrar_auditoria_validador(
            ruta_real,
            "permitido",
            hash_corto=hash_corto,
            fase="exec",
        )
        return validators

    def __init__(
        self,
        safe_mode: bool = True,
        extra_validators=None,
        main_file: Path | str | None = None,
    ):
        """Crea un nuevo interpretador.

        Parameters
        ----------
        safe_mode: bool, optional
            Indica si el intérprete debe ejecutarse en modo seguro. Está
            activado por defecto y valida cada nodo utilizando la cadena
            devuelta por :func:`construir_cadena`, restringiendo primitivas
            como ``import`` o ``hilo``.
        extra_validators: list | str, optional
            Ruta a un módulo que defina ``VALIDADORES_EXTRA`` mediante
            descriptores declarativos. Las instancias y callables se rechazan.
        main_file: Path | str, optional
            Archivo principal conocido por CLI/runtime para resolver módulos de
            proyecto con ``usar`` desde la raíz canonicalizada.
        """
        extra = extra_validators
        if isinstance(extra, str):
            extra = self._cargar_validadores(extra)
        elif isinstance(extra, list) and all(
            isinstance(validador, ValidadorBase) for validador in extra
        ):
            extra = list(extra)
        elif extra:
            raise TypeError(
                "Los validadores adicionales deben indicarse mediante una ruta "
                "con descriptores declarativos o instancias preautorizadas; "
                "no se admiten callables arbitrarios."
            )

        self.safe_mode = safe_mode
        # Regla de fases: analysis = sin efectos, execution = con efectos.
        # Por defecto iniciamos en ejecución para preservar compatibilidad fuera del REPL.
        self.mode = "execution"

        self._main_file: Path | None = None
        self._project_root: Path = Path.cwd().resolve()
        self._contexto_proyecto_verificado = False
        self.configurar_archivo_principal(main_file)

        self._validador = (
            construir_cadena(
                extra,
                emitir_side_effects=True,
                main_file=self._main_file,
                project_root=self._project_root,
            )
            if safe_mode
            else None
        )
        # Analizador semántico persistente para mantener contexto entre ejecuciones
        self.analizador = AnalizadorSemantico()
        # Conjunto para evitar validar el mismo nodo varias veces
        self._validados = set()
        # Estado estrictamente por ejecución. El entorno raíz sigue siendo la
        # referencia léxica compartida desde la que parten los workers.
        self._execution_state = _EstadoEjecucion()
        self._global_environment = Environment()
        self._global_mem_context: dict[str, tuple[int, int]] = {}
        self.contextos = [self._global_environment]
        self.funciones_nativas = {"longitud": longitud}
        # Mapa paralelo para gestionar bloques de memoria por contexto
        self.mem_contextos = [self._global_mem_context]
        # Gestor genético de estrategias de memoria
        self.gestor_memoria = GestorMemoriaGenetico()
        self.estrategia = self.gestor_memoria.poblacion[0]
        self.op_memoria = 0
        self._eval_stack = set()
        self._call_depth = 0
        # Orden de bloqueo único: ninguna ruta adquiere otro lock mientras
        # mantiene éste. Solo protege el gestor/estrategia de memoria común.
        self._thread_execution_lock = threading.RLock()
        self._thread_isolation_depth = 0
        # Funciones Cobra declaradas en el AST fuente. Se mantiene separada del
        # entorno de variables para que los optimizadores puedan eliminar nodos
        # ``NodoFuncion`` sin impedir que sus nombres sigan siendo resolubles
        # como valores/callbacks en expresiones.
        self._funciones_declaradas_valor: dict[str, dict[str, object]] = {}
        # Último IR generado a partir del AST ejecutado
        self.ultimo_ir: Optional[InternalIRModule] = None
        # Restricción opcional para `usar` en REPL/evaluador incremental.
        self._repl_usar_alias_map: dict[str, str] | None = None
        self._usar_collision_policy = USAR_COLLISION_STRICT_ERROR
        # Metadatos de símbolos inyectados por `usar` para soportar reimport idempotente.
        # nombre_simbolo -> {"module": str, "exported_name": str, "callable_id": int}
        self._usar_symbol_metadata: dict[str, dict[str, object]] = {}
        self._current_module_stack: list[Path] = []
        self._usar_module_cache: dict[Path, dict[str, object]] = {}
        self._usar_loading_stack: list[Path] = []
        self._import_ast_cache: dict[Path, list[object]] = {}
        self._import_execution_stack: list[Path] = []
        self._imported_module_paths: set[Path] = set()
        # Debe ejecutarse siempre después de crear _validador y _usar_symbol_metadata.
        self.asegurar_estado_runtime_inicial()

    @property
    def contextos(self) -> list[Environment]:
        contextos = self._execution_state.contextos
        if contextos is None:
            contextos = [self._global_environment]
            self._execution_state.contextos = contextos
        return contextos

    @contextos.setter
    def contextos(self, value: list[Environment]) -> None:
        self._execution_state.contextos = value

    @property
    def mem_contextos(self) -> list[dict[str, tuple[int, int]]]:
        contextos = self._execution_state.mem_contextos
        if contextos is None:
            contextos = [self._global_mem_context]
            self._execution_state.mem_contextos = contextos
        return contextos

    @mem_contextos.setter
    def mem_contextos(self, value: list[dict[str, tuple[int, int]]]) -> None:
        self._execution_state.mem_contextos = value

    @property
    def _call_depth(self) -> int:
        return self._execution_state.call_depth

    @_call_depth.setter
    def _call_depth(self, value: int) -> None:
        self._execution_state.call_depth = value

    @property
    def _eval_stack(self) -> Any:
        return self._execution_state.eval_stack

    @_eval_stack.setter
    def _eval_stack(self, value: Any) -> None:
        self._execution_state.eval_stack = value

    @property
    def _thread_isolation_depth(self) -> int:
        return self._execution_state.thread_isolation_depth

    @_thread_isolation_depth.setter
    def _thread_isolation_depth(self, value: int) -> None:
        self._execution_state.thread_isolation_depth = value

    def asegurar_estado_runtime_inicial(self) -> None:
        """Garantiza estado mínimo de runtime para metadata de `usar`.

        Este método es idempotente: solo crea contenedores cuando faltan o
        cuando están en ``None``, sin reescribir diccionarios ya poblados.
        """
        self._normalizar_metadata_usar_en_inicializacion()

    def _normalizar_metadata_usar_en_inicializacion(self) -> None:
        """Normaliza contenedores mínimos de metadata para etapa='inicialización'.

        Reglas:
        - Si falta ``_usar_symbol_metadata`` o está en ``None``, crear ``{}``.
        - Si falta ``_metadata_simbolos_usar`` en validador o está en ``None``,
          crear ``{}``.
        - Si ``_metadata_simbolos_usar`` existe y no es ``dict``, no corregir de
          forma silenciosa aquí; la validación estricta en etapa='pre-auditoría'
          debe fallar con ``invalid_container``.
        """
        if (
            not hasattr(self, "_usar_symbol_metadata")
        ) or self._usar_symbol_metadata is None:
            self._usar_symbol_metadata = {}

        validador = getattr(self, "_validador", None)
        if validador is not None:
            if not hasattr(validador, "_metadata_simbolos_usar"):
                validador._metadata_simbolos_usar = {}
            elif validador._metadata_simbolos_usar is None:
                validador._metadata_simbolos_usar = {}

    def configurar_restriccion_usar_repl(
        self, alias_map: dict[str, str] | None
    ) -> None:
        """Configura whitelist explícita de módulos `usar` para flujo REPL.

        Cuando ``alias_map`` es ``None``, no se aplica restricción adicional.
        """
        self._repl_usar_alias_map = alias_map.copy() if alias_map is not None else None

    def configurar_politica_colision_usar(self, policy: str) -> None:
        """Configura la política de colisión para ``usar`` en runtime."""
        if policy not in _USAR_COLLISION_POLICIES:
            raise ValueError(f"Política de colisión inválida: {policy}")
        self._usar_collision_policy = policy

    def in_execution(self) -> bool:
        """Indica si el intérprete se encuentra en fase de ejecución."""
        return self.mode == "execution"

    def _set_mode(self, mode: str) -> str:
        """Actualiza la fase del intérprete y retorna el modo previo."""
        if mode not in {"analysis", "execution"}:
            raise ValueError(f"Modo inválido: {mode}")
        previo = self.mode
        self.mode = mode
        if self._validador is not None and hasattr(
            self._validador, "emitir_side_effects"
        ):
            self._validador.emitir_side_effects = mode == "execution"
            if hasattr(self._validador, "mode"):
                self._validador.mode = mode
        return previo

    @property
    def variables(self) -> Any:
        """Devuelve el mapeo local del entorno activo (compatibilidad)."""
        return self.contextos[-1].values

    def reset_context_values(self, mapping: Mapping[str, object]) -> None:
        """Reemplaza de forma controlada los valores del contexto activo.

        Se copia explícitamente ``mapping`` para evitar aliasing accidental
        de diccionarios externos y se valida cada entrada antes de aplicarla.
        """
        if not isinstance(mapping, Mapping):
            raise TypeError("mapping debe implementar Mapping[str, object]")

        nuevos_valores: dict[str, object] = {}
        for clave, valor in mapping.items():
            if not isinstance(clave, str):
                raise TypeError("Las claves del contexto deben ser str")
            self._verificar_valor_contexto(valor)
            nuevos_valores[clave] = valor

        contexto_activo = self.contextos[-1]
        contexto_activo.values.clear()
        contexto_activo.values.update(nuevos_valores)

    def _indice_entorno_variable(self, nombre: str) -> int | None:
        """Retorna el índice del primer entorno (de adentro hacia afuera) con ``nombre``."""
        for indice in range(len(self.contextos) - 1, -1, -1):
            if nombre in self.contextos[indice].values:
                return indice
        return None

    def _entorno_funcion_activo(self) -> Environment | None:
        """Devuelve el entorno de la llamada activa, si existe."""
        for entorno in reversed(self.contextos):
            if entorno.is_function_scope:
                return entorno
        return None

    def _entorno_global(self) -> Environment:
        entorno = self.contextos[-1]
        while entorno.parent is not None:
            entorno = entorno.parent
        return entorno

    def _indice_contexto_entorno(self, entorno: Environment) -> int | None:
        for indice, candidato in enumerate(self.contextos):
            if candidato is entorno:
                return indice
        return None

    def _declarar_nolocal(self, nombre: str) -> None:
        entorno_funcion = self._entorno_funcion_activo()
        if entorno_funcion is None:
            raise SyntaxError("nolocal fuera de función")
        if nombre in entorno_funcion.local_names:
            raise SyntaxError(f"Nombre '{nombre}' declarado local y nolocal")
        if nombre in entorno_funcion.global_names:
            raise SyntaxError(f"Nombre '{nombre}' declarado global y nolocal")

        exterior = entorno_funcion.parent
        while exterior is not None and exterior.parent is not None:
            if exterior.is_function_scope and nombre in exterior.values:
                entorno_funcion.nonlocal_bindings[nombre] = exterior
                return
            exterior = exterior.parent
        raise SyntaxError(f"No existe binding nolocal para '{nombre}'")

    def _declarar_global(self, nombre: str) -> None:
        entorno_funcion = self._entorno_funcion_activo()
        if entorno_funcion is None:
            return
        if nombre in entorno_funcion.local_names:
            raise SyntaxError(f"Nombre '{nombre}' declarado local y global")
        if nombre in entorno_funcion.nonlocal_bindings:
            raise SyntaxError(f"Nombre '{nombre}' declarado nolocal y global")
        entorno_funcion.global_names.add(nombre)

    def _liberar_memoria_variable_en_contexto(
        self, nombre: str, indice_contexto: int
    ) -> None:
        """Libera el bloque de memoria asociado a ``nombre`` en un contexto concreto."""
        if indice_contexto < 0 or indice_contexto >= len(self.mem_contextos):
            return
        mem_ctx = self.mem_contextos[indice_contexto]
        if nombre not in mem_ctx:
            return
        idx, tam = mem_ctx.pop(nombre)
        self.liberar_memoria(idx, tam)

    def obtener_variable(self, nombre, visitados=None):
        """Busca una variable en la pila de contextos.

        Evita seguir referencias encadenadas para prevenir bucles
        innecesarios y devuelve el valor almacenado directamente.
        """
        return self._resolver_identificador(nombre, visitados)

    def _asignacion_referencia_identificador(
        self,
        expresion,
        nombre,
        visitados_ids: set[int] | None = None,
    ):
        """Detecta si una expresión contiene una referencia al identificador."""
        if visitados_ids is None:
            visitados_ids = set()
        if isinstance(expresion, NodoIdentificador):
            return expresion.nombre == nombre
        if isinstance(expresion, Token):
            return False
        if hasattr(expresion, "__dict__"):
            expresion_id = id(expresion)
            if expresion_id in visitados_ids:
                return False
            visitados_ids.add(expresion_id)
        for valor in getattr(expresion, "__dict__", {}).values():
            if isinstance(valor, list):
                for elem in valor:
                    if self._asignacion_referencia_identificador(
                        elem,
                        nombre,
                        visitados_ids,
                    ):
                        return True
            elif self._asignacion_referencia_identificador(
                valor,
                nombre,
                visitados_ids,
            ):
                return True
        return False

    def _validar_asignacion_autorreferente(self, nombre, valor):
        """Valida que una variable no apunte a una asignación autorreferente."""
        if not isinstance(valor, NodoAsignacion):
            return
        expresion = getattr(valor, "expresion", getattr(valor, "valor", None))
        if self._asignacion_referencia_identificador(expresion, nombre):
            raise RuntimeError(f"Ciclo de variables detectado en '{nombre}'")

    def _resolver_identificador(self, nombre, visitados=None):
        """Resuelve un identificador usando el entorno léxico activo."""
        visitados = set() if visitados is None else visitados
        if nombre in visitados:
            raise RuntimeError(f"Ciclo de variables detectado en '{nombre}'")
        visitados.add(nombre)
        try:
            try:
                valor = self.contextos[-1].get(nombre)
            except NameError:
                if nombre in self._funciones_declaradas_valor:
                    return self._funciones_declaradas_valor[nombre]
                raise
            self._validar_asignacion_autorreferente(nombre, valor)
            valor_resuelto = self._materializar_valor(
                valor,
                visitados,
                origen="resolucion_variable",
                nombre_variable=nombre,
            )
            if isinstance(valor_resuelto, NodoAST):
                raise RuntimeError(
                    "Resolución inválida de variable: "
                    f"'{nombre}' quedó en nodo AST "
                    f"({type(valor_resuelto).__name__})"
                )
            # Persistimos siempre el valor ya materializado para consolidar
            # el contrato de contexto -> materialización.
            self.contextos[-1].set(nombre, valor_resuelto)
            return valor_resuelto
        finally:
            visitados.discard(nombre)

    def _verificar_valor_contexto(self, valor):
        """Valida que el contexto sólo guarde tipos simples o contenedores.

        Se detectan referencias circulares utilizando una pila iterativa para
        evitar recursión profunda.
        """

        permitidos = (int, float, bool, str, type(None))
        contenedores = (dict, list, tuple, set)
        if isinstance(valor, permitidos):
            return
        if not isinstance(valor, contenedores):
            raise TypeError(
                "Solo se permiten tipos primitivos o diccionarios en el contexto"
            )

        pila = [(valor, set())]
        while pila:
            actual, ancestros = pila.pop()
            if id(actual) in ancestros:
                raise RuntimeError("Referencia circular detectada en el contexto")
            nuevos_ancestros = ancestros | {id(actual)}

            if isinstance(actual, dict):
                elementos = actual.values()
            elif isinstance(actual, (list, tuple, set)):
                elementos = actual
            else:
                continue

            for elem in elementos:
                if isinstance(elem, permitidos):
                    continue
                if isinstance(elem, contenedores):
                    pila.append((elem, nuevos_ancestros))
                else:
                    continue

    def _construir_funcion(self, nodo):
        entorno = self.contextos[-1]
        return {
            "tipo": "funcion",
            "nombre": nodo.nombre,
            "parametros": list(nodo.parametros),
            "cuerpo": list(nodo.cuerpo),
            "scope_lexico": entorno,
            "entorno": entorno,
        }

    def _registrar_funciones_declaradas_como_valores(self, ast) -> None:
        """Registra funciones top-level para resolución por identificador.

        Las llamadas directas pueden sobrevivir gracias a la ruta de llamada o
        al inlining, pero cuando una función aparece como expresión
        (``f = doble`` o ``filtrar(xs, predicado)``), el identificador debe
        poder resolverse incluso si ``inline_functions`` eliminó el
        ``NodoFuncion`` original del AST ejecutable. Esta tabla actúa como
        fallback de solo funciones; las variables/imports del entorno activo
        mantienen prioridad.
        """
        if not isinstance(ast, list):
            return
        for nodo in ast:
            if isinstance(nodo, NodoFuncion):
                self._funciones_declaradas_valor[nodo.nombre] = self._construir_funcion(
                    nodo
                )

    def _construir_clase(self, nodo, bases):
        return {
            "tipo": "clase",
            "nombre": nodo.nombre,
            "bases": bases,
            "metodos": [self._construir_funcion(m) for m in nodo.metodos],
        }

    def _materializar_valor(
        self,
        valor,
        visitados=None,
        origen="general",
        *,
        nombre_variable=None,
        operando=None,
    ):
        """Convierte nodos/valores a un valor inmediato y materializado.

        Contrato:
        - si el valor es resoluble, devuelve un valor utilizable por capas
          superiores (primitivos, contenedores normalizados o entidades runtime);
        - nunca debe permitir que se propague un ``NodoAST`` residual;
        - en ``origen='resolucion_variable'`` preserva el flujo
          ``contexto -> materialización -> persistencia`` para mantener el
          contexto con valores ya materializados.
        """
        visitados = set() if visitados is None else visitados
        primitivos = (int, float, bool, str, type(None), Environment)
        contenedores = (list, tuple, dict, set)

        def _normalizar_contenedor(contenedor):
            if isinstance(contenedor, list):
                return [
                    self._materializar_valor(
                        elem,
                        visitados,
                        origen,
                        nombre_variable=nombre_variable,
                        operando=operando,
                    )
                    for elem in contenedor
                ]
            if isinstance(contenedor, tuple):
                return tuple(
                    self._materializar_valor(
                        elem,
                        visitados,
                        origen,
                        nombre_variable=nombre_variable,
                        operando=operando,
                    )
                    for elem in contenedor
                )
            if isinstance(contenedor, set):
                return {
                    self._materializar_valor(
                        elem,
                        visitados,
                        origen,
                        nombre_variable=nombre_variable,
                        operando=operando,
                    )
                    for elem in contenedor
                }
            if isinstance(contenedor, dict):
                return {
                    clave: self._materializar_valor(
                        elem,
                        visitados,
                        origen,
                        nombre_variable=nombre_variable,
                        operando=operando,
                    )
                    for clave, elem in contenedor.items()
                }
            return contenedor

        actual = valor
        guardia = 0
        limite_guardia = 128

        while True:
            guardia += 1
            if gua…13783 tokens truncated…      return result
                elif tipo == TipoToken.O:
                    verificar_booleanos(left, right, "||")
                    result = left or right
                    self._trace_debug(
                        f"[BIN-RESULT] value={result} type={type(result).__name__}"
                    )
                    return result
                else:
                    raise ValueError(f"Operador no soportado: {tipo}")
            elif isinstance(expresion, NodoOperacionUnaria):
                valor = self.evaluar_expresion(expresion.operando, visitados)
                valor = self._materializar_valor(valor, visitados)
                self._asegurar_resultado_no_ast(
                    valor,
                    nodo_origen=expresion.operando,
                    operador=f"{expresion.operador.tipo}:operando",
                )
                tipo = expresion.operador.tipo
                if tipo == TipoToken.NO:
                    verificar_booleano(valor, "!")
                    return _retorno_critico(not valor, operador=tipo)
                else:
                    raise ValueError(f"Operador unario no soportado: {tipo}")
            elif isinstance(expresion, NodoEsperar):
                return self.evaluar_expresion(expresion.expresion, visitados)
            elif isinstance(expresion, NodoLlamadaMetodo):
                return _retorno_critico(
                    self.ejecutar_llamada_metodo(expresion),
                    operador="llamada_metodo",
                )
            elif isinstance(expresion, NodoLlamadaFuncion):
                return _retorno_critico(
                    self.ejecutar_llamada_funcion(expresion),
                    operador="llamada_funcion",
                )
            else:
                tipo_expresion = type(expresion).__name__
                expresion_id_seguro = id(expresion)
                raise ValueError(
                    f"Expresión no soportada: tipo={tipo_expresion} id={expresion_id_seguro}"
                )
        finally:
            # Siempre limpiar la traza de evaluación, incluso ante errores
            # semánticos o excepciones en ramas internas, para evitar
            # falsos positivos en evaluaciones posteriores.
            self._eval_stack.discard(expresion_key)

    def _evaluar_condicion_control(self, condicion):
        """Evalúa una condición y exige que quede materializada.

        Una condición no debe propagarse como ``NodoAST`` sin resolver para
        evitar comparaciones ambiguas entre nodos y errores opacos aguas abajo.

        Contrato de control de flujo:
        - la condición se evalúa usando ``evaluar_expresion``;
        - si aparece un identificador indefinido, ``NameError`` se propaga;
        - el resultado debe quedar materializado y ser estrictamente booleano
          antes de ejecutar cualquier bloque ``si/sino`` o ``mientras``.
        """
        condicion_resuelta = self.evaluar_expresion(condicion)
        if isinstance(condicion_resuelta, NodoAST):
            raise RuntimeError(
                "Condición no materializada: "
                f"se recibió nodo AST {type(condicion_resuelta).__name__}"
            )
        # No se permite coerción implícita (bool(x)); la condición debe ser
        # un booleano real para evitar ambigüedad semántica en control de flujo.
        if not isinstance(condicion_resuelta, bool):
            raise CondicionNoBooleanaError()
        return condicion_resuelta

    def ejecutar_condicional(self, nodo):
        """Ejecuta un bloque condicional."""
        # Contrato explícito del runtime:
        # "control-flow no abre scope; function-call sí abre scope".
        # Regla semántica de scope:
        # ``si/sino`` NO crea un entorno nuevo. Las instrucciones de cada rama
        # se ejecutan sobre ``self.contextos[-1]`` (contexto activo), por lo que
        # cualquier asignación queda visible al salir del condicional.
        # Nota: no se captura ``NameError`` ni otras excepciones aquí para no
        # ocultar la causa real del fallo en la evaluación de la condición.
        bloque_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", NodoBloque()))
        bloque_sino = getattr(
            nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", NodoBloque())
        )
        condicion = self._evaluar_condicion_control(nodo.condicion)

        if condicion is True:
            for instruccion in bloque_si:
                self.ejecutar_nodo(instruccion)
            return None

        # Única ruta restante válida: ``False``.
        if bloque_sino is None:
            return None
        for instruccion in bloque_sino:
            self.ejecutar_nodo(instruccion)
        return None

    def ejecutar_mientras(self, nodo):
        """Ejecuta un bucle ``mientras`` hasta que la condición sea falsa."""
        # Regla semántica de scope:
        # ``mientras`` NO abre un ámbito nuevo por iteración. El cuerpo del
        # bucle reutiliza ``self.contextos[-1]`` en cada vuelta y, por tanto,
        # las mutaciones del contexto persisten entre iteraciones y después.
        while self._evaluar_condicion_control(nodo.condicion):
            try:
                for instruccion in nodo.cuerpo:
                    self.ejecutar_nodo(instruccion)
            except _ControlContinuar:
                continue
            except _ControlRomper:
                break
        return None

    def ejecutar_para(self, nodo):
        """Ejecuta un bucle ``para`` sobre un iterable."""
        iterable = self.evaluar_expresion(nodo.iterable)
        iterable = self._materializar_valor(
            iterable,
            origen="bucle_para",
        )

        try:
            iterador = iter(iterable)
        except TypeError as exc:
            raise TypeError(
                "El iterable de 'para' no es recorrible: " f"{type(iterable).__name__}"
            ) from exc

        for valor in iterador:
            declaracion = not self.contextos[-1].contains(nodo.variable)

            self.ejecutar_asignacion(
                NodoAsignacion(
                    nodo.variable,
                    NodoValor(valor),
                    declaracion=declaracion,
                )
            )

            try:
                for instruccion in nodo.cuerpo:
                    self.ejecutar_nodo(instruccion)
            except _ControlContinuar:
                continue
            except _ControlRomper:
                break

        return None

    def ejecutar_try_catch(self, nodo):
        """Ejecuta un bloque ``try`` con manejo de excepciones Cobra."""
        try:
            for instruccion in nodo.bloque_try:
                self.ejecutar_nodo(instruccion)
        except ExcepcionCobra as exc:
            if nodo.nombre_excepcion is None:
                raise
            if nodo.nombre_excepcion:
                contexto_actual = self.contextos[-1]
                if contexto_actual.contains(nodo.nombre_excepcion):
                    contexto_actual.set(nodo.nombre_excepcion, exc.valor)
                else:
                    contexto_actual.define(nodo.nombre_excepcion, exc.valor)
            for instruccion in nodo.bloque_catch:
                self.ejecutar_nodo(instruccion)
        finally:
            for instruccion in nodo.bloque_finally:
                self.ejecutar_nodo(instruccion)

    def ejecutar_funcion(self, nodo):
        """Registra una función definida por el usuario sin ejecutarla.

        Contrato de ejecución:
        - Solo construye el descriptor de función y lo guarda con ``define`` en
          el entorno actual.
        - No evalúa parámetros por defecto dinámicos (si existieran) durante la
          definición.
        - No ejecuta ni recorre ``nodo.cuerpo`` en esta fase; el cuerpo se
          procesa únicamente al invocar la función.
        """
        funcion = self._construir_funcion(nodo)
        self._verificar_valor_contexto(funcion)
        self.contextos[-1].define(nodo.nombre, funcion)
        return None

    @staticmethod
    def _es_descriptor_funcion_cobra(valor):
        """Indica si ``valor`` es un descriptor runtime de función Cobra."""
        return isinstance(valor, dict) and valor.get("tipo") == "funcion"

    def _ejecutar_descriptor_funcion_cobra(self, funcion, argumentos):
        """Ejecuta un descriptor de función Cobra con argumentos ya resueltos."""
        parametros = funcion.get("parametros", funcion.get("params", []))
        cuerpo = funcion.get("cuerpo", funcion.get("body", []))

        if len(parametros) != len(argumentos):
            raise TypeError(f"se esperaban {len(parametros)} argumentos")

        entorno_capturado = funcion.get(
            "scope_lexico", funcion.get("entorno", self.contextos[-1])
        )
        if self._thread_isolation_depth:
            entorno_capturado = Environment(
                values=dict(entorno_capturado.values),
                parent=entorno_capturado.parent,
            )
        self.contextos.append(
            Environment(parent=entorno_capturado, is_function_scope=True)
        )
        self.mem_contextos.append({})
        try:
            for nombre_param, valor in zip(parametros, argumentos):
                indice = self.solicitar_memoria(1)
                self.mem_contextos[-1][nombre_param] = (indice, 1)
                self.contextos[-1].define(nombre_param, valor)
                self.contextos[-1].local_names.add(nombre_param)

            self._call_depth += 1
            try:
                for instruccion in cuerpo:
                    self.ejecutar_nodo(instruccion)
                return None
            except _ControlRetorno as retorno:
                return retorno.valor
            finally:
                self._call_depth -= 1
        finally:
            memoria_local = self.mem_contextos.pop()
            for idx, tam in memoria_local.values():
                self.liberar_memoria(idx, tam)
            self.contextos.pop()

    def _adaptar_callback_cobra(self, funcion):
        """Convierte un descriptor de función Cobra en un callback Python mínimo."""

        def callback(*argumentos):
            return self._ejecutar_descriptor_funcion_cobra(funcion, list(argumentos))

        nombre = funcion.get("nombre")
        if nombre:
            callback.__name__ = str(nombre)
        return callback

    def ejecutar_llamada_funcion(self, nodo):
        """Ejecuta la invocación de una función, interna o del usuario."""
        emitir_salida_llamada = self.in_execution()
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("Llamada a función: %s", nodo.nombre)
        if nodo.nombre == "imprimir":
            for arg in nodo.argumentos:
                if isinstance(arg, Token) and arg.tipo == TipoToken.IDENTIFICADOR:
                    arg = NodoIdentificador(arg.valor)
                valor = self.evaluar_expresion(arg)
                if valor is True:
                    valor = "verdadero"
                elif valor is False:
                    valor = "falso"
                if emitir_salida_llamada:
                    print(valor)
        else:
            try:
                funcion = self.obtener_variable(nodo.nombre)
            except NameError:
                if nodo.nombre not in self.funciones_nativas:
                    raise
                funcion = self.funciones_nativas[nodo.nombre]

            if callable(funcion):
                argumentos_resueltos = []
                for arg in nodo.argumentos:
                    valor = self.evaluar_expresion(arg)
                    self._verificar_valor_contexto(valor)
                    if self._es_descriptor_funcion_cobra(valor):
                        valor = self._adaptar_callback_cobra(valor)
                    argumentos_resueltos.append(valor)

                try:
                    resultado = funcion(*argumentos_resueltos)
                except (TypeError, IndexError) as exc:
                    raise self._normalizar_error_publico_usar(nodo.nombre, exc) from exc
                self._verificar_valor_contexto(resultado)
                return resultado

            if not self._es_descriptor_funcion_cobra(funcion):
                if emitir_salida_llamada:
                    print(f"Funci\u00f3n '{nodo.nombre}' no implementada")
                return None

            parametros = funcion.get("parametros", funcion.get("params", []))
            if len(parametros) != len(nodo.argumentos):
                if emitir_salida_llamada:
                    print(f"Error: se esperaban {len(parametros)} argumentos")
                return None

            cuerpo = funcion.get("cuerpo", funcion.get("body", []))
            contiene_yield = any(self._contiene_yield(instr) for instr in cuerpo)

            def preparar_contexto():
                # Los argumentos se evalúan en el contexto llamador antes de
                # abrir el nuevo scope local de la función.
                argumentos_resueltos = []
                for arg in nodo.argumentos:
                    valor = self.evaluar_expresion(arg)
                    self._verificar_valor_contexto(valor)
                    argumentos_resueltos.append(valor)

                # Regla semántica opuesta al control de flujo: cada llamada de
                # función sí encapsula su scope creando un nuevo contexto local.
                entorno_capturado = funcion.get(
                    "scope_lexico", funcion.get("entorno", self.contextos[-1])
                )
                if self._thread_isolation_depth:
                    entorno_capturado = Environment(
                        values=dict(entorno_capturado.values),
                        parent=entorno_capturado.parent,
                    )
                self.contextos.append(
                    Environment(parent=entorno_capturado, is_function_scope=True)
                )
                self.mem_contextos.append({})
                for nombre_param, valor in zip(parametros, argumentos_resueltos):
                    indice = self.solicitar_memoria(1)
                    self.mem_contextos[-1][nombre_param] = (indice, 1)
                    self.contextos[-1].define(nombre_param, valor)
                    self.contextos[-1].local_names.add(nombre_param)

            def limpiar_contexto():
                # Se restaura el scope anterior al finalizar la llamada.
                memoria_local = self.mem_contextos.pop()
                for idx, tam in memoria_local.values():
                    self.liberar_memoria(idx, tam)
                self.contextos.pop()

            if contiene_yield:

                def generador():
                    preparar_contexto()
                    self._call_depth += 1
                    try:
                        try:
                            for instr in cuerpo:
                                if isinstance(instr, NodoYield):
                                    yield self.evaluar_expresion(instr.expresion)
                                else:
                                    self.ejecutar_nodo(instr)
                        except _ControlRetorno as retorno:
                            return retorno.valor
                    finally:
                        self._call_depth -= 1
                        limpiar_contexto()

                return generador()
            else:
                preparar_contexto()
                try:
                    self._call_depth += 1
                    try:
                        for instruccion in cuerpo:
                            self.ejecutar_nodo(instruccion)
                        return None
                    except _ControlRetorno as retorno:
                        return retorno.valor
                    finally:
                        self._call_depth -= 1
                finally:
                    limpiar_contexto()

    def _normalizar_error_publico_usar(self, nombre: str, exc: Exception) -> Exception:
        """Normaliza errores contractuales de APIs públicas `usar`.

        Captura únicamente errores esperados para evitar ocultar fallas reales.
        """
        metadata = self._usar_symbol_metadata.get(nombre) or {}
        if metadata.get("module") == "datos" and metadata.get("symbol") == "elemento":
            mensaje = str(exc).strip()
            mensajes_permitidos = _ERRORES_USUARIO_ELEMENTO.get(type(exc), set())
            if mensaje in mensajes_permitidos:
                return type(exc)(f"Error: {mensaje}")
        return exc

    def ejecutar_clase(self, nodo):
        """Registra una clase definida por el usuario."""
        bases_resueltas = []
        for base_nombre in nodo.bases:
            base = self.obtener_variable(base_nombre)
            if not isinstance(base, dict) or base.get("tipo") != "clase":
                raise ValueError(f"Clase base '{base_nombre}' no definida")
            bases_resueltas.append(base)
        clase = self._construir_clase(nodo, bases_resueltas)
        self._verificar_valor_contexto(clase)
        self.contextos[-1].define(nodo.nombre, clase)

    def ejecutar_instancia(self, nodo):
        """Crea una instancia de la clase indicada."""
        clase = self.obtener_variable(nodo.nombre_clase)
        if not isinstance(clase, dict) or clase.get("tipo") != "clase":
            raise ValueError(f"Clase '{nodo.nombre_clase}' no definida")
        constructores = [
            metodo
            for metodo in clase.get("metodos", [])
            if metodo.get("nombre") in {"inicializar", "__init__"}
        ]
        if len(constructores) > 1:
            raise TypeError(
                f"Clase '{nodo.nombre_clase}' tiene varios constructores propios"
            )
        constructor = constructores[0] if constructores else None
        argumentos = []
        if constructor is None:
            if nodo.argumentos:
                raise TypeError(
                    f"Clase '{nodo.nombre_clase}' sin constructor propio "
                    "no acepta argumentos"
                )
        else:
            parametros = constructor.get("parametros", [])
            if not parametros or parametros[0] not in {"este", "self"}:
                raise TypeError("El constructor requiere un receptor 'este' o 'self'")
            esperados = len(parametros) - 1
            if len(nodo.argumentos) != esperados:
                raise TypeError(
                    f"Constructor de '{nodo.nombre_clase}': "
                    f"se esperaban {esperados} argumentos"
                )
            for argumento in nodo.argumentos:
                valor = self.evaluar_expresion(argumento)
                self._verificar_valor_contexto(valor)
                argumentos.append(valor)
        bases = clase.get("bases", [])
        instancia = {"__clase__": clase, "__bases__": bases, "__atributos__": {}}
        self._verificar_valor_contexto(instancia)
        if constructor is not None:
            self._ejecutar_descriptor_funcion_cobra(
                constructor, [instancia, *argumentos]
            )
        return instancia

    def ejecutar_llamada_metodo(self, nodo):
        """Invoca un método de un objeto instanciado."""
        objeto = self.evaluar_expresion(nodo.objeto)
        if not isinstance(objeto, dict) or "__clase__" not in objeto:
            raise ValueError("Objeto inv\u00e1lido en llamada a m\u00e9todo")
        clase = objeto["__clase__"]

        def buscar_metodo(clase_actual):
            metodos = clase_actual.get("metodos", [])
            metodo = next(
                (m for m in metodos if m.get("nombre") == nodo.nombre_metodo),
                None,
            )
            if metodo is not None:
                return metodo
            for base in clase_actual.get("bases", []):
                encontrado = buscar_metodo(base)
                if encontrado is not None:
                    return encontrado
            return None

        metodo = buscar_metodo(clase)
        if metodo is None:
            raise ValueError(f"Método '{nodo.nombre_metodo}' no encontrado")

        parametros = metodo.get("parametros", [])
        if not parametros or parametros[0] not in {"este", "self"}:
            raise TypeError(
                f"Método '{nodo.nombre_metodo}' requiere un receptor 'este' o 'self'"
            )
        esperados = len(parametros) - 1
        if len(nodo.argumentos) != esperados:
            raise TypeError(
                f"Método '{nodo.nombre_metodo}': se esperaban {esperados} argumentos"
            )
        argumentos = []
        for argumento in nodo.argumentos:
            valor = self.evaluar_expresion(argumento)
            self._verificar_valor_contexto(valor)
            argumentos.append(valor)

        entorno_capturado = metodo.get("entorno", self.contextos[-1])
        self.contextos.append(
            Environment(parent=entorno_capturado, is_function_scope=True)
        )
        self.mem_contextos.append({})
        receptor = parametros[0]
        self.contextos[-1].define(receptor, objeto)
        self.contextos[-1].local_names.add(receptor)
        for nombre_param, valor in zip(parametros[1:], argumentos):
            self.contextos[-1].define(nombre_param, valor)
            self.contextos[-1].local_names.add(nombre_param)

        try:
            self._call_depth += 1
            try:
                for instruccion in metodo.get("cuerpo", []):
                    self.ejecutar_nodo(instruccion)
                return None
            except _ControlRetorno as retorno:
                return retorno.valor
            finally:
                self._call_depth -= 1
        finally:
            memoria_local = self.mem_contextos.pop()
            for idx, tam in memoria_local.values():
                self.liberar_memoria(idx, tam)
            self.contextos.pop()

    def ejecutar_import(self, nodo: NodoImport) -> None:
        """Ejecuta una declaración de importación de módulo legacy.

        ``NodoImport`` mantiene la semántica histórica de ``import``: carga el
        AST del archivo con ``cargar_ast_modulo`` y ejecuta todos sus nodos en el
        contexto actual. La caché de AST sólo evita parseos repetidos; no debe
        delegar en ``usar_modulo`` ni aplicar la semántica pública/exportada de
        ``usar``.
        """
        ruta = Path(nodo.ruta).expanduser()
        ruta_import_legacy = str(ruta)
        if not ruta.is_absolute():
            base = (
                self._current_module_stack[-1].parent
                if self._current_module_stack
                else (
                    self._main_file.parent
                    if self._main_file is not None
                    else Path.cwd()
                )
            )
            ruta = base / ruta

        ruta_canonica = ruta.resolve(strict=False)
        ast_cache = self._import_ast_cache

        if ruta_canonica in self._imported_module_paths:
            return

        if ruta_canonica in self._import_execution_stack:
            inicio_ciclo = self._import_execution_stack.index(ruta_canonica)
            ciclo = self._import_execution_stack[inicio_ciclo:] + [ruta_canonica]
            nombres = " -> ".join(ruta.name for ruta in ciclo)
            raise ImportError(f"Ciclo de módulos detectado en import: {nombres}")

        if ruta_canonica in ast_cache:
            ast = ast_cache[ruta_canonica]
        else:
            # Pasar la pila de carga del intérprete a cargar_ast_modulo
            ruta_para_loader = (
                str(ruta_canonica)
                if getattr(cargar_ast_modulo, "__module__", "")
                == "pcobra.core.import_utils"
                else ruta_import_legacy
            )
            ast = cargar_ast_modulo(
                ruta_para_loader,
                modules_path=str(MODULES_PATH),
                whitelist={MODULES_PATH, self._project_root, *IMPORT_WHITELIST},
                loading_stack=self._usar_loading_stack,
            )
            ast_cache[ruta_canonica] = ast

        self._import_execution_stack.append(ruta_canonica)
        self._current_module_stack.append(ruta_canonica)
        try:
            for subnodo in ast:
                modo_previo = self._set_mode("analysis")
                try:
                    self._validar(subnodo)
                    self._set_mode("execution")
                    self.ejecutar_nodo(subnodo)
                finally:
                    self._set_mode(modo_previo)
        finally:
            self._current_module_stack.pop()
            self._import_execution_stack.pop()
        self._imported_module_paths.add(ruta_canonica)

    def _ejecutar_usar_modulo_proyecto(self, nombre_modulo: str) -> None:
        """Compatibilidad interna: delega directamente en ``usar_modulo``.

        La resolución, caché y detección de ciclos de módulos Cobra de proyecto
        pertenecen exclusivamente a :func:`pcobra.cobra.usar_loader.usar_modulo`.
        Este método se conserva sólo para callers internos legacy y no debe
        reimplementar un segundo sistema de imports.
        """

        current_file = (
            self._current_module_stack[-1]
            if self._current_module_stack
            else self._main_file
        )
        exports = _usar_modulo_con_estado_aislado(
            nombre_modulo,
            project_root=self._project_root,
            current_file=current_file,
            module_cache=self._usar_module_cache,
            loading_stack=self._usar_loading_stack,
            contexto_proyecto_verificado=self._contexto_proyecto_verificado,
            safe_mode=self.safe_mode,
        )
        self._inyectar_exports_modulo_proyecto(exports)

    def _inyectar_exports_modulo_proyecto(self, exports: Mapping[str, object]) -> None:
        """Inyecta en el contexto activo los exports cacheados de un módulo de proyecto."""

        simbolos_saneados = list(exports.get("simbolos", []))
        metadata_por_simbolo = {
            nombre: dict(metadata)
            for nombre, metadata in dict(exports.get("metadata", {})).items()
        }
        conflictos = self._detectar_conflictos_usar_en_contexto(
            simbolos_saneados,
            metadata_por_simbolo=metadata_por_simbolo,
        )
        if conflictos:
            simbolo = conflictos[0]
            modulo = str(
                metadata_por_simbolo.get(simbolo, {}).get("module", "módulo Cobra")
            )
            detalle = {
                "code": "symbol_collision",
                "message": "símbolo ya existe en contexto actual",
                "symbol": simbolo,
                "module": modulo,
                "phase": "preflight",
            }

            if self._usar_collision_policy == USAR_COLLISION_WARN_ALIAS_REQUIRED:
                warnings.warn(
                    "Conflicto de nombres en `usar`: "
                    f"el símbolo '{simbolo}' ya existe y no será sobrescrito.",
                    RuntimeWarning,
                    stacklevel=2,
                )

            raise NameError(
                f"No se puede usar '{modulo}': "
                "hay conflicto de símbolos en el contexto actual. "
                f"Símbolo conflictivo: {simbolo}. "
                f"No se puede usar el módulo '{modulo}': "
                f"colisión estructurada={detalle}"
            )
        self._inyectar_simbolos_usar_en_contexto(
            simbolos_saneados,
            metadata_por_simbolo=metadata_por_simbolo,
        )

    def ejecutar_usar(self, nodo):
        """Importa símbolos públicos usando ``usar_modulo`` como fuente única.

        ``usar_modulo`` concentra la resolución de módulos oficiales y de
        proyecto, así como la caché y la pila de ciclos. El intérprete sólo
        adapta el contexto de llamada e inyecta atómicamente los exports
        devueltos mediante ``_inyectar_exports_modulo_proyecto``.
        """

        try:
            nombre_modulo_limpio = str(nodo.modulo).strip().strip("\"'")
            current_file = (
                self._current_module_stack[-1]
                if self._current_module_stack
                else self._main_file
            )
            exports = _usar_modulo_con_estado_aislado(
                nombre_modulo_limpio,
                project_root=self._project_root,
                current_file=current_file,
                module_cache=self._usar_module_cache,
                loading_stack=self._usar_loading_stack,
                contexto_proyecto_verificado=self._contexto_proyecto_verificado,
                safe_mode=self.safe_mode,
            )
            self._inyectar_exports_modulo_proyecto(exports)
        except Exception as exc:
            detalle_usar_habilitado = _usar_detalle_habilitado()
            exc_usuario: Exception
            if isinstance(exc, ModuloFueraCatalogoPublicoError):
                exc_usuario = _error_usuario_modulo_fuera_catalogo(
                    nombre_modulo_limpio,
                    exc,
                    repl_estricto=self._repl_usar_alias_map is not None,
                    incluir_detalle=detalle_usar_habilitado,
                )
            elif isinstance(exc, ValueError):
                mensaje = str(exc)
                if "Nombre de módulo inválido en 'usar':" in mensaje:
                    exc_usuario = ValueError(mensaje)
                else:
                    # Los rechazos de política continúan exponiendo el contrato
                    # público estable, sin filtrar detalles internos.
                    exc_usuario = PermissionError(USAR_DIRECT_BACKEND_IMPORT_ERROR)
                    exc_usuario.add_note(mensaje)
            elif isinstance(exc, FileNotFoundError):
                exc_usuario = FileNotFoundError(
                    formatear_error_usar_usuario(
                        "modulo_no_encontrado", nombre_modulo_limpio
                    )
                )
                exc_usuario.add_note(str(exc))
            elif isinstance(exc, NameError):
                mensaje = str(exc)
                marcador_colision = "colisión estructurada="
                colision_estructurada = False
                if marcador_colision in mensaje:
                    payload = mensaje.split(marcador_colision, 1)[1].strip()
                    try:
                        detalle_colision = ast.literal_eval(payload)
                    except (ValueError, SyntaxError):
                        detalle_colision = None
                    colision_estructurada = isinstance(
                        detalle_colision, dict
                    ) and detalle_colision.get("code") in {
                        "symbol_collision",
                        "symbol_collision_runtime_recheck",
                    }

                if colision_estructurada:
                    # El detalle estructurado permanece en la causa interna;
                    # la frontera pública expone el diagnóstico estable de `usar`.
                    exc_usuario = NameError(
                        formatear_error_usar_usuario(
                            "conflicto_simbolo", nombre_modulo_limpio
                        )
                    )

                else:
                    exc_usuario = NameError(
                        formatear_error_usar_usuario(
                            "conflicto_simbolo", nombre_modulo_limpio
                        )
                    )
            elif isinstance(exc, (ImportError, PermissionError)):
                mensaje = str(exc)

                if (
                    isinstance(exc, ImportError)
                    and "Ciclo de módulos detectado en usar:" in mensaje
                ):
                    exc_usuario = ImportError(mensaje)
                elif "usar_error[" in mensaje:
                    exc_usuario = type(exc)(mensaje)
                else:
                    exc_usuario = type(exc)(
                        formatear_error_usar_usuario(
                            "carga_modulo_error", nombre_modulo_limpio
                        )
                    )
                    exc_usuario.add_note(mensaje)
            else:
                exc_usuario = ImportError(
                    formatear_error_usar_usuario(
                        "carga_modulo_error", nombre_modulo_limpio
                    )
                )
                exc_usuario.add_note(str(exc))
            if detalle_usar_habilitado:
                logging.exception(
                    "Error al usar el módulo '%s': %s", nodo.modulo, exc_usuario
                )
            else:
                logging.debug(
                    "Error esperado al usar módulo %s: %s",
                    nodo.modulo,
                    exc_usuario,
                )
            raise exc_usuario from exc

    def _detectar_conflictos_usar_en_contexto(
        self,
        simbolos_saneados: list[tuple[str, object]],
        *,
        metadata_por_simbolo: Mapping[str, dict[str, object]],
    ) -> list[str]:
        """Devuelve símbolos en conflicto real (ignora reimport idempotente por metadatos)."""
        contexto_actual = self.contextos[-1]
        conflictos: list[str] = []
        for nombre, simbolo in simbolos_saneados:
            if not contexto_actual.contains(nombre):
                continue
            previo = self._usar_symbol_metadata.get(nombre)
            metadata_actual = metadata_por_simbolo.get(nombre)
            if metadata_actual is None:
                continue
            if self._metadata_usar_equivalente_idempotente(previo, metadata_actual):
                # Reimport idempotente: mismo símbolo, mismo módulo origen y misma identidad.
                continue
            conflictos.append(nombre)
        if conflictos:
            self._trace_debug(
                "[USAR_COLLISION][PREFLIGHT] "
                f"módulo={metadata_por_simbolo[conflictos[0]].get('module')} conflictos={','.join(conflictos)}"
            )
        return conflictos

    def _inyectar_simbolos_usar_en_contexto(
        self,
        simbolos_saneados: list[tuple[str, object]],
        *,
        metadata_por_simbolo: Mapping[str, dict[str, object]],
        permitir_sobrescritura: bool = False,
    ) -> None:
        """Inyecta símbolos saneados en el entorno activo centralizando el binding."""
        contexto_actual = self.contextos[-1]
        for nombre, simbolo in simbolos_saneados:
            if contexto_actual.contains(nombre) and not permitir_sobrescritura:
                previo = self._usar_symbol_metadata.get(nombre)
                metadata_actual = metadata_por_simbolo.get(nombre)
                if metadata_actual is None:
                    continue
                if self._metadata_usar_equivalente_idempotente(previo, metadata_actual):
                    # No-op idempotente: evita warning/ruido al reimportar lo mismo.
                    continue
                modulo = str(metadata_actual.get("module"))
                detalle = {
                    "module": modulo,
                    "symbol": nombre,
                    "code": "symbol_collision_runtime_recheck",
                    "message": "símbolo ya existe en contexto actual",
                    "policy": self._usar_collision_policy,
                    "phase": "runtime_recheck",
                }
                self._trace_debug(
                    "[USAR_COLLISION][ERROR] "
                    f"módulo={modulo} símbolo={nombre} code=symbol_collision_runtime_recheck"
                )
                raise NameError(
                    "No se puede usar el módulo "
                    f"'{metadata_actual.get('module')}': {USAR_SYMBOL_CONFLICT_ERROR} colisión estructurada={detalle}"
                )
            metadata_simbolo = metadata_por_simbolo.get(nombre)
            if metadata_simbolo is None:
                continue
            metadata_simbolo = self._canonicalizar_metadata_usar(
                nombre, metadata_simbolo
            )
            simbolo = self._materializar_valor(simbolo, visitados=None)
            contexto_actual.define(nombre, simbolo)
            self._usar_symbol_metadata[nombre] = dict(metadata_simbolo)
            if self._validador is not None and hasattr(
                self._validador, "registrar_simbolo_publico_usar"
            ):
                resumen = {
                    "module": metadata_simbolo.get("module"),
                    "symbol": metadata_simbolo.get("symbol"),
                    "callable": metadata_simbolo.get("callable"),
                    "public_api": metadata_simbolo.get("public_api"),
                    "sanitized": metadata_simbolo.get("sanitized"),
                }
                self._trace_debug(f"[USAR_METADATA][PRE_REGISTRO] {resumen}")
                self._validador.registrar_simbolo_publico_usar(
                    nombre,
                    str(metadata_simbolo["module"]),
                    metadata=dict(metadata_simbolo),
                )
                self._sincronizar_metadata_usar_no_destructiva()
                self._trace_debug(f"[USAR_METADATA][POST_REGISTRO] {resumen}")
                if (
                    str(metadata_simbolo.get("module")) == "archivo"
                    and nombre == "existe"
                ):
                    self._trace_debug(
                        "[USAR_TRACE][archivo.existe] confirmado wrapper sanitizado "
                        f"(public_api={metadata_simbolo.get('public_api')}, sanitized={metadata_simbolo.get('sanitized')})"
                    )
                self._asegurar_metadata_usar_sincronizada(etapa="post-registro")

    def ejecutar_holobit(self, nodo):
        """Simula la ejecución de un holobit y devuelve sus valores."""
        if self.in_execution():
            print(f"Simulando holobit: {nodo.nombre}")
        valores = []
        for v in nodo.valores:
            if isinstance(v, NodoValor):
                valores.append(v.valor)
            else:
                valores.append(v)
        return valores

    def ejecutar_hilo(self, nodo):
        """Ejecuta una función en un hilo separado."""

        def destino():
            # ``threading.local`` crea pilas limpias para este worker. No se
            # serializa la ejecución completa: solo las operaciones realmente
            # compartidas (p. ej. memoria) toman su bloqueo específico.
            self._thread_isolation_depth += 1
            try:
                self.ejecutar_llamada_funcion(nodo.llamada)
            finally:
                self._thread_isolation_depth -= 1
                # Una excepción no debe dejar scopes ni temporales vivos en el
                # estado local si el Thread es retenido por instrumentación.
                self.contextos[:] = [self._global_environment]
                self.mem_contextos[:] = [self._global_mem_context]
                self._eval_stack.clear()
                self._call_depth = 0

        # El hilo se marca como daemon para evitar que bloquee el cierre del
        # intérprete si queda en ejecución al finalizar el programa.
        hilo = threading.Thread(target=destino, daemon=True)
        hilo.start()
        return hilo


# Protección de compatibilidad: algunos consumidores legacy sustituyen
# ``InterpretadorCobra`` en el módulo global durante inicialización de CLI.
# Evitamos que stubs incompletos contaminen imports posteriores del runtime.
import sys as _sys
from types import ModuleType as _ModuleType


class _InterpreterModule(_ModuleType):
    def __setattr__(self, name, value):
        if name == "InterpretadorCobra" and not hasattr(value, "ejecutar_asignacion"):
            return
        super().__setattr__(name, value)


_sys.modules[__name__].__class__ = _InterpreterModule
