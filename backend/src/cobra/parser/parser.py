"""Parser del lenguaje Cobra que genera un AST a partir de tokens."""

import logging
import json
from backend.src.cobra.lexico.lexer import TipoToken, Token

from backend.src.core.ast_nodes import (
    NodoAsignacion,
    NodoHolobit,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoClase,
    NodoMetodo,
    NodoLlamadaFuncion,
    NodoHilo,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoValor,
    NodoIdentificador,
    NodoImprimir,
    NodoRetorno,
    NodoPara,
    NodoDecorador,
    NodoTryCatch,
    NodoThrow,
    NodoRomper,
    NodoContinuar,
    NodoPasar,
    NodoImport,
    NodoUsar,
    NodoMacro,
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoImportDesde,
    NodoEsperar,
    NodoOption,
    NodoSwitch,
    NodoCase,
)

from backend.src.core import NodoYield

# Palabras reservadas que no pueden usarse como identificadores
PALABRAS_RESERVADAS = {
    "var",
    "func",
    "rel",
    "si",
    "sino",
    "mientras",
    "para",
    "import",
    "try",
    "catch",
    "throw",
    "hilo",
    "retorno",
    "fin",
    "in",
    "holobit",
    "imprimir",
    "proyectar",
    "transformar",
    "graficar",
    "usar",
    "macro",
    "clase",
    "decorador",
    "yield",
    "romper",
    "continuar",
    "pasar",
    "afirmar",
    "eliminar",
    "global",
    "nolocal",
    "lambda",
    "asincronico",
    "esperar",
    "con",
    "finalmente",
    "desde",
    "como",
    "switch",
    "case",
    "segun",
    "caso",
}


logging.basicConfig(level=logging.DEBUG)



class Parser:
    """Convierte una lista de tokens en nodos del AST."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.indentacion_actual = 0
        # Mapeo de tokens a funciones de construcción del AST
        self._factories = {
            TipoToken.VAR: self.declaracion_asignacion,
            TipoToken.HOLOBIT: self.declaracion_holobit,
            TipoToken.SI: self.declaracion_condicional,
            TipoToken.PARA: self.declaracion_para,
            TipoToken.MIENTRAS: self.declaracion_mientras,
            TipoToken.FUNC: self.declaracion_funcion,
            TipoToken.IMPORT: self.declaracion_import,
            TipoToken.USAR: self.declaracion_usar,
            TipoToken.IMPRIMIR: self.declaracion_imprimir,
            TipoToken.HILO: self.declaracion_hilo,
            TipoToken.TRY: self.declaracion_try_catch,
            TipoToken.THROW: self.declaracion_throw,
            TipoToken.YIELD: self.declaracion_yield,
            TipoToken.ROMPER: self.declaracion_romper,
            TipoToken.CONTINUAR: self.declaracion_continuar,
            TipoToken.PASAR: self.declaracion_pasar,
            TipoToken.MACRO: self.declaracion_macro,
            TipoToken.CLASE: self.declaracion_clase,
            TipoToken.AFIRMAR: self.declaracion_afirmar,
            TipoToken.ELIMINAR: self.declaracion_eliminar,
            TipoToken.GLOBAL: self.declaracion_global,
            TipoToken.NOLOCAL: self.declaracion_nolocal,
            TipoToken.CON: self.declaracion_con,
            TipoToken.DESDE: self.declaracion_desde,
            TipoToken.ESPERAR: self.declaracion_esperar,
            TipoToken.SWITCH: self.declaracion_switch,
        }

    def token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        # Retorna un token EOF si ya no hay más tokens
        return Token(TipoToken.EOF, None)

    def token_siguiente(self):
        if self.posicion + 1 < len(self.tokens):
            return self.tokens[self.posicion + 1]
        return None

    def avanzar(self):
        """Avanza al siguiente token, si es posible."""
        if self.posicion < len(self.tokens) - 1:
            self.posicion += 1

    def comer(self, tipo):
        if self.token_actual().tipo == tipo:
            self.avanzar()
        else:
            raise SyntaxError(
                f"Se esperaba {tipo}, pero se encontró {self.token_actual().tipo}"
            )

    def parsear(self):
        nodos = []
        while self.token_actual().tipo != TipoToken.EOF:
            nodos.append(self.declaracion())
        return nodos

    def declaracion(self):
        """Procesa una instrucción o expresión."""
        token = self.token_actual()
        try:
            # Alias 'definir' para declarar funciones
            if token.tipo == TipoToken.IDENTIFICADOR and token.valor == "definir":
                self.token_actual().tipo = TipoToken.FUNC
                token = self.token_actual()

            # Decoradores antes de funciones
            if token.tipo == TipoToken.DECORADOR:
                decoradores = []
                while self.token_actual().tipo == TipoToken.DECORADOR:
                    decoradores.append(self.declaracion_decorador())
                asincronica = False
                if self.token_actual().tipo == TipoToken.ASINCRONICO:
                    self.comer(TipoToken.ASINCRONICO)
                    asincronica = True
                if self.token_actual().tipo != TipoToken.FUNC:
                    raise SyntaxError("Un decorador debe preceder a una función")
                funcion = self.declaracion_funcion(asincronica)
                funcion.decoradores = decoradores + funcion.decoradores
                return funcion

            if token.tipo == TipoToken.ASINCRONICO:
                self.comer(TipoToken.ASINCRONICO)
                if self.token_actual().tipo == TipoToken.FUNC:
                    return self.declaracion_funcion(True)
                raise SyntaxError("Se esperaba 'func' después de 'asincronico'")

            if token.tipo == TipoToken.ESPERAR:
                return self.declaracion_esperar()

            # Manejo especial para declaraciones de retorno
            if token.tipo == TipoToken.RETORNO:
                self.comer(TipoToken.RETORNO)
                return NodoRetorno(self.expresion())

            # Busca una función de construcción asociada al tipo de token
            handler = self._factories.get(token.tipo)
            if handler:
                return handler()

            # Posibles expresiones o asignaciones/invocaciones
            if token.tipo in [TipoToken.IDENTIFICADOR, TipoToken.ENTERO, TipoToken.FLOTANTE, TipoToken.LAMBDA]:
                siguiente = self.token_siguiente()
                if siguiente and siguiente.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()
                elif siguiente and siguiente.tipo == TipoToken.ASIGNAR:
                    return self.declaracion_asignacion()
                return self.expresion()

            raise SyntaxError(f"Token inesperado: {token.tipo}")

        except Exception as e:
            logging.error(f"Error en la declaración: {e}")
            raise

    def declaracion_para(self):
        """Parsea una declaración de bucle 'para'."""
        self.comer(TipoToken.PARA)  # Consume el token 'para'

        # Captura la variable de iteración
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un identificador después de 'para'")
        variable = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)

        # Consume la palabra clave 'in'
        if self.token_actual().tipo != TipoToken.IN:
            raise SyntaxError("Se esperaba 'in' después del identificador en 'para'")
        self.comer(TipoToken.IN)

        # Procesa el rango o iterable
        try:
            iterable = self.expresion()

            # Normaliza el iterable a un NodoValor con su representación en texto
            if isinstance(iterable, NodoLlamadaFuncion):
                args = []
                for arg in iterable.argumentos:
                    if isinstance(arg, NodoValor):
                        args.append(str(arg.valor))
                    elif isinstance(arg, NodoIdentificador):
                        args.append(arg.nombre)
                    else:
                        args.append(str(arg))
                iterable_texto = f"{iterable.nombre}({', '.join(args)})"
                iterable = NodoValor(iterable_texto)
        except SyntaxError as e:
            raise SyntaxError(f"Error al procesar el iterable en 'para': {e}")

        # Verifica y consume el ':'
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después del iterable en 'para'")
        self.comer(TipoToken.DOSPUNTOS)

        # Parsea el cuerpo del bucle
        cuerpo = []
        max_iteraciones = 1000
        iteraciones = 0

        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            logging.debug(
                f"Procesando token dentro del bucle 'para': {self.token_actual()}"
            )
            iteraciones += 1
            if iteraciones > max_iteraciones:
                raise RuntimeError("Bucle infinito detectado en 'para'")

            try:
                cuerpo.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el cuerpo del bucle 'para': {e}")
                self.avanzar()  # Avanzar para evitar bloqueo

        logging.debug(f"Token actual antes de 'fin': {self.token_actual()}")
        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bucle 'para'")
        self.comer(TipoToken.FIN)

        logging.debug(
            f"Bucle 'para' parseado correctamente: variable={variable}, "
            f"iterable={iterable}, cuerpo={cuerpo}"
        )
        return NodoPara(variable, iterable, cuerpo)

    def llamada_funcion(self):
        """Parsea una llamada a función."""
        nombre_funcion = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)  # Consumir el nombre de la función
        self.comer(TipoToken.LPAREN)  # Consumir '('

        argumentos = []
        # Si no es un paréntesis de cierre, hay argumentos
        if self.token_actual().tipo != TipoToken.RPAREN:
            while True:
                argumentos.append(self.expresion())  # Parsear cada argumento
                # Si hay una coma, continuar con más argumentos
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break

        self.comer(TipoToken.RPAREN)  # Consumir ')'
        return NodoLlamadaFuncion(nombre_funcion, argumentos)


    def declaracion_asignacion(self):
        variable_token = None
        if self.token_actual().tipo == TipoToken.VAR:
            self.comer(TipoToken.VAR)  # Consume el token 'var' si está presente
        
        variable_token = self.token_actual()
        # Comprobación de palabras reservadas antes de validar el tipo
        if variable_token.valor in PALABRAS_RESERVADAS:
            raise SyntaxError(
                f"El identificador '{variable_token.valor}' es una palabra reservada"
            )

        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un identificador en la asignación")

        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        valor = self.expresion()
        # Si la expresión es un holobit, completar su nombre con la variable
        if isinstance(valor, NodoHolobit) and valor.nombre is None:
            valor.nombre = variable_token.valor
        # El identificador se pasa como cadena de texto
        return NodoAsignacion(variable_token.valor, valor)

    def declaracion_mientras(self):
        """Parsea un bucle mientras."""
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        logging.debug(f"Condición del bucle mientras: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError(
                "Se esperaba ':' después de la condición del bucle 'mientras'"
            )
        self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            try:
                cuerpo.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el cuerpo del bucle 'mientras': {e}")
                self.avanzar()  # Avanza para evitar bloqueo

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bucle 'mientras'")
        self.comer(TipoToken.FIN)

        logging.debug(f"Cuerpo del bucle mientras: {cuerpo}")
        return NodoBucleMientras(condicion, cuerpo)

    def declaracion_holobit(self):
        self.comer(TipoToken.HOLOBIT)
        self.comer(TipoToken.LPAREN)
        valores = []
        self.comer(TipoToken.LBRACKET)
        while self.token_actual().tipo != TipoToken.RBRACKET:
            if self.token_actual().tipo in [TipoToken.FLOTANTE, TipoToken.ENTERO]:
                valores.append(self.expresion())
            elif self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
            else:
                token_invalido = self.token_actual()
                self.avanzar()
                raise SyntaxError(
                    f"Token inesperado en declaracion_holobit: {token_invalido.tipo}"
                )
        self.comer(TipoToken.RBRACKET)
        self.comer(TipoToken.RPAREN)
        return NodoHolobit(valores=valores)

    def declaracion_switch(self):
        """Parsea una estructura switch/case."""
        self.comer(TipoToken.SWITCH)
        expresion = self.expresion()
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de 'switch'")
        self.comer(TipoToken.DOSPUNTOS)

        casos = []
        while self.token_actual().tipo == TipoToken.CASE:
            self.comer(TipoToken.CASE)
            valor = self.expresion()
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después de 'case'")
            self.comer(TipoToken.DOSPUNTOS)
            cuerpo = []
            while self.token_actual().tipo not in [TipoToken.CASE, TipoToken.SINO, TipoToken.FIN, TipoToken.EOF]:
                cuerpo.append(self.declaracion())
            casos.append(NodoCase(valor, cuerpo))

        bloque_defecto = []
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después de 'sino'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                bloque_defecto.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el switch")
        self.comer(TipoToken.FIN)

        return NodoSwitch(expresion, casos, bloque_defecto)

    def declaracion_condicional(self):
        """Parsea un bloque condicional."""
        self.comer(TipoToken.SI)
        condicion = self.expresion()
        logging.debug(f"Condición del condicional: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la condición del 'si'")
        self.comer(TipoToken.DOSPUNTOS)

        bloque_si = []
        while self.token_actual().tipo not in [
            TipoToken.SINO,
            TipoToken.FIN,
            TipoToken.EOF,
        ]:
            try:
                bloque_si.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el bloque 'si': {e}")
                self.avanzar()  # Evitar bloqueo en caso de error

        bloque_sino = []
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después del 'sino'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                try:
                    bloque_sino.append(self.declaracion())
                except SyntaxError as e:
                    logging.error(f"Error en el bloque 'sino': {e}")
                    self.avanzar()

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bloque condicional")
        self.comer(TipoToken.FIN)

        logging.debug(f"Bloque si: {bloque_si}, Bloque sino: {bloque_sino}")
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def declaracion_funcion(self, asincronica: bool = False):
        """Parsea una declaración de función."""
        self.comer(TipoToken.FUNC)

        # Captura el nombre de la función
        nombre_token = self.token_actual()
        if nombre_token.valor in PALABRAS_RESERVADAS:
            raise SyntaxError(
                f"El nombre de función '{nombre_token.valor}' es una palabra reservada"
            )
        if nombre_token.tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un nombre para la función después de 'func'")
        nombre = nombre_token.valor
        self.comer(TipoToken.IDENTIFICADOR)

        # Captura los parámetros
        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)

        # Verifica y consume ':'
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la declaración de la función")
        self.comer(TipoToken.DOSPUNTOS)

        # Parsea el cuerpo de la función
        cuerpo = []
        max_iteraciones = 1000  # Límite para evitar bucles infinitos
        iteraciones = 0

        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            iteraciones += 1
            if iteraciones > max_iteraciones:
                raise RuntimeError("Bucle infinito detectado en declaracion_funcion")

            try:
                if self.token_actual().tipo == TipoToken.RETORNO:
                    self.comer(TipoToken.RETORNO)
                    expresion = self.expresion()
                    cuerpo.append(NodoRetorno(expresion))
                else:
                    cuerpo.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el cuerpo de la función '{nombre}': {e}")
                self.avanzar()

        # Verifica y consume 'fin'
        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError(f"Se esperaba 'fin' para cerrar la función '{nombre}'")
        self.comer(TipoToken.FIN)

        logging.debug(f"Función '{nombre}' parseada con cuerpo: {cuerpo}")
        return NodoFuncion(nombre, parametros, cuerpo, asincronica=asincronica)

    def declaracion_imprimir(self):
        """Parsea una declaración de impresión."""
        self.comer(TipoToken.IMPRIMIR)  # Consume el token 'imprimir'
        self.comer(TipoToken.LPAREN)  # Consume '('

        # Procesa el contenido que será impreso (podría ser una expresión)
        expresion = self.expresion()
        if isinstance(expresion, NodoIdentificador):
            expresion = NodoValor(expresion.nombre)

        # Consume ')'
        if self.token_actual().tipo != TipoToken.RPAREN:
            raise SyntaxError("Se esperaba ')' al final de la instrucción 'imprimir'")
        self.comer(TipoToken.RPAREN)

        return NodoImprimir(expresion)

    def declaracion_import(self):
        """Parsea una declaración de importación de módulo."""
        self.comer(TipoToken.IMPORT)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise SyntaxError("Se esperaba una ruta de módulo entre comillas")
        ruta = self.token_actual().valor
        self.comer(TipoToken.CADENA)
        return NodoImport(ruta)

    def declaracion_usar(self):
        """Parsea una declaración 'usar' para importar módulos."""
        self.comer(TipoToken.USAR)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise SyntaxError("Se esperaba una ruta de módulo entre comillas")
        ruta = self.token_actual().valor
        self.comer(TipoToken.CADENA)
        return NodoUsar(ruta)

    def declaracion_decorador(self):
        """Parsea una línea de decorador previa a una función."""
        self.comer(TipoToken.DECORADOR)
        expresion = self.expresion()
        return NodoDecorador(expresion)

    def declaracion_hilo(self):
        """Parsea la creación de un hilo que ejecuta una función."""
        self.comer(TipoToken.HILO)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba el nombre de una función después de 'hilo'")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LPAREN)
        argumentos = []
        if self.token_actual().tipo != TipoToken.RPAREN:
            while True:
                argumentos.append(self.expresion())
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break
        self.comer(TipoToken.RPAREN)
        llamada = NodoLlamadaFuncion(nombre, argumentos)
        return NodoHilo(llamada)

    def declaracion_try_catch(self):
        self.comer(TipoToken.TRY)
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de 'try'")
        self.comer(TipoToken.DOSPUNTOS)

        bloque_try = []
        while self.token_actual().tipo not in [TipoToken.CATCH, TipoToken.FIN, TipoToken.EOF]:
            bloque_try.append(self.declaracion())

        nombre_exc = None
        bloque_catch = []
        if self.token_actual().tipo == TipoToken.CATCH:
            self.comer(TipoToken.CATCH)
            if self.token_actual().tipo == TipoToken.IDENTIFICADOR:
                nombre_exc = self.token_actual().valor
                self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después de 'catch'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF, TipoToken.FINALMENTE]:
                bloque_catch.append(self.declaracion())

        bloque_finally = []
        if self.token_actual().tipo == TipoToken.FINALMENTE:
            self.comer(TipoToken.FINALMENTE)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después de 'finalmente'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                bloque_finally.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bloque try/catch")
        self.comer(TipoToken.FIN)

        return NodoTryCatch(bloque_try, nombre_exc, bloque_catch, bloque_finally)

    def declaracion_throw(self):
        """Parsea una declaración 'throw'."""
        self.comer(TipoToken.THROW)
        return NodoThrow(self.expresion())

    def declaracion_yield(self):
        """Parsea una expresión 'yield' dentro de una función generadora."""
        self.comer(TipoToken.YIELD)
        return NodoYield(self.expresion())

    def declaracion_esperar(self):
        """Parsea una expresión 'esperar' para await."""
        self.comer(TipoToken.ESPERAR)
        return NodoEsperar(self.expresion())

    def declaracion_romper(self):
        """Parsea la sentencia 'romper' para salir de un bucle."""
        self.comer(TipoToken.ROMPER)
        return NodoRomper()

    def declaracion_continuar(self):
        """Parsea la sentencia 'continuar' para la siguiente iteración."""
        self.comer(TipoToken.CONTINUAR)
        return NodoContinuar()

    def declaracion_pasar(self):
        """Parsea la sentencia 'pasar' que no realiza ninguna acción."""
        self.comer(TipoToken.PASAR)
        return NodoPasar()

    def declaracion_afirmar(self):
        self.comer(TipoToken.AFIRMAR)
        condicion = self.expresion()
        mensaje = None
        if self.token_actual().tipo == TipoToken.COMA:
            self.comer(TipoToken.COMA)
            mensaje = self.expresion()
        return NodoAssert(condicion, mensaje)

    def declaracion_eliminar(self):
        self.comer(TipoToken.ELIMINAR)
        objetivo = self.expresion()
        return NodoDel(objetivo)

    def declaracion_global(self):
        self.comer(TipoToken.GLOBAL)
        nombres = []
        while self.token_actual().tipo == TipoToken.IDENTIFICADOR:
            nombres.append(self.token_actual().valor)
            self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
            else:
                break
        return NodoGlobal(nombres)

    def declaracion_nolocal(self):
        self.comer(TipoToken.NOLOCAL)
        nombres = []
        while self.token_actual().tipo == TipoToken.IDENTIFICADOR:
            nombres.append(self.token_actual().valor)
            self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
            else:
                break
        return NodoNoLocal(nombres)

    def declaracion_con(self):
        self.comer(TipoToken.CON)
        contexto = self.expresion()
        alias = None
        if self.token_actual().tipo == TipoToken.COMO:
            self.comer(TipoToken.COMO)
            if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                raise SyntaxError("Se esperaba un identificador luego de 'como'")
            alias = self.token_actual().valor
            self.comer(TipoToken.IDENTIFICADOR)
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de 'con'")
        self.comer(TipoToken.DOSPUNTOS)
        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            cuerpo.append(self.declaracion())
        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bloque 'con'")
        self.comer(TipoToken.FIN)
        return NodoWith(contexto, alias, cuerpo)

    def declaracion_desde(self):
        self.comer(TipoToken.DESDE)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise SyntaxError("Se esperaba una ruta de módulo entre comillas")
        modulo = self.token_actual().valor
        self.comer(TipoToken.CADENA)
        if self.token_actual().tipo != TipoToken.IMPORT:
            raise SyntaxError("Se esperaba 'import' después de 'desde'")
        self.comer(TipoToken.IMPORT)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un nombre a importar")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        alias = None
        if self.token_actual().tipo == TipoToken.COMO:
            self.comer(TipoToken.COMO)
            if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                raise SyntaxError("Se esperaba un alias después de 'como'")
            alias = self.token_actual().valor
            self.comer(TipoToken.IDENTIFICADOR)
        return NodoImportDesde(modulo, nombre, alias)

    def declaracion_macro(self):
        """Parsea la definición de una macro simple."""
        self.comer(TipoToken.MACRO)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un nombre de macro")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LBRACE)
        cuerpo_tokens = []
        profundidad = 1
        while profundidad > 0 and self.token_actual().tipo != TipoToken.EOF:
            token = self.token_actual()
            if token.tipo == TipoToken.LBRACE:
                profundidad += 1
            elif token.tipo == TipoToken.RBRACE:
                profundidad -= 1
                if profundidad == 0:
                    break
            cuerpo_tokens.append(token)
            self.avanzar()
        self.comer(TipoToken.RBRACE)
        cuerpo_parser = Parser(cuerpo_tokens + [Token(TipoToken.EOF, None)])
        cuerpo = cuerpo_parser.parsear()
        return NodoMacro(nombre, cuerpo)

    def declaracion_metodo(self, asincronica: bool = False):
        """Parsea la declaración de un método dentro de una clase."""
        if self.token_actual().tipo == TipoToken.ASINCRONICO:
            self.comer(TipoToken.ASINCRONICO)
            asincronica = True
        self.comer(TipoToken.FUNC)

        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un nombre de método")
        nombre = self.token_actual().valor
        if nombre in PALABRAS_RESERVADAS:
            raise SyntaxError(
                f"El nombre del método '{nombre}' es una palabra reservada"
            )
        self.comer(TipoToken.IDENTIFICADOR)

        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)

        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la cabecera del método")
        self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            cuerpo.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el método")
        self.comer(TipoToken.FIN)

        return NodoMetodo(nombre, parametros, cuerpo, asincronica=asincronica)

    def declaracion_clase(self):
        """Parsea la declaración de una clase."""
        self.comer(TipoToken.CLASE)

        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise SyntaxError("Se esperaba un nombre de clase")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)

        bases = []
        if self.token_actual().tipo == TipoToken.LPAREN:
            self.comer(TipoToken.LPAREN)
            while self.token_actual().tipo != TipoToken.RPAREN:
                if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                    raise SyntaxError("Se esperaba un nombre de clase base")
                bases.append(self.token_actual().valor)
                self.comer(TipoToken.IDENTIFICADOR)
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break
            self.comer(TipoToken.RPAREN)

        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después del encabezado de la clase")
        self.comer(TipoToken.DOSPUNTOS)

        metodos = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            if self.token_actual().tipo in [TipoToken.FUNC, TipoToken.ASINCRONICO]:
                metodos.append(self.declaracion_metodo())
            else:
                metodos.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar la clase")
        self.comer(TipoToken.FIN)

        return NodoClase(nombre, metodos, bases)

    def expresion(self):
        return self.exp_or()

    def exp_or(self):
        nodo = self.exp_and()
        while self.token_actual().tipo == TipoToken.OR:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_and()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_and(self):
        nodo = self.exp_equality()
        while self.token_actual().tipo == TipoToken.AND:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_equality()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_equality(self):
        nodo = self.exp_comparison()
        while self.token_actual().tipo in [TipoToken.IGUAL, TipoToken.DIFERENTE]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_comparison()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_comparison(self):
        nodo = self.exp_addition()
        while self.token_actual().tipo in [
            TipoToken.MAYORQUE,
            TipoToken.MAYORIGUAL,
            TipoToken.MENORQUE,
            TipoToken.MENORIGUAL,
        ]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_addition()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_addition(self):
        nodo = self.exp_multiplication()
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_multiplication()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_multiplication(self):
        nodo = self.exp_unario()
        while self.token_actual().tipo in [TipoToken.MULT, TipoToken.DIV, TipoToken.MOD]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_unario()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_unario(self):
        if self.token_actual().tipo == TipoToken.NOT:
            operador = self.token_actual()
            self.avanzar()
            operando = self.exp_unario()
            return NodoOperacionUnaria(operador, operando)
        elif self.token_actual().tipo == TipoToken.ESPERAR:
            self.comer(TipoToken.ESPERAR)
            return NodoEsperar(self.exp_unario())
        else:
            return self.termino()

    def termino(self):
        """Procesa términos como literales, identificadores y llamados a funciones."""
        token = self.token_actual()
        if token.tipo == TipoToken.ENTERO:
            self.comer(TipoToken.ENTERO)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.FLOTANTE:
            self.comer(TipoToken.FLOTANTE)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.CADENA:
            self.comer(TipoToken.CADENA)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.LAMBDA:
            self.comer(TipoToken.LAMBDA)
            parametros = []
            while self.token_actual().tipo == TipoToken.IDENTIFICADOR:
                parametros.append(self.token_actual().valor)
                self.comer(TipoToken.IDENTIFICADOR)
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' en la expresión lambda")
            self.comer(TipoToken.DOSPUNTOS)
            cuerpo = self.expresion()
            return NodoLambda(parametros, cuerpo)
        elif token.tipo == TipoToken.IDENTIFICADOR:
            if token.valor == "Some":
                self.comer(TipoToken.IDENTIFICADOR)
                self.comer(TipoToken.LPAREN)
                valor = self.expresion()
                self.comer(TipoToken.RPAREN)
                return NodoOption(valor)
            elif token.valor == "None":
                self.comer(TipoToken.IDENTIFICADOR)
                return NodoOption(None)
            else:
                siguiente_token = self.token_siguiente()
                if siguiente_token and siguiente_token.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()
                self.comer(TipoToken.IDENTIFICADOR)
                return NodoIdentificador(token.valor)
        elif token.tipo == TipoToken.HOLOBIT:
            # Permitir el uso de 'holobit' dentro de expresiones
            return self.declaracion_holobit()
        else:
            raise SyntaxError(f"Token inesperado en término: {token.tipo}")

    def lista_parametros(self):
        parametros = []
        while self.token_actual().tipo == TipoToken.IDENTIFICADOR:
            nombre_parametro = self.token_actual().valor
            if nombre_parametro in ["si", "mientras", "func", "fin"]:
                raise SyntaxError(
                    f"El nombre del parámetro '{nombre_parametro}' es reservado."
                )
            if nombre_parametro in parametros:
                raise SyntaxError(
                    f"El parámetro '{nombre_parametro}' ya está definido."
                )
            parametros.append(nombre_parametro)
            self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
        return parametros

    def ast_to_json(self, nodo):
        """Exporta el AST a un formato JSON para depuración o visualización."""
        return json.dumps(nodo, default=lambda o: o.__dict__, indent=4)
