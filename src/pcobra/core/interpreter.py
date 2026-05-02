"""Implementación del intérprete del lenguaje Cobra."""

import logging
import os
import hashlib
from typing import Mapping, Optional

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
from .semantico import AnalizadorSemantico
from .cobra_config import (
    limite_nodos,
    limite_memoria_mb,
    limite_cpu_segundos,
)
from .resource_limits import (
    limitar_memoria_mb as _lim_mem,
    limitar_cpu_segundos as _lim_cpu,
)
from .import_utils import (
    MODULES_PATH as _DEFAULT_MODULES_PATH,
    IMPORT_WHITELIST,
    ruta_import_permitida,
    cargar_ast_modulo,
)
from .utils import validar_ast_estructural, ErrorEstructuraAST
from .errors import CondicionNoBooleanaError
from .environment import Environment

MODULES_PATH = _DEFAULT_MODULES_PATH


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
        """Carga una lista de validadores desde un archivo Python."""
        import ast

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

        try:
            tree = ast.parse(source, filename=ruta_real)
        except SyntaxError as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "sintaxis_invalida",
                hash_corto=hash_corto,
                fase="parse",
            )
            raise ImportError(
                "El archivo de validadores tiene sintaxis inválida."
            ) from e

        magia_permitida = {"__name__"}
        tokens_sensibles = {
            "__subclasses__",
            "__globals__",
            "__dict__",
            "__mro__",
            "__bases__",
            "__getattribute__",
            "__setattr__",
            "__delattr__",
            "__code__",
            "__closure__",
            "__func__",
            "__self__",
        }
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                InterpretadorCobra._registrar_auditoria_validador(
                    ruta_real,
                    "rechazado",
                    "import_no_permitido",
                    hash_corto=hash_corto,
                    fase="policy_check",
                )
                raise ImportError(
                    "ImportError: no se permiten importaciones en validadores adicionales."
                )
            if isinstance(node, ast.Attribute):
                if (
                    node.attr.startswith("__")
                    and node.attr.endswith("__")
                    and node.attr not in magia_permitida
                ):
                    InterpretadorCobra._registrar_auditoria_validador(
                        ruta_real,
                        "rechazado",
                        "atributo_magico_no_permitido",
                        hash_corto=hash_corto,
                        fase="policy_check",
                    )
                    raise ImportError(
                        "ImportError: se detectó acceso a atributo mágico no permitido en el validador adicional."
                    )
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if any(token in node.value for token in tokens_sensibles):
                    InterpretadorCobra._registrar_auditoria_validador(
                        ruta_real,
                        "rechazado",
                        "cadena_introspeccion_sensible",
                        hash_corto=hash_corto,
                        fase="policy_check",
                    )
                    raise ImportError(
                        "ImportError: se detectó un patrón de introspección no permitido en el validador adicional."
                    )
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "__import__":
                    InterpretadorCobra._registrar_auditoria_validador(
                        ruta_real,
                        "rechazado",
                        "dunder_import_bloqueado",
                        hash_corto=hash_corto,
                        fase="policy_check",
                    )
                    raise ImportError(
                        "ImportError: el uso de __import__ está bloqueado en validadores adicionales."
                    )
                if isinstance(func, ast.Name) and func.id == "getattr":
                    primer_arg = node.args[0] if node.args else None
                    objetivo_sensible = isinstance(primer_arg, ast.Name) and primer_arg.id in {
                        "__builtins__",
                        "builtins",
                        "object",
                        "type",
                    }
                    atributo_sensible = (
                        len(node.args) > 1
                        and isinstance(node.args[1], ast.Constant)
                        and isinstance(node.args[1].value, str)
                        and any(token in node.args[1].value for token in tokens_sensibles)
                    )
                    if objetivo_sensible or atributo_sensible:
                        InterpretadorCobra._registrar_auditoria_validador(
                            ruta_real,
                            "rechazado",
                            "getattr_introspeccion_bloqueado",
                            hash_corto=hash_corto,
                            fase="policy_check",
                        )
                        raise ImportError(
                            "ImportError: uso de introspección dinámica no permitido en el validador adicional."
                        )

        from RestrictedPython import compile_restricted
        from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getattr
        from RestrictedPython.Guards import (
            guarded_iter_unpack_sequence,
            guarded_unpack_sequence,
        )
        from RestrictedPython.PrintCollector import PrintCollector

        import builtins

        safe_builtins = {
            "len": builtins.len,
            "range": builtins.range,
            "__build_class__": builtins.__build_class__,
            "Exception": builtins.Exception,
            "object": builtins.object,
        }
        from .semantic_validators.base import ValidadorBase

        namespace = {
            "__builtins__": safe_builtins,
            "ValidadorBase": ValidadorBase,
            "__name__": "validators",
            "__metaclass__": builtins.type,
            "_print_": PrintCollector,
            "_getattr_": default_guarded_getattr,
            "_getitem_": default_guarded_getitem,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
        }
        mem_limit = limite_memoria_mb()
        cpu_limit = limite_cpu_segundos()
        if mem_limit is not None:
            _lim_mem(int(mem_limit))
        if cpu_limit is not None:
            _lim_cpu(int(cpu_limit))

        try:
            byte_code = compile_restricted(source, ruta_abs, "exec")
        except TimeoutError as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "timeout",
                hash_corto=hash_corto,
                fase="compile",
            )
            raise ImportError(
                "El validador adicional superó el tiempo permitido."
            ) from e
        except (MemoryError, OverflowError) as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "memoria_excedida",
                hash_corto=hash_corto,
                fase="compile",
            )
            raise ImportError(
                "El validador adicional excede los límites de memoria permitidos."
            ) from e
        try:
            exec(byte_code, namespace)
        except TimeoutError as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "timeout",
                hash_corto=hash_corto,
                fase="exec",
            )
            raise ImportError(
                "El validador adicional superó el tiempo permitido."
            ) from e
        except (MemoryError, OverflowError) as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "memoria_excedida",
                hash_corto=hash_corto,
                fase="exec",
            )
            raise ImportError(
                "El validador adicional excede los límites de memoria permitidos."
            ) from e
        except Exception as e:
            InterpretadorCobra._registrar_auditoria_validador(
                ruta_real,
                "rechazado",
                "error_en_ejecucion",
                hash_corto=hash_corto,
                fase="exec",
            )
            raise ImportError(
                "No se pudo cargar el validador adicional de forma segura."
            ) from e
        InterpretadorCobra._registrar_auditoria_validador(
            ruta_real,
            "permitido",
            hash_corto=hash_corto,
            fase="exec",
        )
        return namespace.get("VALIDADORES_EXTRA", [])

    def __init__(self, safe_mode: bool = True, extra_validators=None):
        """Crea un nuevo interpretador.

        Parameters
        ----------
        safe_mode: bool, optional
            Indica si el intérprete debe ejecutarse en modo seguro. Está
            activado por defecto y valida cada nodo utilizando la cadena
            devuelta por :func:`construir_cadena`, restringiendo primitivas
            como ``import`` o ``hilo``.
        extra_validators: list | str, optional
            Lista de instancias adicionales o ruta a un módulo que defina
            ``VALIDADORES_EXTRA``.
        """
        extra = extra_validators
        if isinstance(extra, str):
            extra = self._cargar_validadores(extra)

        self.safe_mode = safe_mode
        # Regla de fases: analysis = sin efectos, execution = con efectos.
        # Por defecto iniciamos en ejecución para preservar compatibilidad fuera del REPL.
        self.mode = "execution"
        self._validador = (
            construir_cadena(extra, emitir_side_effects=True) if safe_mode else None
        )
        # Analizador semántico persistente para mantener contexto entre ejecuciones
        self.analizador = AnalizadorSemantico()
        # Conjunto para evitar validar el mismo nodo varias veces
        self._validados = set()
        # Pila de entornos para mantener variables locales en cada llamada
        self.contextos = [Environment()]
        # Mapa paralelo para gestionar bloques de memoria por contexto
        self.mem_contextos = [{}]
        # Gestor genético de estrategias de memoria
        self.gestor_memoria = GestorMemoriaGenetico()
        self.estrategia = self.gestor_memoria.poblacion[0]
        self.op_memoria = 0
        self._eval_stack = set()
        # Último IR generado a partir del AST ejecutado
        self.ultimo_ir: Optional[InternalIRModule] = None
        # Restricción opcional para `usar` en REPL/evaluador incremental.
        self._repl_usar_alias_map: dict[str, str] | None = None

    def configurar_restriccion_usar_repl(self, alias_map: dict[str, str] | None) -> None:
        """Configura whitelist explícita de módulos `usar` para flujo REPL.

        Cuando ``alias_map`` es ``None``, no se aplica restricción adicional.
        """
        self._repl_usar_alias_map = alias_map.copy() if alias_map is not None else None

    def in_execution(self) -> bool:
        """Indica si el intérprete se encuentra en fase de ejecución."""
        return self.mode == "execution"

    def _set_mode(self, mode: str) -> str:
        """Actualiza la fase del intérprete y retorna el modo previo."""
        if mode not in {"analysis", "execution"}:
            raise ValueError(f"Modo inválido: {mode}")
        previo = self.mode
        self.mode = mode
        if self._validador is not None and hasattr(self._validador, "emitir_side_effects"):
            self._validador.emitir_side_effects = mode == "execution"
            if hasattr(self._validador, "mode"):
                self._validador.mode = mode
        return previo

    @property
    def variables(self):
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

    def _liberar_memoria_variable_en_contexto(self, nombre: str, indice_contexto: int) -> None:
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
            valor = self.contextos[-1].get(nombre)
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
        return {
            "tipo": "funcion",
            "nombre": nodo.nombre,
            "parametros": list(nodo.parametros),
            "cuerpo": list(nodo.cuerpo),
            "scope_lexico": self.contextos[-1],
        }

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
            if guardia > limite_guardia:
                raise RuntimeError(
                    "No se pudo materializar el valor: límite de normalización excedido"
                )

            if isinstance(actual, primitivos):
                return actual

            if isinstance(actual, NodoValor):
                actual = actual.valor
                continue

            if isinstance(actual, Token) and actual.tipo in {
                TipoToken.ENTERO,
                TipoToken.FLOTANTE,
                TipoToken.CADENA,
                TipoToken.BOOLEANO,
            }:
                actual = actual.valor
                continue

            if isinstance(actual, dict) and (
                actual.get("tipo") in {"funcion", "clase", "instancia"}
                or "__clase__" in actual
            ):
                return actual

            if isinstance(actual, contenedores):
                actual = _normalizar_contenedor(actual)
                self._verificar_valor_contexto(actual)
                return actual

            if origen == "resolucion_variable":
                if isinstance(actual, NodoIdentificador):
                    actual = self._resolver_identificador(actual.nombre, visitados)
                    if isinstance(actual, NodoAST):
                        nombre_ref = getattr(actual, "nombre", "<desconocido>")
                        raise RuntimeError(
                            "Resolución inválida de variable durante materialización: "
                            f"variable '{nombre_variable or nombre_ref}', "
                            f"operando '{operando or 'valor'}', "
                            f"nodo {type(actual).__name__}"
                        )
                    continue
                if isinstance(actual, NodoAST):
                    raise RuntimeError(
                        "No se pudo materializar un nodo AST durante la resolución "
                        f"de variable '{nombre_variable or '<desconocida>'}' "
                        f"(operando: '{operando or 'valor'}', "
                        f"nodo: {type(actual).__name__})"
                    )

            elif origen == "operacion_binaria":
                if isinstance(actual, NodoIdentificador):
                    actual = self._resolver_identificador(actual.nombre, visitados)
                if isinstance(actual, NodoAST):
                    raise RuntimeError(
                        "No se pudo materializar el operando de operación binaria: "
                        f"nodo AST residual ({type(actual).__name__})"
                    )
                if actual is not valor:
                    continue

            else:
                expresiones_soportadas = (
                    NodoAsignacion,
                    NodoIdentificador,
                    NodoInstancia,
                    NodoAtributo,
                    NodoHolobit,
                    NodoEsperar,
                    NodoOperacionBinaria,
                    NodoOperacionUnaria,
                    NodoLlamadaMetodo,
                    NodoLlamadaFuncion,
                )
                if isinstance(actual, expresiones_soportadas):
                    actual = self.evaluar_expresion(actual, visitados)
                    continue

            if isinstance(actual, NodoAST):
                raise RuntimeError(
                    "No se pudo materializar el valor: "
                    f"nodo AST no resoluble ({type(actual).__name__})"
                )

            return actual

    # -- Gestión de memoria -------------------------------------------------
    def solicitar_memoria(self, tam):
        """Solicita un bloque a la estrategia actual."""
        index = self.estrategia.asignar(tam)
        if index == -1:
            self.gestor_memoria.evolucionar(verbose=False)
            self.estrategia = self.gestor_memoria.poblacion[0]
            index = self.estrategia.asignar(tam)
        self.op_memoria += 1
        if self.op_memoria >= 1000:
            self.gestor_memoria.evolucionar(verbose=False)
            self.estrategia = self.gestor_memoria.poblacion[0]
            self.op_memoria = 0
        return index

    def liberar_memoria(self, index, tam):
        """Libera un bloque de memoria."""
        self.estrategia.liberar(index, tam)

    # -- Utilidades ---------------------------------------------------------
    def _validar(self, nodo):
        """Valida un nodo en fase de análisis si el modo seguro está activo."""
        if self.mode != "analysis":
            return
        if self.safe_mode and id(nodo) not in self._validados:
            nodo.aceptar(self._validador)
            self._validados.add(id(nodo))

    def _auditar_en_ejecucion(self, nodo) -> None:
        """Ejecuta la auditoría funcional únicamente durante la fase de ejecución."""
        if not self.in_execution() or not self.safe_mode or self._validador is None:
            return
        # En ejecución permitimos side effects de auditoría visibles al usuario.
        nodo.aceptar(self._validador)

    def _contiene_yield(self, nodo, visitados_ids: set[int] | None = None):
        if visitados_ids is None:
            visitados_ids = set()
        if isinstance(nodo, NodoYield):
            return True
        if isinstance(nodo, Token):
            return False
        if not hasattr(nodo, "__dict__"):
            return False

        nodo_id = id(nodo)
        if nodo_id in visitados_ids:
            return False
        visitados_ids.add(nodo_id)

        for valor in getattr(nodo, "__dict__", {}).values():
            if isinstance(valor, list):
                for elem in valor:
                    if hasattr(elem, "__dict__") and self._contiene_yield(
                        elem, visitados_ids
                    ):
                        return True
            elif hasattr(valor, "__dict__") and self._contiene_yield(
                valor, visitados_ids
            ):
                return True
        return False

    @staticmethod
    def _contar_nodos(ast):
        total = 0
        pila = list(ast)
        visitados = set()
        while pila:
            nodo = pila.pop()
            if id(nodo) in visitados:
                continue
            visitados.add(id(nodo))
            total += 1
            for val in getattr(nodo, "__dict__", {}).values():
                if isinstance(val, list):
                    for elem in val:
                        if hasattr(elem, "__dict__"):
                            pila.append(elem)
                elif hasattr(val, "__dict__"):
                    pila.append(val)
        return total

    @staticmethod
    def _asegurar_ast_tipado(ast, fase: str) -> None:
        """Garantiza el contrato mínimo del AST en una fase concreta."""
        try:
            validar_ast_estructural(ast)
        except ErrorEstructuraAST as exc:
            raise RuntimeError(f"Estructura AST inválida en fase '{fase}': {exc}") from exc

    def _asegurar_no_autorreferencia_asignacion(
        self, nombre, valor_nodo, visitados
    ) -> None:
        """Rechaza autorreferencias directas o indirectas antes de persistir."""
        if not isinstance(nombre, str):
            return
        if nombre in visitados:
            raise RuntimeError(f"Ciclo de variables detectado en '{nombre}'")

        visitados.add(nombre)
        try:
            if self._asignacion_referencia_identificador(valor_nodo, nombre):
                raise RuntimeError(f"Ciclo de variables detectado en '{nombre}'")

            pila = [valor_nodo]
            while pila:
                actual = pila.pop()
                if isinstance(actual, NodoIdentificador):
                    self._resolver_identificador(actual.nombre, visitados)
                    continue
                if isinstance(actual, Token):
                    continue
                if isinstance(actual, list):
                    pila.extend(actual)
                    continue
                if isinstance(actual, NodoAST):
                    pila.extend(getattr(actual, "__dict__", {}).values())
        finally:
            visitados.discard(nombre)

    @staticmethod
    def _debug_resumen_ast_habilitado() -> bool:
        """Activa una salida resumida del AST cuando el repr es grande."""
        return os.getenv("PCOBRA_DEBUG_AST_RESUMEN", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    @staticmethod
    def _resumir_ast(ast, max_chars: int = 2000) -> str:
        """Devuelve un resumen seguro del AST sin renderizar subnodos."""
        if not isinstance(ast, list):
            return f"ast_tipo={type(ast).__name__}"

        tipos_raiz = [type(nodo).__name__ for nodo in ast[:10]]
        restante = max(0, len(ast) - len(tipos_raiz))
        resumen = (
            f"ast_len={len(ast)} "
            f"total_nodos={InterpretadorCobra._contar_nodos(ast)} "
            f"tipos_raiz={tipos_raiz}"
        )
        if restante:
            resumen += f" (+{restante} tipos raíz más)"
        if len(resumen) <= max_chars:
            return resumen
        truncado = max_chars - len("... <resumen recortado>")
        return f"{resumen[:max(0, truncado)]}... <resumen recortado>"

    def _repr_corto(self, valor, max_chars: int = 160) -> str:
        """Devuelve un ``repr`` compacto para mensajes de error."""
        try:
            texto = repr(valor)
        except RecursionError:
            return (
                f"<repr_recursivo tipo={type(valor).__name__} "
                f"id={id(valor)}>"
            )
        if len(texto) <= max_chars:
            return texto
        restante = len(texto) - max_chars
        return f"{texto[:max_chars]}... <recortado {restante} caracteres>"

    def _asegurar_resultado_no_ast(
        self,
        resultado,
        *,
        nodo_origen,
        operador=None,
    ):
        """Garantiza que un resultado evaluado no propague nodos AST.

        Contrato explícito: las salidas de ``evaluar_expresion`` deben ser
        valores materializados y nunca instancias de ``NodoAST``.
        """
        if isinstance(resultado, NodoAST):
            operador_txt = operador if operador is not None else "<sin_operador>"
            raise RuntimeError(
                "Resultado no materializado en evaluar_expresion: "
                f"operador='{operador_txt}', "
                f"nodo_origen={type(nodo_origen).__name__}, "
                f"resultado_tipo={type(resultado).__name__}, "
                f"resultado_id={id(resultado)}"
            )
        return resultado

    def _asegurar_ast_aciclico_por_identidad(self, ast, fase: str) -> None:
        """Verifica que el AST no tenga ciclos por identidad de objetos."""

        visitados_globales: set[int] = set()
        en_ruta: set[int] = set()
        pila: list[tuple[object, bool]] = [(ast, False)]

        while pila:
            actual, salir = pila.pop()
            if not isinstance(actual, (NodoAST, NodoBloque, list)):
                continue

            actual_id = id(actual)
            if salir:
                en_ruta.discard(actual_id)
                visitados_globales.add(actual_id)
                continue

            if actual_id in visitados_globales:
                continue
            if actual_id in en_ruta:
                raise RuntimeError(
                    f"Se detectó un ciclo en el AST durante '{fase}' "
                    f"(node_id={actual_id})"
                )

            en_ruta.add(actual_id)
            pila.append((actual, True))

            if isinstance(actual, list):
                hijos = reversed(actual)
            else:
                hijos = reversed(list(getattr(actual, "__dict__", {}).values()))

            for hijo in hijos:
                if not isinstance(hijo, (NodoAST, NodoBloque, list)):
                    continue
                hijo_id = id(hijo)
                if hijo_id in en_ruta:
                    raise RuntimeError(
                        f"Se detectó un ciclo en el AST durante '{fase}' "
                        f"(node_id={hijo_id})"
                    )
                if hijo_id not in visitados_globales:
                    pila.append((hijo, False))

    def ejecutar_ast(self, ast):
        # Pipeline explícito:
        # 1) parseo/entrada tipada válida
        # 2) análisis semántico
        # 3) evaluación de AST validado
        self._validados.clear()
        self._asegurar_ast_tipado(ast, "parseo")
        total = self._contar_nodos(ast)
        max_nodos = limite_nodos()
        if total > max_nodos:
            raise RuntimeError(f"El AST excede el límite de {max_nodos} nodos")

        mem = limite_memoria_mb()
        if mem:
            _lim_mem(mem)
        cpu = limite_cpu_segundos()
        if cpu:
            _lim_cpu(cpu)

        self._asegurar_ast_tipado(ast, "pre_optimizacion")
        self._asegurar_ast_aciclico_por_identidad(ast, "pre_optimizacion")
        self._trace_debug("[AST BEFORE OPT]")
        self._trace_debug(self._resumir_ast(ast))
        if self._debug_resumen_ast_habilitado():
            self._trace_debug("[AST BEFORE OPT][SUMMARY]")
            self._trace_debug(self._resumir_ast(ast))

        ast = optimize_constants(ast)
        self._asegurar_ast_aciclico_por_identidad(ast, "post_optimize_constants")
        ast = eliminate_common_subexpressions(ast)
        self._asegurar_ast_aciclico_por_identidad(
            ast, "post_eliminate_common_subexpressions"
        )
        ast = inline_functions(ast)
        self._asegurar_ast_aciclico_por_identidad(ast, "post_inline_functions")
        ast = remove_dead_code(ast)
        self._asegurar_ast_aciclico_por_identidad(ast, "post_remove_dead_code")

        self._trace_debug("[AST AFTER OPT]")
        self._trace_debug(self._resumir_ast(ast))
        if self._debug_resumen_ast_habilitado():
            self._trace_debug("[AST AFTER OPT][SUMMARY]")
            self._trace_debug(self._resumir_ast(ast))
        self._asegurar_ast_tipado(ast, "post_optimizacion")
        self.ultimo_ir = None
        self._trace_debug("[RUN] antes de iterar AST")
        for index, nodo in enumerate(ast):
            self._trace_debug(
                f"[RUN] index={index} node_type={type(nodo).__name__} node_id={id(nodo)}"
            )
            modo_prev = self._set_mode("analysis")
            try:
                self._validar(nodo)
                self._set_mode("execution")
                self._trace_debug("[RUN] antes de ejecutar_nodo")
                resultado = self.ejecutar_nodo(nodo)
                if resultado is not None:
                    return resultado
            finally:
                self._set_mode(modo_prev)
        return None

    # -- Generación de IR ----------------------------------------------------
    def generar_internal_ir(self, ast) -> InternalIRModule:
        """Convierte un AST de Cobra en un módulo IR interno."""

        return build_internal_ir(ast)

    def ejecutar_nodo(self, nodo):
        self._trace_debug(f"[EXEC] node_type={type(nodo).__name__} node_id={id(nodo)}")
        if self.mode == "analysis":
            # En análisis no se ejecutan nodos: evita prints, mutaciones y efectos observables.
            return None
        self._auditar_en_ejecucion(nodo)
        if isinstance(nodo, NodoAsignacion):
            return self.ejecutar_asignacion(nodo)
        elif isinstance(nodo, NodoCondicional):
            return self.ejecutar_condicional(nodo)
        elif isinstance(nodo, NodoBucleMientras):
            return self.ejecutar_mientras(nodo)
        elif isinstance(nodo, NodoClase):
            self.ejecutar_clase(nodo)
        elif isinstance(nodo, NodoInstancia):
            return self.ejecutar_instancia(nodo)
        elif isinstance(nodo, NodoFuncion):
            self.ejecutar_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaFuncion):
            return self.ejecutar_llamada_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaMetodo):
            return self.ejecutar_llamada_metodo(nodo)
        elif isinstance(nodo, NodoImprimir):
            # Contrato: está prohibido serializar nodos completos (str/repr/f-string)
            # antes de evaluar; en debug solo usar type(nodo).__name__ e id(nodo).
            expresion = nodo.expresion
            valor = self.evaluar_expresion(expresion)
            valor = self._materializar_valor(valor)
            valor = self._asegurar_resultado_no_ast(
                valor,
                nodo_origen=expresion,
                operador="imprimir",
            )
            if self.in_execution():
                if isinstance(valor, bool):
                    print("verdadero" if valor else "falso")
                else:
                    print(valor)
        elif isinstance(nodo, NodoImport):
            return self.ejecutar_import(nodo)
        elif isinstance(nodo, NodoUsar):
            return self.ejecutar_usar(nodo)
        elif isinstance(nodo, NodoTryCatch):
            return self.ejecutar_try_catch(nodo)
        elif isinstance(nodo, NodoThrow):
            raise ExcepcionCobra(self.evaluar_expresion(nodo.expresion))
        elif isinstance(nodo, NodoAssert):
            condicion = self.evaluar_expresion(nodo.condicion)
            if not condicion:
                mensaje = (
                    self.evaluar_expresion(nodo.mensaje)
                    if nodo.mensaje
                    else "Assertion failed"
                )
                raise AssertionError(mensaje)
        elif isinstance(nodo, NodoDel):
            if not isinstance(nodo.objetivo, NodoIdentificador):
                raise TypeError(
                    "del requiere un identificador como objetivo, "
                    f"se recibió: {type(nodo.objetivo).__name__}"
                )
            nombre = nodo.objetivo.nombre
            indice_contexto = self._indice_entorno_variable(nombre)
            self.contextos[-1].delete(nombre)
            if indice_contexto is not None:
                self._liberar_memoria_variable_en_contexto(nombre, indice_contexto)
        elif isinstance(nodo, NodoGlobal):
            pass  # sin efecto en este intérprete simplificado
        elif isinstance(nodo, NodoNoLocal):
            pass
        elif isinstance(nodo, NodoWith):
            self.evaluar_expresion(nodo.contexto)
            self.contextos.append(Environment(parent=self.contextos[-1]))
            self.mem_contextos.append({})
            try:
                for instr in nodo.cuerpo:
                    resultado = self.ejecutar_nodo(instr)
                    if resultado is not None:
                        return resultado
            finally:
                memoria_local = self.mem_contextos.pop()
                for idx, tam in memoria_local.values():
                    self.liberar_memoria(idx, tam)
                self.contextos.pop()
        elif isinstance(nodo, NodoImportDesde):
            return self.ejecutar_import(NodoImport(nodo.modulo))
        elif isinstance(nodo, NodoHolobit):
            return self.ejecutar_holobit(nodo)
        elif isinstance(nodo, NodoHilo):
            return self.ejecutar_hilo(nodo)
        elif isinstance(nodo, NodoRetorno):
            return self.evaluar_expresion(nodo.expresion)
        elif isinstance(nodo, NodoRomper):
            raise _ControlRomper
        elif isinstance(nodo, NodoContinuar):
            raise _ControlContinuar
        elif isinstance(nodo, NodoEsperar):
            return self.evaluar_expresion(nodo.expresion)
        elif isinstance(nodo, NodoValor):
            return nodo.valor  # Retorna el valor directo de NodoValor
        else:
            raise ValueError(f"Nodo no soportado: {type(nodo)}")

    def ejecutar_asignacion(self, nodo, visitados=None):
        """Evalúa una asignación de variable o atributo."""
        visitados = set() if visitados is None else visitados
        nombre = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        # Evita llamadas recursivas directas con el mismo nodo
        if valor_nodo is nodo:
            raise ValueError("Asignación no puede evaluarse a sí misma")
        self._asegurar_no_autorreferencia_asignacion(nombre, valor_nodo, visitados)
        valor = self.evaluar_expresion(valor_nodo, visitados)
        valor = self._materializar_valor(valor, visitados)
        self._verificar_valor_contexto(valor)
        if isinstance(nombre, NodoAtributo):
            objeto = self.evaluar_expresion(nombre.objeto, visitados)
            if objeto is None:
                raise ValueError("Objeto no definido para asignación de atributo")
            atributos = objeto.setdefault("__atributos__", {})
            self._verificar_valor_contexto(valor)
            atributos[nombre.nombre] = valor
        else:
            if getattr(nodo, "inferencia", False) or getattr(nodo, "declaracion", False):
                # Declaración local (explícita o por inferencia)
                indice_contexto = len(self.mem_contextos) - 1
                self._liberar_memoria_variable_en_contexto(nombre, indice_contexto)
                indice = self.solicitar_memoria(1)
                self.mem_contextos[indice_contexto][nombre] = (indice, 1)
                self.contextos[-1].define(nombre, valor)
            else:
                indice_contexto = self._indice_entorno_variable(nombre)
                if indice_contexto is None:
                    raise NameError(f"Variable no declarada: {nombre}")
                else:
                    # Mutación sobre una variable existente: ``set`` solo
                    # actualiza en el scope donde ya está declarada.
                    self._liberar_memoria_variable_en_contexto(nombre, indice_contexto)
                    indice = self.solicitar_memoria(1)
                    self.mem_contextos[indice_contexto][nombre] = (indice, 1)
                    self.contextos[-1].set(nombre, valor)
        return valor

    def evaluar_expresion(self, expresion, visitados=None):
        """Resuelve el valor de una expresión de forma recursiva.

        El parámetro ``visitados`` se utiliza internamente para propagar el
        seguimiento de variables visitadas y detectar referencias circulares
        durante la evaluación.

        Contrato explícito de errores del evaluador:
        - identificador ausente -> ``NameError('Variable no declarada: ...')``
        - ciclo de referencias -> ``RuntimeError`` con mensaje de ciclo
        - para comparaciones, ambos operandos se evalúan/materializan por
          completo antes de aplicar el operador;
        - nunca debe propagarse un ``NodoAST`` hacia capas superiores:
          cualquier rama crítica debe devolver un valor materializado.
        """
        visitados = set() if visitados is None else visitados
        expresion_id = id(expresion)
        self._trace_debug(f"[EVAL] tipo={type(expresion).__name__} id={expresion_id}")
        if expresion_id in self._eval_stack:
            self._trace_debug(
                f"[RECURSION DETECTED] tipo={type(expresion).__name__} id={expresion_id}"
            )
            raise Exception("Recursive evaluation detected")
        self._eval_stack.add(expresion_id)
        try:
            def _retorno_critico(resultado, *, operador=None):
                return self._asegurar_resultado_no_ast(
                    resultado,
                    nodo_origen=expresion,
                    operador=operador,
                )

            if isinstance(expresion, NodoValor):
                return expresion.valor  # Obtiene el valor directo si es un NodoValor
            elif isinstance(expresion, Token) and expresion.tipo in {
                TipoToken.ENTERO,
                TipoToken.FLOTANTE,
                TipoToken.CADENA,
                TipoToken.BOOLEANO,
            }:
                return expresion.valor  # Si es un token de tipo literal, devuelve su valor
            elif isinstance(expresion, NodoAsignacion):
                # Resuelve asignaciones anidadas y devuelve su valor
                return self.ejecutar_asignacion(expresion, visitados)
            elif isinstance(expresion, NodoIdentificador):
                self._trace_debug(f"[ID] resolving {expresion.nombre}")
                valor = self._resolver_identificador(expresion.nombre, visitados)

                if valor is None:
                    raise RuntimeError(
                        f"Error semántico: identificador no definido '{expresion.nombre}'"
                    )

                if isinstance(valor, NodoValor):
                    valor = valor.valor

                if isinstance(valor, NodoAST):
                    raise RuntimeError(
                        "Error semántico: identificador "
                        f"'{expresion.nombre}' resolvió a un nodo AST "
                        f"({type(valor).__name__}) en lugar de un valor materializado"
                    )

                self._trace_debug(
                    "[ID] "
                    f"value_type={type(valor).__name__} value_id={id(valor)} "
                    f"is_runtime_value={not isinstance(valor, NodoAST)}"
                )

                return _retorno_critico(valor, operador="identificador")
            elif isinstance(expresion, NodoInstancia):
                return self.ejecutar_instancia(expresion)
            elif isinstance(expresion, NodoAtributo):
                objeto = self.evaluar_expresion(expresion.objeto, visitados)
                if objeto is None:
                    raise ValueError("Objeto no definido al acceder al atributo")
                atributos = objeto.get("__atributos__", {})
                valor = atributos.get(expresion.nombre)
                valor_resuelto = self._materializar_valor(valor, visitados)
                if valor_resuelto is not valor:
                    atributos[expresion.nombre] = valor_resuelto
                return _retorno_critico(valor_resuelto, operador="atributo")
            elif isinstance(expresion, NodoHolobit):
                return self.ejecutar_holobit(expresion)
            elif isinstance(expresion, NodoOperacionBinaria):
                tipo = expresion.operador.tipo
                self._trace_debug(
                    "[BIN-ENTER] "
                    f"id={id(expresion)} op={expresion.operador.valor} op_tipo={tipo} "
                    f"left_type={type(expresion.izquierda).__name__} "
                    f"right_type={type(expresion.derecha).__name__}"
                )
                self._trace_debug(f"[BIN] op_tipo={tipo} op_valor={expresion.operador.valor}")

                left = self.evaluar_expresion(expresion.izquierda, visitados)
                self._trace_debug(
                    "[BIN-LEFT] "
                    f"type={type(left).__name__} id={id(left)} "
                    f"is_primitive={isinstance(left, (int, float, bool, str))}"
                )
                right = self.evaluar_expresion(expresion.derecha, visitados)
                self._trace_debug(
                    "[BIN-RIGHT] "
                    f"type={type(right).__name__} id={id(right)} "
                    f"is_primitive={isinstance(right, (int, float, bool, str))}"
                )

                left = self._materializar_valor(
                    left,
                    visitados,
                    origen="operacion_binaria",
                )
                right = self._materializar_valor(
                    right,
                    visitados,
                    origen="operacion_binaria",
                )

                self._asegurar_resultado_no_ast(
                    left,
                    nodo_origen=expresion.izquierda,
                    operador=f"{tipo}:izquierda",
                )
                self._asegurar_resultado_no_ast(
                    right,
                    nodo_origen=expresion.derecha,
                    operador=f"{tipo}:derecha",
                )

                def _validar_operandos_primitivos():
                    """Valida de forma defensiva que ambos operandos sean primitivos runtime."""
                    if not isinstance(left, (int, float, bool, str)):
                        raise RuntimeError(
                            "Error semántico: operando izquierdo no es un valor "
                            f"primitivo runtime ({type(left).__name__})"
                        )
                    if not isinstance(right, (int, float, bool, str)):
                        raise RuntimeError(
                            "Error semántico: operando derecho no es un valor "
                            f"primitivo runtime ({type(right).__name__})"
                        )

                _validar_operandos_primitivos()

                if tipo == TipoToken.MAYORQUE:
                    verificar_comparables(left, right, ">")
                    result = left > right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.MENORQUE:
                    verificar_comparables(left, right, "<")
                    result = left < right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.MAYORIGUAL:
                    verificar_comparables(left, right, ">=")
                    result = left >= right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.MENORIGUAL:
                    verificar_comparables(left, right, "<=")
                    result = left <= right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.IGUAL:
                    result = left == right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.DIFERENTE:
                    result = left != right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result

                if tipo == TipoToken.SUMA:
                    verificar_sumables(left, right)
                    result = left + right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.RESTA:
                    verificar_numeros(left, right, "-")
                    result = left - right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.MULT:
                    verificar_numeros(left, right, "*")
                    result = left * right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.DIV:
                    verificar_numeros(left, right, "/")
                    result = left / right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.MOD:
                    verificar_numeros(left, right, "%")
                    result = left % right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.AND:
                    verificar_booleanos(left, right, "&&")
                    result = left and right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
                    return result
                elif tipo == TipoToken.OR:
                    verificar_booleanos(left, right, "||")
                    result = left or right
                    self._trace_debug(f"[BIN-RESULT] value={result} type={type(result).__name__}")
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
                if tipo == TipoToken.NOT:
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
            self._eval_stack.discard(expresion_id)

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
        bloque_si = getattr(
            nodo, "cuerpo_si", getattr(nodo, "bloque_si", NodoBloque())
        )
        bloque_sino = getattr(
            nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", NodoBloque())
        )
        condicion = self._evaluar_condicion_control(nodo.condicion)

        if condicion is True:
            for instruccion in bloque_si:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
            return None

        # Única ruta restante válida: ``False``.
        if bloque_sino is None:
            return None
        for instruccion in bloque_sino:
            resultado = self.ejecutar_nodo(instruccion)
            if resultado is not None:
                return resultado

    def ejecutar_mientras(self, nodo):
        """Ejecuta un bucle ``mientras`` hasta que la condición sea falsa."""
        # Regla semántica de scope:
        # ``mientras`` NO abre un ámbito nuevo por iteración. El cuerpo del
        # bucle reutiliza ``self.contextos[-1]`` en cada vuelta y, por tanto,
        # las mutaciones del contexto persisten entre iteraciones y después.
        while self._evaluar_condicion_control(nodo.condicion):
            try:
                for instruccion in nodo.cuerpo:
                    resultado = self.ejecutar_nodo(instruccion)
                    if isinstance(instruccion, NodoAsignacion):
                        continue
                    if resultado is not None:
                        return resultado
            except _ControlContinuar:
                continue
            except _ControlRomper:
                break
        return None

    def ejecutar_try_catch(self, nodo):
        """Ejecuta un bloque ``try`` con manejo de excepciones Cobra."""
        try:
            for instruccion in nodo.bloque_try:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        except ExcepcionCobra as exc:
            if nodo.nombre_excepcion:
                contexto_actual = self.contextos[-1]
                if contexto_actual.contains(nodo.nombre_excepcion):
                    contexto_actual.set(nodo.nombre_excepcion, exc.valor)
                else:
                    contexto_actual.define(nodo.nombre_excepcion, exc.valor)
            for instruccion in nodo.bloque_catch:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        finally:
            for instruccion in nodo.bloque_finally:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

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

    def ejecutar_llamada_funcion(self, nodo):
        """Ejecuta la invocación de una función, interna o del usuario."""
        emitir_salida_llamada = self.in_execution()
        if emitir_salida_llamada:
            print(f"WARNING: Llamada a funcion: {nodo.nombre}")
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
            funcion = self.obtener_variable(nodo.nombre)
            if not isinstance(funcion, dict) or funcion.get("tipo") != "funcion":
                if emitir_salida_llamada:
                    print(f"Funci\u00f3n '{nodo.nombre}' no implementada")
                return None

            if len(funcion["parametros"]) != len(nodo.argumentos):
                if emitir_salida_llamada:
                    print(
                        f"Error: se esperaban {len(funcion['parametros'])} argumentos"
                    )
                return None

            contiene_yield = any(
                self._contiene_yield(instr) for instr in funcion["cuerpo"]
            )

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
                self.contextos.append(Environment(parent=entorno_capturado))
                self.mem_contextos.append({})
                for nombre_param, valor in zip(funcion["parametros"], argumentos_resueltos):
                    indice = self.solicitar_memoria(1)
                    self.mem_contextos[-1][nombre_param] = (indice, 1)
                    self.contextos[-1].define(nombre_param, valor)

            def limpiar_contexto():
                # Se restaura el scope anterior al finalizar la llamada.
                memoria_local = self.mem_contextos.pop()
                for idx, tam in memoria_local.values():
                    self.liberar_memoria(idx, tam)
                self.contextos.pop()

            if contiene_yield:

                def generador():
                    preparar_contexto()
                    try:
                        for instr in funcion["cuerpo"]:
                            if isinstance(instr, NodoYield):
                                yield self.evaluar_expresion(instr.expresion)
                            else:
                                resultado = self.ejecutar_nodo(instr)
                                if resultado is not None:
                                    return
                    finally:
                        limpiar_contexto()

                return generador()
            else:
                preparar_contexto()
                try:
                    resultado = None
                    for instruccion in funcion["cuerpo"]:
                        resultado = self.ejecutar_nodo(instruccion)
                        if resultado is not None:
                            break
                    return resultado
                finally:
                    limpiar_contexto()

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
        bases = clase.get("bases", [])
        instancia = {"__clase__": clase, "__bases__": bases, "__atributos__": {}}
        self._verificar_valor_contexto(instancia)
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

        entorno_capturado = metodo.get("entorno", self.contextos[-1])
        self.contextos.append(Environment(parent=entorno_capturado))
        self.mem_contextos.append({})
        self.contextos[-1].define("self", objeto)
        for nombre_param, arg in zip(metodo.get("parametros", [])[1:], nodo.argumentos):
            valor = self.evaluar_expresion(arg)
            self._verificar_valor_contexto(valor)
            self.contextos[-1].define(nombre_param, valor)

        try:
            resultado = None
            for instruccion in metodo.get("cuerpo", []):
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    break
            return resultado
        finally:
            memoria_local = self.mem_contextos.pop()
            for idx, tam in memoria_local.values():
                self.liberar_memoria(idx, tam)
            self.contextos.pop()

    def ejecutar_import(self, nodo):
        """Carga y ejecuta un módulo especificado en la declaración import."""
        # Cada módulo inicia su propia validación
        self._validados.clear()
        ruta = nodo.ruta
        _sincronizar_config_import()
        try:
            ast = cargar_ast_modulo(
                ruta,
                modules_path=MODULES_PATH,
                whitelist=IMPORT_WHITELIST,
            )
        except PermissionError as exc:
            raise PrimitivaPeligrosaError(str(exc)) from exc
        except FileNotFoundError:
            raise FileNotFoundError(f"Módulo no encontrado: {nodo.ruta}")
        except Exception as exc:
            raise ImportError(
                f"Error al analizar el módulo importado '{nodo.ruta}': {exc}"
            ) from exc
        total = self._contar_nodos(ast)
        max_nodos = limite_nodos()
        if total > max_nodos:
            raise RuntimeError(f"El AST excede el límite de {max_nodos} nodos")
        for subnodo in ast:
            modo_prev = self._set_mode("analysis")
            try:
                self._validar(subnodo)
                self._set_mode("execution")
                self.ejecutar_nodo(subnodo)
            finally:
                self._set_mode(modo_prev)

    def ejecutar_usar(self, nodo):
        """Importa callables públicos de un módulo Python al contexto actual."""
        from .usar_loader import obtener_modulo

        try:
            nombre_modulo = nodo.modulo
            if self._repl_usar_alias_map is not None:
                modulo_resuelto = self._repl_usar_alias_map.get(nombre_modulo)
                if modulo_resuelto is None:
                    raise PermissionError(
                        "módulos externos no soportados en REPL"
                    )
                nombre_modulo = modulo_resuelto

            es_repl_estricto = self._repl_usar_alias_map is not None
            modulo = obtener_modulo(
                nombre_modulo,
                permitir_instalacion=not es_repl_estricto,
            )
            exportables = getattr(modulo, "__all__", None)
            if exportables is None:
                exportables = dir(modulo)

            simbolos_a_inyectar = []
            contexto_actual = self.contextos[-1]

            # Fase A: recolectar y validar todos los símbolos exportables.
            for nombre in exportables:
                if not isinstance(nombre, str) or nombre.startswith("_"):
                    continue

                if not hasattr(modulo, nombre):
                    continue

                simbolo = getattr(modulo, nombre)
                if not callable(simbolo):
                    continue

                simbolos_a_inyectar.append((nombre, simbolo))

            # Fase B: validar colisiones de forma completa antes de definir.
            for nombre, _simbolo in simbolos_a_inyectar:
                if contexto_actual.contains(nombre):
                    raise NameError(
                        "No se puede usar el módulo "
                        f"'{nodo.modulo}': el símbolo '{nombre}' ya existe en el contexto actual"
                    )

            # Definir en bloque solo si toda la validación anterior fue exitosa.
            for nombre, simbolo in simbolos_a_inyectar:
                contexto_actual.define(nombre, simbolo)
        except Exception as exc:
            logging.exception(f"Error al usar el módulo '{nodo.modulo}': {exc}")
            raise

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
        import threading

        def destino():
            self.ejecutar_llamada_funcion(nodo.llamada)

        # El hilo se marca como daemon para evitar que bloquee el cierre del
        # intérprete si queda en ejecución al finalizar el programa.
        hilo = threading.Thread(target=destino, daemon=True)
        hilo.start()
        return hilo
