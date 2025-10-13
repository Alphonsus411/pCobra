"""Implementación del intérprete del lenguaje Cobra."""

import logging
import os
from typing import Optional

from pcobra.cobra.core import Token, TipoToken, Lexer
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
from pcobra.cobra.core import Parser
from .memoria.gestor_memoria import GestorMemoriaGenetico
from .hololang_ir import HololangModule, build_hololang_ir
from .semantic_validators import (
    construir_cadena,
    PrimitivaPeligrosaError,
)
from pcobra.cobra.semantico import AnalizadorSemantico
from .qualia_bridge import register_execution
from .cobra_config import (
    limite_nodos,
    limite_memoria_mb,
    limite_cpu_segundos,
)
from .resource_limits import (
    limitar_memoria_mb as _lim_mem,
    limitar_cpu_segundos as _lim_cpu,
)

# Ruta de los módulos instalados junto con una lista blanca opcional.
MODULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cli", "modules")
)
IMPORT_WHITELIST = set()


def _ruta_import_permitida(ruta: str) -> bool:
    """Indica si una ruta está autorizada para importarse."""

    ruta_abs = os.path.abspath(ruta)
    ruta_real = os.path.realpath(ruta_abs)
    allowed_roots = [MODULES_PATH, *IMPORT_WHITELIST]

    for root in allowed_roots:
        if not root:
            continue
        root_abs = os.path.abspath(root)
        root_real = os.path.realpath(root_abs)
        try:
            if (
                os.path.commonpath([ruta_abs, root_abs]) == root_abs
                and os.path.commonpath([ruta_real, root_real]) == root_real
            ):
                return True
        except ValueError:
            # En diferentes unidades (por ejemplo en Windows) commonpath puede
            # fallar; en tal caso la ruta no pertenece al directorio permitido.
            continue
    return False


class ExcepcionCobra(Exception):
    def __init__(self, valor):
        super().__init__(valor)
        self.valor = valor


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""

    @staticmethod
    def _cargar_validadores(ruta):
        """Carga una lista de validadores desde un archivo Python."""
        import ast

        ruta_abs = os.path.abspath(ruta)
        if not _ruta_import_permitida(ruta_abs):
            raise ImportError(f"Módulo fuera de la lista blanca: {ruta}")
        ruta_real = os.path.realpath(ruta_abs)

        try:
            with open(ruta_real, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No se encontró el archivo de validadores: {ruta}"
            ) from e

        try:
            tree = ast.parse(source, filename=ruta_real)
        except SyntaxError as e:
            raise ImportError(f"Error de sintaxis en {ruta}: {e}") from e

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ImportError(
                    "Importaciones no permitidas en los validadores adicionales."
                )
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "__import__":
                    raise SyntaxError(
                        "El uso de __import__ está bloqueado en los validadores adicionales."
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
        byte_code = compile_restricted(source, ruta_abs, "exec")
        exec(byte_code, namespace)
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
        self.ultimo_ir: Optional[HololangModule] = None

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

        Utiliza un conjunto de nombres visitados para detectar referencias
        circulares y evitar bucles infinitos al resolver identificadores
        encadenados.
        """
        visitados = visitados or set()
        if nombre in visitados:
            raise RuntimeError(f"Referencia circular detectada en '{nombre}'")
        visitados.add(nombre)
        try:
            for contexto in reversed(self.contextos):
                if nombre in contexto:
                    valor = contexto[nombre]
                    # Resuelve nodos simples a valores primitivos
                    while isinstance(
                        valor,
                        (
                            NodoValor,
                            NodoIdentificador,
                            NodoAsignacion,
                            NodoInstancia,
                            NodoAtributo,
                            NodoOperacionBinaria,
                            NodoOperacionUnaria,
                            NodoEsperar,
                            NodoLlamadaFuncion,
                            NodoLlamadaMetodo,
                            NodoHolobit,
                            Token,
                        ),
                    ):
                        valor = self.evaluar_expresion(valor, visitados)
                    return valor
            return None
        finally:
            visitados.remove(nombre)

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

    def ejecutar_ast(self, ast):
        # Reinicia el conjunto de nodos validados al comenzar una ejecución
        self._validados.clear()
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

        ast = remove_dead_code(
            inline_functions(eliminate_common_subexpressions(optimize_constants(ast)))
        )
        # Genera y expone el IR de Hololang correspondiente al AST
        self.ultimo_ir = self.generar_hololang_ir(ast)
        register_execution(ast)
        self.analizador.analizar(ast)
        for nodo in ast:
            self._validar(nodo)
            resultado = self.ejecutar_nodo(nodo)
            if resultado is not None:
                return resultado
        return None

    # -- Generación de IR ----------------------------------------------------
    def generar_hololang_ir(self, ast) -> HololangModule:
        """Convierte un AST de Cobra en un módulo IR de Hololang."""

        return build_hololang_ir(ast)

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
            if valor is None and isinstance(nodo.expresion, NodoIdentificador):
                print(f"Variable '{nodo.expresion.nombre}' no definida")
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
            nombre = self.evaluar_expresion(nodo.objetivo)
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
        nombre = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        # Evita llamadas recursivas directas con el mismo nodo
        if valor_nodo is nodo:
            raise ValueError("Asignación no puede evaluarse a sí misma")
        valor = self.evaluar_expresion(valor_nodo, visitados)
        if isinstance(nombre, NodoAtributo):
            objeto = self.evaluar_expresion(nombre.objeto, visitados)
            if objeto is None:
                raise ValueError("Objeto no definido para asignación de atributo")
            atributos = objeto.setdefault("__atributos__", {})
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
        """
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
            return self.obtener_variable(expresion.nombre, visitados)
        elif isinstance(expresion, NodoInstancia):
            return self.ejecutar_instancia(expresion)
        elif isinstance(expresion, NodoAtributo):
            objeto = self.evaluar_expresion(expresion.objeto, visitados)
            if objeto is None:
                raise ValueError("Objeto no definido al acceder al atributo")
            atributos = objeto.get("__atributos__", {})
            return atributos.get(expresion.nombre)
        elif isinstance(expresion, NodoHolobit):
            return self.ejecutar_holobit(expresion)
        elif isinstance(expresion, NodoOperacionBinaria):
            izquierda = self.evaluar_expresion(expresion.izquierda, visitados)
            derecha = self.evaluar_expresion(expresion.derecha, visitados)
            tipo = expresion.operador.tipo
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
            elif tipo == TipoToken.MAYORQUE:
                verificar_comparables(izquierda, derecha, ">")
                return izquierda > derecha
            elif tipo == TipoToken.MENORQUE:
                verificar_comparables(izquierda, derecha, "<")
                return izquierda < derecha
            elif tipo == TipoToken.MAYORIGUAL:
                verificar_comparables(izquierda, derecha, ">=")
                return izquierda >= derecha
            elif tipo == TipoToken.MENORIGUAL:
                verificar_comparables(izquierda, derecha, "<=")
                return izquierda <= derecha
            elif tipo == TipoToken.IGUAL:
                return izquierda == derecha
            elif tipo == TipoToken.DIFERENTE:
                return izquierda != derecha
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

    def ejecutar_condicional(self, nodo):
        """Ejecuta un bloque condicional."""
        bloque_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
        bloque_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
        if self.evaluar_expresion(nodo.condicion):
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
        while self.evaluar_expresion(nodo.condicion):
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
        self.variables[nodo.nombre] = nodo

    def ejecutar_llamada_funcion(self, nodo):
        """Ejecuta la invocación de una función, interna o del usuario."""
        if nodo.nombre == "imprimir":
            for arg in nodo.argumentos:
                if isinstance(arg, Token) and arg.tipo == TipoToken.IDENTIFICADOR:
                    valor = self.obtener_variable(arg.valor)
                    if valor is None:
                        valor = f"Variable '{arg.valor}' no definida"
                else:
                    valor = self.evaluar_expresion(arg)
                print(valor)
        else:
            funcion = self.obtener_variable(nodo.nombre)
            if not isinstance(funcion, NodoFuncion):
                print(f"Funci\u00f3n '{nodo.nombre}' no implementada")
                return None

            if len(funcion.parametros) != len(nodo.argumentos):
                print(f"Error: se esperaban {len(funcion.parametros)} argumentos")
                return None

            contiene_yield = any(
                self._contiene_yield(instr) for instr in funcion.cuerpo
            )

            def preparar_contexto():
                self.contextos.append({})
                self.mem_contextos.append({})
                for nombre_param, arg in zip(funcion.parametros, nodo.argumentos):
                    valor = self.evaluar_expresion(arg)
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
                        for instr in funcion.cuerpo:
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
                for instruccion in funcion.cuerpo:
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
            if not isinstance(base, NodoClase):
                raise ValueError(f"Clase base '{base_nombre}' no definida")
            bases_resueltas.append(base)
        nodo.bases_resueltas = bases_resueltas
        self.variables[nodo.nombre] = nodo

    def ejecutar_instancia(self, nodo):
        """Crea una instancia de la clase indicada."""
        clase = self.obtener_variable(nodo.nombre_clase)
        if not isinstance(clase, NodoClase):
            raise ValueError(f"Clase '{nodo.nombre_clase}' no definida")
        bases = getattr(clase, "bases_resueltas", [])
        return {"__clase__": clase, "__bases__": bases, "__atributos__": {}}

    def ejecutar_llamada_metodo(self, nodo):
        """Invoca un método de un objeto instanciado."""
        objeto = self.evaluar_expresion(nodo.objeto)
        if not isinstance(objeto, dict) or "__clase__" not in objeto:
            raise ValueError("Objeto inv\u00e1lido en llamada a m\u00e9todo")
        clase = objeto["__clase__"]

        def buscar_metodo(clase_actual):
            metodo = next(
                (m for m in clase_actual.metodos if m.nombre == nodo.nombre_metodo),
                None,
            )
            if metodo is not None:
                return metodo
            for base in getattr(clase_actual, "bases_resueltas", []):
                encontrado = buscar_metodo(base)
                if encontrado is not None:
                    return encontrado
            return None

        metodo = buscar_metodo(clase)
        if metodo is None:
            raise ValueError(f"M\u00e9todo '{nodo.nombre_metodo}' no encontrado")

        contexto = {"self": objeto}
        self.contextos.append(contexto)
        self.mem_contextos.append({})
        for nombre_param, arg in zip(metodo.parametros[1:], nodo.argumentos):
            self.variables[nombre_param] = self.evaluar_expresion(arg)

        resultado = None
        for instruccion in metodo.cuerpo:
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
        ruta = os.path.abspath(nodo.ruta)
        if not _ruta_import_permitida(ruta):
            raise PrimitivaPeligrosaError(
                f"Importación de módulo no permitida: {nodo.ruta}"
            )

        try:
            ruta_real = os.path.realpath(ruta)
            with open(ruta_real, "r", encoding="utf-8") as f:
                codigo = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Módulo no encontrado: {nodo.ruta}")

        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        total = self._contar_nodos(ast)
        max_nodos = limite_nodos()
        if total > max_nodos:
            raise RuntimeError(f"El AST excede el límite de {max_nodos} nodos")
        for subnodo in ast:
            self._validar(subnodo)
            resultado = self.ejecutar_nodo(subnodo)
            if resultado is not None:
                return resultado

    def ejecutar_usar(self, nodo):
        """Importa un módulo de Python instalándolo si es necesario."""
        from pcobra.cobra.usar_loader import obtener_modulo

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
