"""Parser del lenguaje Cobra que genera un AST a partir de tokens."""

import logging
import json
import os
from cobra.lexico.lexer import TipoToken, Token
from .utils import PALABRAS_RESERVADAS, sugerir_palabra_clave

from core.ast_nodes import (
    NodoAsignacion,
    NodoHolobit,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoClase,
    NodoMetodo,
    NodoAtributo,
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

from core import NodoYield




logger = logging.getLogger(__name__)


class ClassicParser:
    """Convierte una lista de tokens en nodos del AST."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.indentacion_actual = 0
        self.errores: list[str] = []
        # Mapeo de tokens a funciones de construcción del AST
        self._factories = {
            TipoToken.VAR: self.declaracion_asignacion,
            TipoToken.VARIABLE: self.declaracion_asignacion,
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
            TipoToken.INTENTAR: self.declaracion_try_catch,
            TipoToken.THROW: self.declaracion_throw,
            TipoToken.LANZAR: self.declaracion_throw,
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
            TipoToken.ASINCRONICO: self.declaracion_asincronico,
            TipoToken.ESPERAR: self.declaracion_esperar,
            TipoToken.SWITCH: self.declaracion_switch,
        }

    def reportar_error(self, mensaje: str) -> None:
        """Registra un mensaje de error para reportarlo al final."""
        self.errores.append(mensaje)

    def token_actual(self):
        """Devuelve el token actualmente en procesamiento.

        Returns
        -------
        Token
            El token en la posición actual o ``EOF`` si se alcanzó el final.
        """
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        # Retorna un token EOF si ya no hay más tokens
        return Token(TipoToken.EOF, None)

    def token_siguiente(self):
        """Obtiene el token siguiente sin avanzar el cursor.

        Returns
        -------
        Token | None
            El token en la siguiente posición o ``None`` si no existe.
        """
        if self.posicion + 1 < len(self.tokens):
            return self.tokens[self.posicion + 1]
        return None

    def avanzar(self):
        """Avanza al siguiente token, si es posible."""
        if self.posicion < len(self.tokens) - 1:
            self.posicion += 1

    def comer(self, tipo):
        """Consume un token del tipo indicado o lanza ``ParserError``.

        Parameters
        ----------
        tipo : TipoToken
            Tipo de token que se espera consumir.
        """
        if self.token_actual().tipo == tipo:
            self.avanzar()
        else:
            raise ParserError(
                f"Se esperaba {tipo}, pero se encontró {self.token_actual().tipo}"
            )

    def _parsear_base(self):
        nodos = []
        while self.token_actual().tipo != TipoToken.EOF:
            nodos.append(self.declaracion())
        return nodos

    def parsear(self, *, incremental: bool = False, profile: bool = False):
        """Parsea tokens con soporte de caché incremental y perfilado."""
        if incremental:
            from core.ast_cache import obtener_ast_fragmento

            codigo = "\n".join(
                token.valor if token.valor is not None else ""
                for token in self.tokens
                if token.tipo != TipoToken.EOF
            )
            return obtener_ast_fragmento(codigo)

        if profile:
            import cProfile
            import pstats
            import io

            pr = cProfile.Profile()
            pr.enable()
            resultado = self._parsear_base()
            pr.disable()
            s = io.StringIO()
            pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(5)
            print("Parser profile:\n" + s.getvalue())
        else:
            resultado = self._parsear_base()

        if self.errores:
            raise ParserError("\n".join(self.errores))
        return resultado

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
                    raise ParserError("Un decorador debe preceder a una función")
                funcion = self.declaracion_funcion(asincronica)
                funcion.decoradores = decoradores + funcion.decoradores
                return funcion

            if token.tipo == TipoToken.ASINCRONICO:
                return self.declaracion_asincronico()

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

            if token.tipo == TipoToken.IDENTIFICADOR:
                sugerencia = sugerir_palabra_clave(token.valor)
                if sugerencia:
                    raise ParserError(
                        f"Token inesperado. ¿Quiso decir '{sugerencia}'?"
                    )

            # Posibles expresiones o asignaciones/invocaciones
            if token.tipo == TipoToken.ATRIBUTO:
                atrib = self.exp_atributo()
                if self.token_actual().tipo == TipoToken.ASIGNAR:
                    self.comer(TipoToken.ASIGNAR)
                    valor = self.expresion()
                    return NodoAsignacion(atrib, valor)
                return atrib
            if token.tipo in [
                TipoToken.IDENTIFICADOR,
                TipoToken.ENTERO,
                TipoToken.FLOTANTE,
                TipoToken.LAMBDA,
            ]:
                siguiente = self.token_siguiente()
                if siguiente and siguiente.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()
                elif siguiente and siguiente.tipo == TipoToken.ASIGNAR:
                    return self.declaracion_asignacion()
                return self.expresion()

            raise ParserError(f"Token inesperado: {token.tipo}")

        except Exception as e:
            logger.error(f"Error en la declaración: {e}")
            raise

    def declaracion_para(self):
        """Parsea una declaración de bucle 'para'."""
        self.comer(TipoToken.PARA)  # Consume el token 'para'

        # Captura la variable de iteración
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            self.reportar_error("Se esperaba un identificador después de 'para'")
            variable = "<error>"
        else:
            variable = self.token_actual().valor
            self.comer(TipoToken.IDENTIFICADOR)

        # Consume la palabra clave 'in'
        if self.token_actual().tipo != TipoToken.IN:
            self.reportar_error("Se esperaba 'in' después del identificador en 'para'")
        else:
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
        except ParserError as e:
            self.reportar_error(f"Error al procesar el iterable en 'para': {e}")
            iterable = NodoValor(None)
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()

        # Verifica y consume el ':'
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            self.reportar_error("Se esperaba ':' después del iterable en 'para'")
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()
        else:
            self.comer(TipoToken.DOSPUNTOS)

        # Parsea el cuerpo del bucle
        cuerpo = []

        while True:
            token = self.token_actual()
            if token.tipo in (TipoToken.FIN, TipoToken.EOF):
                break

            logger.debug(
                f"Procesando token dentro del bucle 'para': {self.token_actual()}"
            )

            posicion_inicial = self.posicion
            try:
                cuerpo.append(self.declaracion())
            except ParserError as e:
                logger.error(f"Error en el cuerpo del bucle 'para': {e}")
                self.reportar_error(f"Error en el cuerpo del bucle 'para': {e}")
                if self.token_actual().tipo != TipoToken.EOF:
                    self.avanzar()  # Avanzar para evitar bloqueo

            if self.posicion == posicion_inicial:
                self.reportar_error(
                    "La declaración dentro del bucle 'para' no consumió tokens"
                )
                if self.token_actual().tipo != TipoToken.EOF:
                    self.avanzar()

        logger.debug(f"Token actual antes de 'fin': {self.token_actual()}")
        if self.token_actual().tipo == TipoToken.FIN:
            self.comer(TipoToken.FIN)
        else:
            self.reportar_error("Se esperaba 'fin' para cerrar el bucle 'para'")
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()

        logger.debug(
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
        """Procesa una asignación de variable opcionalmente inferida.

        Returns
        -------
        NodoAsignacion
            Nodo del AST que representa la asignación realizada.
        """
        variable_token = None
        inferencia = False
        nombre_embedido = None
        if self.token_actual().tipo in (TipoToken.VAR, TipoToken.VARIABLE):
            inferencia = self.token_actual().tipo == TipoToken.VARIABLE
            # Permite 'var x = 1' y un caso compacto donde el nombre está en el token
            siguiente = self.token_siguiente()
            if siguiente and siguiente.tipo == TipoToken.ASIGNAR:
                nombre_embedido = self.token_actual().valor
            self.comer(self.token_actual().tipo)

        if self.token_actual().tipo == TipoToken.ATRIBUTO:
            variable_token = self.exp_atributo()
        else:
            variable_token = self.token_actual()
            if nombre_embedido is not None and self.token_actual().tipo == TipoToken.ASIGNAR:
                variable_token = Token(TipoToken.IDENTIFICADOR, nombre_embedido)
            if variable_token.valor in PALABRAS_RESERVADAS:
                raise ParserError(
                    (
                        "El identificador "
                        f"'{variable_token.valor}' es una palabra reservada"
                    )
                )
            if variable_token.tipo != TipoToken.IDENTIFICADOR:
                raise ParserError("Se esperaba un identificador en la asignación")
            if nombre_embedido is None:
                self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR_INFERENCIA if inferencia else TipoToken.ASIGNAR)
        valor = self.expresion()
        if (
            isinstance(valor, NodoHolobit)
            and valor.nombre is None
            and not isinstance(variable_token, NodoAtributo)
        ):
            valor.nombre = variable_token.valor
        nombre_asignacion = (
            variable_token
            if isinstance(variable_token, NodoAtributo)
            else variable_token.valor
        )
        return NodoAsignacion(nombre_asignacion, valor, inferencia)

    def declaracion_mientras(self):
        """Parsea un bucle mientras."""
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        logger.debug(f"Condición del bucle mientras: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            self.reportar_error(
                "Se esperaba ':' después de la condición del bucle 'mientras'",
            )
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()
        else:
            self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            try:
                cuerpo.append(self.declaracion())
            except ParserError as e:
                logger.error(f"Error en el cuerpo del bucle 'mientras': {e}")
                self.reportar_error(f"Error en el cuerpo del bucle 'mientras': {e}")
                if self.token_actual().tipo != TipoToken.EOF:
                    self.avanzar()  # Avanza para evitar bloqueo

        if self.token_actual().tipo != TipoToken.FIN:
            self.reportar_error(
                "Se esperaba 'fin' para cerrar el bucle 'mientras'",
            )
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()
        else:
            self.comer(TipoToken.FIN)

        logger.debug(f"Cuerpo del bucle mientras: {cuerpo}")
        return NodoBucleMientras(condicion, cuerpo)

    def declaracion_holobit(self):
        """Parsea la creación de un objeto ``holobit``.

        Returns
        -------
        NodoHolobit
            Instancia que contiene los valores proporcionados.
        """
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
                raise ParserError(
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
            raise ParserError("Se esperaba ':' después de 'switch'")
        self.comer(TipoToken.DOSPUNTOS)

        casos = []
        while self.token_actual().tipo == TipoToken.CASE:
            self.comer(TipoToken.CASE)
            valor = self.expresion()
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise ParserError("Se esperaba ':' después de 'case'")
            self.comer(TipoToken.DOSPUNTOS)
            cuerpo = []
            while self.token_actual().tipo not in [
                TipoToken.CASE,
                TipoToken.SINO,
                TipoToken.FIN,
                TipoToken.EOF,
            ]:
                cuerpo.append(self.declaracion())
            casos.append(NodoCase(valor, cuerpo))

        bloque_defecto = []
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise ParserError("Se esperaba ':' después de 'sino'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                bloque_defecto.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError("Se esperaba 'fin' para cerrar el switch")
        self.comer(TipoToken.FIN)

        return NodoSwitch(expresion, casos, bloque_defecto)

    def declaracion_condicional(self):
        """Parsea un bloque condicional."""
        self.comer(TipoToken.SI)
        condicion = self.expresion()
        logger.debug(f"Condición del condicional: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            self.reportar_error("Se esperaba ':' después de la condición del 'si'")
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()
        else:
            self.comer(TipoToken.DOSPUNTOS)

        bloque_si = []
        while self.token_actual().tipo not in [
            TipoToken.SINO,
            TipoToken.FIN,
            TipoToken.EOF,
        ]:
            try:
                bloque_si.append(self.declaracion())
            except ParserError as e:
                logger.error(f"Error en el bloque 'si': {e}")
                self.reportar_error(f"Error en el bloque 'si': {e}")
                if self.token_actual().tipo != TipoToken.EOF:
                    self.avanzar()  # Evitar bloqueo en caso de error

        bloque_sino = []
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                self.reportar_error("Se esperaba ':' después del 'sino'")
                if self.token_actual().tipo != TipoToken.EOF:
                    self.avanzar()
            else:
                self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                try:
                    bloque_sino.append(self.declaracion())
                except ParserError as e:
                    logger.error(f"Error en el bloque 'sino': {e}")
                    self.reportar_error(f"Error en el bloque 'sino': {e}")
                    if self.token_actual().tipo != TipoToken.EOF:
                        self.avanzar()

        if self.token_actual().tipo != TipoToken.FIN:
            self.reportar_error("Se esperaba 'fin' para cerrar el bloque condicional")
            if self.token_actual().tipo != TipoToken.EOF:
                self.avanzar()
        else:
            self.comer(TipoToken.FIN)

        logger.debug(f"Bloque si: {bloque_si}, Bloque sino: {bloque_sino}")
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def declaracion_funcion(self, asincronica: bool = False):
        """Parsea una declaración de función."""
        self.comer(TipoToken.FUNC)

        # Captura el nombre de la función
        nombre_token = self.token_actual()
        if nombre_token.valor in PALABRAS_RESERVADAS:
            raise ParserError(
                f"El nombre de función '{nombre_token.valor}' es una palabra reservada"
            )
        if nombre_token.tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba un nombre para la función después de 'func'")
        nombre = nombre_token.valor
        self.comer(TipoToken.IDENTIFICADOR)

        # Parámetros de tipo genéricos opcionales
        type_params = self.lista_parametros_tipo()

        # Captura los parámetros
        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)

        # Verifica y consume ':'
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise ParserError("Se esperaba ':' después de la declaración de la función")
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
            except ParserError as e:
                logger.error(f"Error en el cuerpo de la función '{nombre}': {e}")
                self.avanzar()

        # Verifica y consume 'fin'
        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError(f"Se esperaba 'fin' para cerrar la función '{nombre}'")
        self.comer(TipoToken.FIN)

        logger.debug(f"Función '{nombre}' parseada con cuerpo: {cuerpo}")
        return NodoFuncion(nombre, parametros, cuerpo, asincronica=asincronica, type_params=type_params)

    def declaracion_imprimir(self):
        """Parsea una declaración de impresión."""
        self.comer(TipoToken.IMPRIMIR)  # Consume el token 'imprimir'

        # Si la siguiente parte comienza con paréntesis, se maneja como antes
        if self.token_actual().tipo == TipoToken.LPAREN:
            self.comer(TipoToken.LPAREN)
            expresion = self.expresion()
            if self.token_actual().tipo != TipoToken.RPAREN:
                raise ParserError(
                    "Se esperaba ')' al final de la instrucción 'imprimir'"
                )
            self.comer(TipoToken.RPAREN)
        else:
            # Sin paréntesis, se parsea la expresión directamente
            expresion = self.expresion()

        return NodoImprimir(expresion)

    def declaracion_import(self):
        """Parsea una declaración de importación de módulo."""
        self.comer(TipoToken.IMPORT)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise ParserError("Se esperaba una ruta de módulo entre comillas")
        ruta = self.token_actual().valor
        self.comer(TipoToken.CADENA)
        return NodoImport(ruta)

    def declaracion_usar(self):
        """Parsea una declaración 'usar' para importar módulos."""
        self.comer(TipoToken.USAR)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise ParserError("Se esperaba una ruta de módulo entre comillas")
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
            raise ParserError("Se esperaba el nombre de una función después de 'hilo'")
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
        """Parsea un bloque ``try/catch`` con soporte opcional de ``finally``.

        Returns
        -------
        NodoTryCatch
            Nodo que representa la estructura de manejo de excepciones.
        """
        if self.token_actual().tipo in (TipoToken.TRY, TipoToken.INTENTAR):
            self.avanzar()
        else:
            raise ParserError("Se esperaba 'try' o 'intentar'")
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise ParserError("Se esperaba ':' después de 'try'")
        self.comer(TipoToken.DOSPUNTOS)

        bloque_try = []
        while self.token_actual().tipo not in [
            TipoToken.CATCH,
            TipoToken.CAPTURAR,
            TipoToken.FIN,
            TipoToken.EOF,
        ]:
            bloque_try.append(self.declaracion())

        nombre_exc = None
        bloque_catch = []
        if self.token_actual().tipo in (TipoToken.CATCH, TipoToken.CAPTURAR):
            self.avanzar()
            if self.token_actual().tipo == TipoToken.IDENTIFICADOR:
                nombre_exc = self.token_actual().valor
                self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise ParserError("Se esperaba ':' después de 'catch/capturar'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [
                TipoToken.FIN,
                TipoToken.EOF,
                TipoToken.FINALMENTE,
            ]:
                bloque_catch.append(self.declaracion())

        bloque_finally = []
        if self.token_actual().tipo == TipoToken.FINALMENTE:
            self.comer(TipoToken.FINALMENTE)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise ParserError("Se esperaba ':' después de 'finalmente'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                bloque_finally.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError("Se esperaba 'fin' para cerrar el bloque try/catch")
        self.comer(TipoToken.FIN)

        return NodoTryCatch(bloque_try, nombre_exc, bloque_catch, bloque_finally)

    def declaracion_throw(self):
        """Parsea una declaración 'throw'."""
        if self.token_actual().tipo in (TipoToken.THROW, TipoToken.LANZAR):
            self.avanzar()
        else:
            raise ParserError("Se esperaba 'throw' o 'lanzar'")
        return NodoThrow(self.expresion())

    def declaracion_yield(self):
        """Parsea una expresión 'yield' dentro de una función generadora."""
        self.comer(TipoToken.YIELD)
        return NodoYield(self.expresion())

    def declaracion_asincronico(self):
        """Parsea una declaración comenzada con 'asincronico'."""
        self.comer(TipoToken.ASINCRONICO)
        if self.token_actual().tipo == TipoToken.FUNC:
            return self.declaracion_funcion(True)
        raise ParserError("Se esperaba 'func' después de 'asincronico'")

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
        """Parsea una sentencia ``afirmar`` (assert)."""
        self.comer(TipoToken.AFIRMAR)
        condicion = self.expresion()
        mensaje = None
        if self.token_actual().tipo == TipoToken.COMA:
            self.comer(TipoToken.COMA)
            mensaje = self.expresion()
        return NodoAssert(condicion, mensaje)

    def declaracion_eliminar(self):
        """Procesa la instrucción ``eliminar`` (del)."""
        self.comer(TipoToken.ELIMINAR)
        objetivo = self.expresion()
        return NodoDel(objetivo)

    def declaracion_global(self):
        """Registra nombres como variables globales."""
        self.comer(TipoToken.GLOBAL)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError(
                "Se esperaba al menos un identificador después de 'global'"
            )
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
        """Marca variables como no locales dentro de un cierre."""
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
        """Parsea el contexto ``con`` similar a ``with`` en Python."""
        self.comer(TipoToken.CON)
        contexto = self.expresion()
        alias = None
        if self.token_actual().tipo == TipoToken.COMO:
            self.comer(TipoToken.COMO)
            if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                raise ParserError("Se esperaba un identificador luego de 'como'")
            alias = self.token_actual().valor
            self.comer(TipoToken.IDENTIFICADOR)
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise ParserError("Se esperaba ':' después de 'con'")
        self.comer(TipoToken.DOSPUNTOS)
        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            cuerpo.append(self.declaracion())
        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError("Se esperaba 'fin' para cerrar el bloque 'con'")
        self.comer(TipoToken.FIN)
        return NodoWith(contexto, alias, cuerpo)

    def declaracion_desde(self):
        """Importa un símbolo específico desde un módulo."""
        self.comer(TipoToken.DESDE)
        if self.token_actual().tipo != TipoToken.CADENA:
            raise ParserError("Se esperaba una ruta de módulo entre comillas")
        modulo = self.token_actual().valor
        self.comer(TipoToken.CADENA)
        if self.token_actual().tipo != TipoToken.IMPORT:
            raise ParserError("Se esperaba 'import' después de 'desde'")
        self.comer(TipoToken.IMPORT)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba un nombre a importar")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        alias = None
        if self.token_actual().tipo == TipoToken.COMO:
            self.comer(TipoToken.COMO)
            if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                raise ParserError("Se esperaba un alias después de 'como'")
            alias = self.token_actual().valor
            self.comer(TipoToken.IDENTIFICADOR)
        return NodoImportDesde(modulo, nombre, alias)

    def declaracion_macro(self):
        """Parsea la definición de una macro simple."""
        self.comer(TipoToken.MACRO)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba un nombre de macro")
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
        cuerpo_parser = ClassicParser(cuerpo_tokens + [Token(TipoToken.EOF, None)])
        cuerpo = cuerpo_parser.parsear()
        return NodoMacro(nombre, cuerpo)

    def declaracion_metodo(self, asincronica: bool = False):
        """Parsea la declaración de un método dentro de una clase."""
        if self.token_actual().tipo == TipoToken.ASINCRONICO:
            self.comer(TipoToken.ASINCRONICO)
            asincronica = True
        if self.token_actual().tipo == TipoToken.METODO:
            self.comer(TipoToken.METODO)
        else:
            self.comer(TipoToken.FUNC)

        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba un nombre de método")
        nombre = self.token_actual().valor
        if nombre in PALABRAS_RESERVADAS:
            raise ParserError(
                f"El nombre del método '{nombre}' es una palabra reservada"
            )
        self.comer(TipoToken.IDENTIFICADOR)

        # Parámetros de tipo genéricos opcionales para el método
        type_params = self.lista_parametros_tipo()

        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)

        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise ParserError("Se esperaba ':' después de la cabecera del método")
        self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            cuerpo.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError("Se esperaba 'fin' para cerrar el método")
        self.comer(TipoToken.FIN)

        return NodoMetodo(nombre, parametros, cuerpo, asincronica=asincronica, type_params=type_params)

    def declaracion_clase(self):
        """Parsea la declaración de una clase."""
        self.comer(TipoToken.CLASE)

        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba un nombre de clase")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)

        # Parámetros de tipo genéricos opcionales para la clase
        type_params = self.lista_parametros_tipo()

        bases = []
        if self.token_actual().tipo == TipoToken.LPAREN:
            self.comer(TipoToken.LPAREN)
            while self.token_actual().tipo != TipoToken.RPAREN:
                if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                    raise ParserError("Se esperaba un nombre de clase base")
                bases.append(self.token_actual().valor)
                self.comer(TipoToken.IDENTIFICADOR)
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break
            self.comer(TipoToken.RPAREN)

        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise ParserError("Se esperaba ':' después del encabezado de la clase")
        self.comer(TipoToken.DOSPUNTOS)

        metodos = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            if self.token_actual().tipo in [
                TipoToken.FUNC,
                TipoToken.METODO,
                TipoToken.ASINCRONICO,
            ]:
                metodos.append(self.declaracion_metodo())
            else:
                metodos.append(self.declaracion())

        if self.token_actual().tipo != TipoToken.FIN:
            raise ParserError("Se esperaba 'fin' para cerrar la clase")
        self.comer(TipoToken.FIN)

        return NodoClase(nombre, metodos, bases, type_params=type_params)

    def expresion(self):
        """Entrada principal para evaluar expresiones."""
        return self.exp_or()

    def exp_or(self):
        """Evalúa expresiones unidas por el operador ``or``."""
        nodo = self.exp_and()
        while self.token_actual().tipo == TipoToken.OR:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_and()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_and(self):
        """Evalúa expresiones unidas por el operador ``and``."""
        nodo = self.exp_equality()
        while self.token_actual().tipo == TipoToken.AND:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_equality()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_equality(self):
        """Procesa comparaciones de igualdad y desigualdad."""
        nodo = self.exp_comparison()
        while self.token_actual().tipo in [TipoToken.IGUAL, TipoToken.DIFERENTE]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_comparison()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_comparison(self):
        """Evalúa operadores relacionales (<, <=, >, >=)."""
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
        """Resuelve sumas y restas en la expresión."""
        nodo = self.exp_multiplication()
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_multiplication()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_multiplication(self):
        """Maneja multiplicación, división y módulo."""
        nodo = self.exp_unario()
        while self.token_actual().tipo in [
            TipoToken.MULT,
            TipoToken.DIV,
            TipoToken.MOD,
        ]:
            operador = self.token_actual()
            self.avanzar()
            derecho = self.exp_unario()
            nodo = NodoOperacionBinaria(nodo, operador, derecho)
        return nodo

    def exp_unario(self):
        """Procesa operaciones unarias y espera."""
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
                raise ParserError("Se esperaba ':' en la expresión lambda")
            self.comer(TipoToken.DOSPUNTOS)
            cuerpo = self.expresion()
            return NodoLambda(parametros, cuerpo)
        elif token.tipo == TipoToken.ATRIBUTO:
            return self.exp_atributo()
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
            raise ParserError(f"Token inesperado en término: {token.tipo}")

    def exp_atributo(self):
        """Parsea la expresión 'atributo objeto nombre'."""
        self.comer(TipoToken.ATRIBUTO)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba el objeto del atributo")
        objeto = NodoIdentificador(self.token_actual().valor)
        self.comer(TipoToken.IDENTIFICADOR)
        if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
            raise ParserError("Se esperaba el nombre del atributo")
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        return NodoAtributo(objeto, nombre)

    def lista_parametros_tipo(self):
        """Parsea una lista de parámetros de tipo genéricos."""
        params = []
        if self.token_actual().tipo == TipoToken.MENORQUE:
            self.comer(TipoToken.MENORQUE)
            while self.token_actual().tipo != TipoToken.MAYORQUE:
                if self.token_actual().tipo != TipoToken.IDENTIFICADOR:
                    raise ParserError("Se esperaba un nombre de parámetro de tipo")
                params.append(self.token_actual().valor)
                self.comer(TipoToken.IDENTIFICADOR)
                if self.token_actual().tipo == TipoToken.COMA:
                    self.comer(TipoToken.COMA)
                else:
                    break
            if self.token_actual().tipo != TipoToken.MAYORQUE:
                raise ParserError("Se esperaba '>' para cerrar los parámetros de tipo")
            self.comer(TipoToken.MAYORQUE)
        return params

    def lista_parametros(self):
        """Devuelve la lista de parámetros de una función o lambda."""
        parametros = []
        while (
            self.token_actual().tipo == TipoToken.IDENTIFICADOR
            or self.token_actual().valor in PALABRAS_RESERVADAS
        ):
            nombre_parametro = self.token_actual().valor
            if nombre_parametro in PALABRAS_RESERVADAS:
                raise ParserError(
                    f"El nombre del parámetro '{nombre_parametro}' es una palabra reservada"
                )
            if nombre_parametro in parametros:
                raise ParserError(
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


# Permitir seleccionar un parser alternativo basado en Lark mediante la variable
# de entorno ``COBRA_PARSER``. Si su valor es ``"lark"`` se cargará
# ``LarkParser`` en lugar del parser clásico.

if os.getenv("COBRA_PARSER") == "lark":
    from cobra.parser.lark_parser import LarkParser

    Parser = LarkParser
else:
    Parser = ClassicParser


class ParserError(Exception):
    """Error personalizado lanzado por el parser de Cobra."""

    pass
