"""Implementación del intérprete del lenguaje Cobra."""

import logging
import os
import hashlib
from typing import Optional

from pcobra.core.lexer import (
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
)
from .memoria.gestor_memoria import GestorMemoriaGenetico
from .internal_ir import InternalIRModule, build_internal_ir
from .semantic_validators import (
    construir_cadena,
    PrimitivaPeligrosaError,
)
from pcobra.core.semantico import AnalizadorSemantico
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


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""

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
        self._validador = construir_cadena(extra) if safe_mode else None
        # Analizador semántico persistente para mantener contexto entre ejecuciones
        self.analizador = AnalizadorSemantico()
        # Conjunto para evitar validar el mismo nodo varias veces
        self._validados = set()
        # Pila de contextos para mantener variables locales en cada llamada
        self.contextos = [{}]
        # Mapa paralelo para gestionar bloques de memoria por contexto
        self.mem_contextos = [{}]
        # Gestor genético de estrategias de memoria
        self.gestor_memoria = GestorMemoriaGenetico()
        self.estrategia = self.gestor_memoria.poblacion[0]
        self.op_memoria = 0
        # Último IR generado a partir del AST ejecutado
        self.ultimo_ir: Optional[InternalIRModule] = None

    @property
    def variables(self):
        """Devuelve el contexto actual de variables."""
        return self.contextos[-1]

    @variables.setter
    def variables(self, valor):
        """Permite reemplazar el contexto actual."""
        self.contextos[-1] = valor

    def obtener_variable(self, nombre, visitados=None):
        """Busca una variable en la pila de contextos.

        Evita seguir referencias encadenadas para prevenir bucles
        innecesarios y devuelve el valor almacenado directamente.
        """
        return self._resolver_identificador(nombre, visitados)

    def _asignacion_referencia_identificador(self, expresion, nombre):
        """Detecta si una expresión contiene una referencia al identificador."""
        if isinstance(expresion, NodoIdentificador):
            return expresion.nombre == nombre
        if isinstance(expresion, Token):
            return False
        for valor in getattr(expresion, "__dict__", {}).values():
            if isinstance(valor, list):
                for elem in valor:
                    if self._asignacion_referencia_identificador(elem, nombre):
                        return True
            elif self._asignacion_referencia_identificador(valor, nombre):
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
        """Resuelve un identificador usando únicamente la pila de contextos."""
        visitados = set() if visitados is None else visitados
        if nombre in visitados:
            raise RuntimeError(f"Ciclo de variables detectado en '{nombre}'")
        visitados.add(nombre)
        try:
            for contexto in reversed(self.contextos):
                if nombre in contexto:
                    valor = contexto[nombre]
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
                    # Persistimos siempre el valor ya materializado para
                    # consolidar el contrato de contexto -> materialización.
                    contexto[nombre] = valor_resuelto
                    return valor_resuelto
            raise NameError(f"Variable no declarada: {nombre}")
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
            "contexto": self.contextos[-1].copy(),
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
        primitivos = (int, float, bool, str, type(None))
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

            if (
                origen == "resolucion_variable"
                and isinstance(actual, dict)
                and actual.get("tipo") in {"funcion", "clase", "instancia"}
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
        """Valida un nodo si el modo seguro está activo."""
        if self.safe_mode and id(nodo) not in self._validados:
            nodo.aceptar(self._validador)
            self._validados.add(id(nodo))

    def _contiene_yield(self, nodo):
        if isinstance(nodo, NodoYield):
            return True
        if isinstance(nodo, Token):
            return False
        for valor in getattr(nodo, "__dict__", {}).values():
            if isinstance(valor, list):
                for elem in valor:
                    if hasattr(elem, "__dict__") and self._contiene_yield(elem):
                        return True
            elif hasattr(valor, "__dict__") and self._contiene_yield(valor):
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
        ast = remove_dead_code(
            inline_functions(eliminate_common_subexpressions(optimize_constants(ast)))
        )
        self._asegurar_ast_tipado(ast, "post_optimizacion")
        # Genera y expone el IR interno correspondiente al AST
        self.ultimo_ir = self.generar_internal_ir(ast)
        try:
            from .qualia_bridge import register_execution  # optional subsystem
        except (ImportError, ModuleNotFoundError):
            register_execution = None
        if register_execution:
            register_execution(ast)
        # Fase 2: análisis semántico estricto
        self.analizador.analizar(ast)
        # Fase 3: evaluación
        for nodo in ast:
            self._validar(nodo)
            resultado = self.ejecutar_nodo(nodo)
            if resultado is not None:
                return resultado
        return None

    # -- Generación de IR ----------------------------------------------------
    def generar_internal_ir(self, ast) -> InternalIRModule:
        """Convierte un AST de Cobra en un módulo IR interno."""

        return build_internal_ir(ast)

    def ejecutar_nodo(self, nodo):
        self._validar(nodo)
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
            valor = self.evaluar_expresion(nodo.expresion)
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
            if nombre in self.variables:
                del self.variables[nombre]
        elif isinstance(nodo, NodoGlobal):
            pass  # sin efecto en este intérprete simplificado
        elif isinstance(nodo, NodoNoLocal):
            pass
        elif isinstance(nodo, NodoWith):
            self.evaluar_expresion(nodo.contexto)
            self.contextos.append({})
            try:
                for instr in nodo.cuerpo:
                    resultado = self.ejecutar_nodo(instr)
                    if resultado is not None:
                        return resultado
            finally:
                self.contextos.pop()
        elif isinstance(nodo, NodoImportDesde):
            return self.ejecutar_import(NodoImport(nodo.modulo))
        elif isinstance(nodo, NodoHolobit):
            return self.ejecutar_holobit(nodo)
        elif isinstance(nodo, NodoHilo):
            return self.ejecutar_hilo(nodo)
        elif isinstance(nodo, NodoRetorno):
            return self.evaluar_expresion(nodo.expresion)
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
            if getattr(nodo, "inferencia", False):
                # Registro simple sin tipo explícito
                self.variables[nombre] = valor
            else:
                # Si la variable ya tiene memoria reservada, se libera
                mem_ctx = self.mem_contextos[-1]
                if nombre in mem_ctx:
                    idx, tam = mem_ctx.pop(nombre)
                    self.liberar_memoria(idx, tam)
                indice = self.solicitar_memoria(1)
                mem_ctx[nombre] = (indice, 1)
                self.variables[nombre] = valor
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
        - nunca debe propagarse un ``NodoAST`` hacia capas superiores.
        """
        visitados = set() if visitados is None else visitados
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
            return self._resolver_identificador(expresion.nombre, visitados)
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
            return valor_resuelto
        elif isinstance(expresion, NodoHolobit):
            return self.ejecutar_holobit(expresion)
        elif isinstance(expresion, NodoOperacionBinaria):
            tipo = expresion.operador.tipo

            izquierda = self.evaluar_expresion(expresion.izquierda, visitados)
            derecha = self.evaluar_expresion(expresion.derecha, visitados)

            izquierda = self._materializar_valor(
                izquierda,
                visitados,
                origen="operacion_binaria",
            )
            derecha = self._materializar_valor(
                derecha,
                visitados,
                origen="operacion_binaria",
            )

            if isinstance(izquierda, NodoAST):
                raise RuntimeError(
                    "Operando binario no materializado tras resolver: "
                    f"lado izquierdo, operador {tipo}, nodo {type(izquierda).__name__}"
                )
            if isinstance(derecha, NodoAST):
                raise RuntimeError(
                    "Operando binario no materializado tras resolver: "
                    f"lado derecho, operador {tipo}, nodo {type(derecha).__name__}"
                )

            def _aplicar_comparacion(operador):
                """Valida y aplica una comparación con operandos materializados."""
                if isinstance(izquierda, NodoAST):
                    raise RuntimeError(
                        "Operando de comparación no materializado: "
                        f"lado izquierdo, operador {tipo}, nodo {type(izquierda).__name__}"
                    )
                if isinstance(derecha, NodoAST):
                    raise RuntimeError(
                        "Operando de comparación no materializado: "
                        f"lado derecho, operador {tipo}, nodo {type(derecha).__name__}"
                    )
                return operador(izquierda, derecha)

            if tipo == TipoToken.MAYORQUE:
                verificar_comparables(izquierda, derecha, ">")
                return _aplicar_comparacion(lambda i, d: i > d)
            elif tipo == TipoToken.MENORQUE:
                verificar_comparables(izquierda, derecha, "<")
                return _aplicar_comparacion(lambda i, d: i < d)
            elif tipo == TipoToken.MAYORIGUAL:
                verificar_comparables(izquierda, derecha, ">=")
                return _aplicar_comparacion(lambda i, d: i >= d)
            elif tipo == TipoToken.MENORIGUAL:
                verificar_comparables(izquierda, derecha, "<=")
                return _aplicar_comparacion(lambda i, d: i <= d)
            elif tipo == TipoToken.IGUAL:
                return _aplicar_comparacion(lambda i, d: i == d)
            elif tipo == TipoToken.DIFERENTE:
                return _aplicar_comparacion(lambda i, d: i != d)

            if tipo == TipoToken.SUMA:
                verificar_sumables(izquierda, derecha)
                return izquierda + derecha
            elif tipo == TipoToken.RESTA:
                verificar_numeros(izquierda, derecha, "-")
                return izquierda - derecha
            elif tipo == TipoToken.MULT:
                verificar_numeros(izquierda, derecha, "*")
                return izquierda * derecha
            elif tipo == TipoToken.DIV:
                verificar_numeros(izquierda, derecha, "/")
                return izquierda / derecha
            elif tipo == TipoToken.MOD:
                verificar_numeros(izquierda, derecha, "%")
                return izquierda % derecha
            elif tipo == TipoToken.AND:
                verificar_booleanos(izquierda, derecha, "&&")
                return izquierda and derecha
            elif tipo == TipoToken.OR:
                verificar_booleanos(izquierda, derecha, "||")
                return izquierda or derecha
            else:
                raise ValueError(f"Operador no soportado: {tipo}")
        elif isinstance(expresion, NodoOperacionUnaria):
            valor = self.evaluar_expresion(expresion.operando, visitados)
            tipo = expresion.operador.tipo
            if tipo == TipoToken.NOT:
                verificar_booleano(valor, "!")
                return not valor
            else:
                raise ValueError(f"Operador unario no soportado: {tipo}")
        elif isinstance(expresion, NodoEsperar):
            return self.evaluar_expresion(expresion.expresion, visitados)
        elif isinstance(expresion, NodoLlamadaMetodo):
            return self.ejecutar_llamada_metodo(expresion)
        elif isinstance(expresion, NodoLlamadaFuncion):
            return self.ejecutar_llamada_funcion(expresion)
        else:
            raise ValueError(f"Expresión no soportada: {expresion}")

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
        if not isinstance(condicion_resuelta, bool):
            raise TypeError(
                "Condición de control inválida: se esperaba booleano materializado, "
                f"se obtuvo {type(condicion_resuelta).__name__}"
            )
        return condicion_resuelta

    def ejecutar_condicional(self, nodo):
        """Ejecuta un bloque condicional."""
        # Nota: no se captura ``NameError`` ni otras excepciones aquí para no
        # ocultar la causa real del fallo en la evaluación de la condición.
        bloque_si = getattr(
            nodo, "cuerpo_si", getattr(nodo, "bloque_si", NodoBloque())
        )
        bloque_sino = getattr(
            nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", NodoBloque())
        )
        if self._evaluar_condicion_control(nodo.condicion):
            for instruccion in bloque_si:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        elif bloque_sino:
            for instruccion in bloque_sino:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_mientras(self, nodo):
        """Ejecuta un bucle ``mientras`` hasta que la condición sea falsa."""
        while self._evaluar_condicion_control(nodo.condicion):
            for instruccion in nodo.cuerpo:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_try_catch(self, nodo):
        """Ejecuta un bloque ``try`` con manejo de excepciones Cobra."""
        try:
            for instruccion in nodo.bloque_try:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        except ExcepcionCobra as exc:
            if nodo.nombre_excepcion:
                self.variables[nodo.nombre_excepcion] = exc.valor
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
        """Registra una función definida por el usuario."""
        funcion = self._construir_funcion(nodo)
        self._verificar_valor_contexto(funcion)
        self.variables[nodo.nombre] = funcion

    def ejecutar_llamada_funcion(self, nodo):
        """Ejecuta la invocación de una función, interna o del usuario."""
        if nodo.nombre == "imprimir":
            for arg in nodo.argumentos:
                if isinstance(arg, Token) and arg.tipo == TipoToken.IDENTIFICADOR:
                    arg = NodoIdentificador(arg.valor)
                valor = self.evaluar_expresion(arg)
                print(valor)
        else:
            funcion = self.obtener_variable(nodo.nombre)
            if not isinstance(funcion, dict) or funcion.get("tipo") != "funcion":
                print(f"Funci\u00f3n '{nodo.nombre}' no implementada")
                return None

            if len(funcion["parametros"]) != len(nodo.argumentos):
                print(
                    f"Error: se esperaban {len(funcion['parametros'])} argumentos"
                )
                return None

            contiene_yield = any(
                self._contiene_yield(instr) for instr in funcion["cuerpo"]
            )

            def preparar_contexto():
                contexto_base = funcion.get("contexto", {}).copy()
                self._verificar_valor_contexto(contexto_base)
                self.contextos.append(contexto_base)
                self.mem_contextos.append({})
                for nombre_param, arg in zip(funcion["parametros"], nodo.argumentos):
                    valor = self.evaluar_expresion(arg)
                    self._verificar_valor_contexto(valor)
                    indice = self.solicitar_memoria(1)
                    self.mem_contextos[-1][nombre_param] = (indice, 1)
                    self.variables[nombre_param] = valor

            def limpiar_contexto():
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
                resultado = None
                for instruccion in funcion["cuerpo"]:
                    resultado = self.ejecutar_nodo(instruccion)
                    if resultado is not None:
                        break
                limpiar_contexto()
                return resultado

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
        self.variables[nodo.nombre] = clase

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

        contexto = {"self": objeto}
        contexto_base = metodo.get("contexto", {}).copy()
        contexto_base.update(contexto)
        self._verificar_valor_contexto(contexto_base)
        self.contextos.append(contexto_base)
        self.mem_contextos.append({})
        for nombre_param, arg in zip(metodo.get("parametros", [])[1:], nodo.argumentos):
            valor = self.evaluar_expresion(arg)
            self._verificar_valor_contexto(valor)
            self.variables[nombre_param] = valor

        resultado = None
        for instruccion in metodo.get("cuerpo", []):
            resultado = self.ejecutar_nodo(instruccion)
            if resultado is not None:
                break
        memoria_local = self.mem_contextos.pop()
        for idx, tam in memoria_local.values():
            self.liberar_memoria(idx, tam)
        self.contextos.pop()
        return resultado

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
            self._validar(subnodo)
            self.ejecutar_nodo(subnodo)

    def ejecutar_usar(self, nodo):
        """Importa un módulo de Python instalándolo si es necesario."""
        from pcobra.core.usar_loader import obtener_modulo

        try:
            modulo = obtener_modulo(nodo.modulo)
            self.variables[nodo.modulo] = modulo
        except Exception as exc:
            logging.exception(f"Error al usar el módulo '{nodo.modulo}': {exc}")
            raise

    def ejecutar_holobit(self, nodo):
        """Simula la ejecución de un holobit y devuelve sus valores."""
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
