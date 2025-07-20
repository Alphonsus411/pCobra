"""Implementación del intérprete del lenguaje Cobra."""

import os

from cobra.lexico.lexer import Token, TipoToken, Lexer
from core.optimizations import (
    optimize_constants,
    remove_dead_code,
    inline_functions,
    eliminate_common_subexpressions,
)
from core.type_utils import (
    verificar_sumables,
    verificar_numeros,
    verificar_comparables,
    verificar_booleanos,
    verificar_booleano,
)
from core.ast_nodes import (
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
)
from cobra.parser.parser import Parser
from core.memoria.gestor_memoria import GestorMemoriaGenetico
from core.semantic_validators import (
    construir_cadena,
    PrimitivaPeligrosaError,
)
from cobra.semantico import AnalizadorSemantico
from core.qualia_bridge import register_execution
from core.cobra_config import (
    limite_nodos,
    limite_memoria_mb,
    limite_cpu_segundos,
)
from core.resource_limits import (
    limitar_memoria_mb as _lim_mem,
    limitar_cpu_segundos as _lim_cpu,
)

# Ruta de los módulos instalados junto con una lista blanca opcional.
MODULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cli", "modules")
)
IMPORT_WHITELIST = set()


class ExcepcionCobra(Exception):
    def __init__(self, valor):
        super().__init__(valor)
        self.valor = valor


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""

    @staticmethod
    def _cargar_validadores(ruta):
        """Carga una lista de validadores desde un archivo Python."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("cobra_extra_validators", ruta)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "VALIDADORES_EXTRA", [])

    def __init__(self, safe_mode: bool = False, extra_validators=None):
        """Crea un nuevo interpretador.

        Parameters
        ----------
        safe_mode: bool, optional
            Si se activa, valida cada nodo utilizando la cadena devuelta por
            :func:`construir_cadena` y restringe primitivas como ``import`` o
            ``hilo``.
        extra_validators: list | str, optional
            Lista de instancias adicionales o ruta a un módulo que defina
            ``VALIDADORES_EXTRA``.
        """
        extra = extra_validators
        if isinstance(extra, str):
            extra = self._cargar_validadores(extra)

        self.safe_mode = safe_mode
        self._validador = construir_cadena(extra) if safe_mode else None
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

    @property
    def variables(self):
        """Devuelve el contexto actual de variables."""
        return self.contextos[-1]

    @variables.setter
    def variables(self, valor):
        """Permite reemplazar el contexto actual."""
        self.contextos[-1] = valor

    def obtener_variable(self, nombre):
        """Busca una variable en la pila de contextos."""
        for contexto in reversed(self.contextos):
            if nombre in contexto:
                return contexto[nombre]
        return None

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
        register_execution(str(ast))
        AnalizadorSemantico().analizar(ast)
        for nodo in ast:
            self._validar(nodo)
            resultado = self.ejecutar_nodo(nodo)
            if resultado is not None:
                return resultado
        return None

    def ejecutar_nodo(self, nodo):
        self._validar(nodo)
        if isinstance(nodo, NodoAsignacion):
            self.ejecutar_asignacion(nodo)
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
            if isinstance(valor, str):
                if (valor.startswith('"') and valor.endswith('"')) or (
                    valor.startswith("'") and valor.endswith("'")
                ):
                    print(valor.strip('"').strip("'"))
                else:
                    obtenido = self.obtener_variable(valor)
                    if obtenido is not None:
                        print(obtenido)
                    else:
                        print(f"Variable '{valor}' no definida")
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

    def ejecutar_asignacion(self, nodo):
        """Evalúa una asignación de variable o atributo."""
        nombre = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        valor = self.evaluar_expresion(valor_nodo)
        if isinstance(nombre, NodoAtributo):
            objeto = self.evaluar_expresion(nombre.objeto)
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

    def evaluar_expresion(self, expresion):
        """Resuelve el valor de una expresión de forma recursiva."""
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
            # Resuelve asignaciones anidadas, si existieran
            self.ejecutar_asignacion(expresion)
        elif isinstance(expresion, NodoIdentificador):
            return self.obtener_variable(expresion.nombre)
        elif isinstance(expresion, NodoInstancia):
            return self.ejecutar_instancia(expresion)
        elif isinstance(expresion, NodoAtributo):
            objeto = self.evaluar_expresion(expresion.objeto)
            if objeto is None:
                raise ValueError("Objeto no definido al acceder al atributo")
            atributos = objeto.get("__atributos__", {})
            return atributos.get(expresion.nombre)
        elif isinstance(expresion, NodoHolobit):
            return self.ejecutar_holobit(expresion)
        elif isinstance(expresion, NodoOperacionBinaria):
            izquierda = self.evaluar_expresion(expresion.izquierda)
            derecha = self.evaluar_expresion(expresion.derecha)
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
            valor = self.evaluar_expresion(expresion.operando)
            tipo = expresion.operador.tipo
            if tipo == TipoToken.NOT:
                verificar_booleano(valor, "!")
                return not valor
            else:
                raise ValueError(f"Operador unario no soportado: {tipo}")
        elif isinstance(expresion, NodoEsperar):
            return self.evaluar_expresion(expresion.expresion)
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
        self.variables[nodo.nombre] = nodo

    def ejecutar_instancia(self, nodo):
        """Crea una instancia de la clase indicada."""
        clase = self.obtener_variable(nodo.nombre_clase)
        if not isinstance(clase, NodoClase):
            raise ValueError(f"Clase '{nodo.nombre_clase}' no definida")
        return {"__clase__": clase, "__atributos__": {}}

    def ejecutar_llamada_metodo(self, nodo):
        """Invoca un método de un objeto instanciado."""
        objeto = self.evaluar_expresion(nodo.objeto)
        if not isinstance(objeto, dict) or "__clase__" not in objeto:
            raise ValueError("Objeto inv\u00e1lido en llamada a m\u00e9todo")
        clase = objeto["__clase__"]
        metodo = next(
            (m for m in clase.metodos if m.nombre == nodo.nombre_metodo), None
        )
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
        if not ruta.startswith(MODULES_PATH) and ruta not in IMPORT_WHITELIST:
            raise PrimitivaPeligrosaError(
                f"Importación de módulo no permitida: {nodo.ruta}"
            )

        try:
            with open(ruta, "r", encoding="utf-8") as f:
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
        from cobra.usar_loader import obtener_modulo

        try:
            modulo = obtener_modulo(nodo.modulo)
            self.variables[nodo.modulo] = modulo
        except Exception as exc:
            print(f"Error al usar el módulo '{nodo.modulo}': {exc}")

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

        hilo = threading.Thread(target=destino)
        hilo.start()
        return hilo
