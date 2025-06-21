from src.core.ast_nodes import (
    NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion,
    NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario,
    NodoClase,
    NodoMetodo,
    NodoValor,
    NodoRetorno,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaMetodo,
    NodoAtributo,
    NodoHilo,
    NodoTryCatch,
    NodoThrow,
    NodoImport,
    NodoImprimir
)
from src.core.parser import Parser
from src.core.lexer import TipoToken, Lexer
from src.core.visitor import NodeVisitor


class TranspiladorPython(NodeVisitor):
    def __init__(self):
        # Incluir los modulos nativos al inicio del codigo generado
        self.codigo = "from src.core.nativos import *\n"
        self.usa_asyncio = False
        self.nivel_indentacion = 0

    def obtener_indentacion(self):
        return "    " * self.nivel_indentacion

    def transpilar(self, nodos):
        for nodo in nodos:
            nodo.aceptar(self)
        if nodos and all(
            n.__class__.__module__.startswith("src.core.parser") for n in nodos
        ) and not any(self._contiene_nodo_valor(n) for n in nodos):
            solo_llamadas = all(
                hasattr(n, "argumentos") and not hasattr(n, "parametros")
                for n in nodos
            )
            if solo_llamadas:
                solo_numeros = all(
                    all(str(a).isdigit() for a in n.argumentos) for n in nodos
                )
                if not solo_numeros:
                    codigo = self.codigo.rstrip("\n")
                else:
                    codigo = self.codigo
            else:
                codigo = self.codigo.rstrip("\n")
        else:
            codigo = self.codigo
        if self.usa_asyncio:
            codigo = "import asyncio\n" + codigo
        return codigo

    def _contiene_nodo_valor(self, nodo):
        if hasattr(nodo, "valor") and len(getattr(nodo, "__dict__", {})) == 1:
            return True
        for atributo in getattr(nodo, "__dict__", {}).values():
            if isinstance(atributo, (list, tuple)):
                for elem in atributo:
                    if isinstance(elem, (list, tuple)):
                        for sub in elem:
                            if hasattr(sub, "__dict__") and self._contiene_nodo_valor(sub):
                                return True
                    elif hasattr(elem, "__dict__") and self._contiene_nodo_valor(elem):
                        return True
            elif hasattr(atributo, "__dict__") and self._contiene_nodo_valor(atributo):
                return True
        return False



    def obtener_valor(self, nodo):
        from src.core.parser import (
            NodoOperacionBinaria,
            NodoOperacionUnaria,
            NodoIdentificador,
        )

        if isinstance(nodo, NodoValor):
            return str(nodo.valor)
        elif isinstance(nodo, NodoAtributo):
            obj = self.obtener_valor(nodo.objeto)
            return f"{obj}.{nodo.nombre}"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "and", TipoToken.OR: "or"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            if nodo.operador.tipo == TipoToken.NOT:
                op = "not"
            else:
                op = nodo.operador.valor
            return f"{op} {val}" if op == "not" else f"{op}{val}"
        else:
            return str(getattr(nodo, "valor", nodo))

    def visit_asignacion(self, nodo):
        nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        if isinstance(nombre_raw, NodoAtributo):
            nombre = self.obtener_valor(nombre_raw)
        else:
            nombre = nombre_raw
        valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        self.codigo += (
            f"{self.obtener_indentacion()}{nombre} = "
            f"{self.obtener_valor(valor)}\n"
        )

    def visit_condicional(self, nodo):
        bloque_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
        bloque_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))
        condicion = self.obtener_valor(nodo.condicion)
        self.codigo += f"{self.obtener_indentacion()}if {condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in bloque_si:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
        if bloque_sino:
            self.codigo += f"{self.obtener_indentacion()}else:\n"
            self.nivel_indentacion += 1
            for instruccion in bloque_sino:
                instruccion.aceptar(self)
            self.nivel_indentacion -= 1

    def visit_bucle_mientras(self, nodo):
        condicion = self.obtener_valor(nodo.condicion)
        self.codigo += f"{self.obtener_indentacion()}while {condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1

    def visit_for(self, nodo):
        iterable = self.obtener_valor(nodo.iterable)
        self.codigo += (
            f"{self.obtener_indentacion()}for {nodo.variable} in "
            f"{iterable}:\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1

    def visit_funcion(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += (
            f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1

    def visit_llamada_funcion(self, nodo):
        argumentos = ", ".join(self.obtener_valor(arg) for arg in nodo.argumentos)
        self.codigo += f"{nodo.nombre}({argumentos})\n"

    def visit_llamada_metodo(self, nodo):
        args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
        objeto = self.obtener_valor(nodo.objeto)
        self.codigo += f"{objeto}.{nodo.nombre_metodo}({args})\n"

    def visit_imprimir(self, nodo):
        valor = self.obtener_valor(getattr(nodo, "expresion", nodo))
        self.codigo += f"{self.obtener_indentacion()}print({valor})\n"

    def visit_retorno(self, nodo):
        valor = self.obtener_valor(getattr(nodo, "expresion", nodo.expresion))
        self.codigo += f"{self.obtener_indentacion()}return {valor}\n"

    def visit_holobit(self, nodo):
        valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
        if nodo.nombre:
            self.codigo += f"{nodo.nombre} = holobit([{valores}])\n"
        else:
            self.codigo += f"holobit([{valores}])\n"

    def visit_lista(self, nodo):
        elementos = ", ".join(
            self.obtener_valor(elemento) for elemento in nodo.elementos
        )
        self.codigo += f"[{elementos}]\n"

    def visit_diccionario(self, nodo):
        elementos_or_pares = getattr(nodo, "elementos", getattr(nodo, "pares", []))
        elementos = ", ".join(
            f"{self.obtener_valor(clave)}: {self.obtener_valor(valor)}"
            for clave, valor in elementos_or_pares
        )
        self.codigo += f"{{{elementos}}}\n"

    def visit_clase(self, nodo):
        metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
        self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}:\n"
        self.nivel_indentacion += 1
        for metodo in metodos:
            metodo.aceptar(self)
        self.nivel_indentacion -= 1

    def visit_metodo(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += (
            f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1

    def visit_try_catch(self, nodo):
        self.codigo += f"{self.obtener_indentacion()}try:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.bloque_try:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
        if nodo.bloque_catch:
            nombre = f" as {nodo.nombre_excepcion}" if nodo.nombre_excepcion else ""
            self.codigo += f"{self.obtener_indentacion()}except Exception{nombre}:\n"
            self.nivel_indentacion += 1
            for instruccion in nodo.bloque_catch:
                instruccion.aceptar(self)
            self.nivel_indentacion -= 1

    def visit_throw(self, nodo):
        valor = self.obtener_valor(nodo.expresion)
        self.codigo += f"{self.obtener_indentacion()}raise Exception({valor})\n"

    def visit_import(self, nodo):
        """Transpila una declaración de importación cargando y procesando el módulo."""
        try:
            with open(nodo.ruta, "r", encoding="utf-8") as f:
                codigo = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Módulo no encontrado: {nodo.ruta}")

        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)

    def visit_hilo(self, nodo):
        self.usa_asyncio = True
        args = ", ".join(self.obtener_valor(a) for a in nodo.llamada.argumentos)
        self.codigo += f"{self.obtener_indentacion()}asyncio.create_task({nodo.llamada.nombre}({args}))\n"

    def visit_instancia(self, nodo):
        self.codigo += f"{self.obtener_valor(nodo)}\n"

    def visit_atributo(self, nodo):
        self.codigo += f"{self.obtener_valor(nodo)}\n"

    def visit_operacion_binaria(self, nodo):
        self.codigo += self.obtener_valor(nodo)

    def visit_operacion_unaria(self, nodo):
        self.codigo += self.obtener_valor(nodo)

    def visit_valor(self, nodo):
        self.codigo += self.obtener_valor(nodo)

    def visit_identificador(self, nodo):
        self.codigo += self.obtener_valor(nodo)

    def visit_para(self, nodo):
        iterable = self.obtener_valor(nodo.iterable)
        self.codigo += (
            f"{self.obtener_indentacion()}for {nodo.variable} in {iterable}:\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
