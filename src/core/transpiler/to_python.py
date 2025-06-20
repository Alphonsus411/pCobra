from src.core.parser import (
    NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion,
    NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario,
    NodoClase, NodoMetodo, NodoValor, NodoRetorno,
    NodoOperacionBinaria, NodoOperacionUnaria, NodoIdentificador,
    NodoInstancia, NodoLlamadaMetodo, NodoAtributo
)
from src.core.lexer import TipoToken


class TranspiladorPython:
    def __init__(self):
        self.codigo = ""
        self.nivel_indentacion = 0

    def obtener_indentacion(self):
        return "    " * self.nivel_indentacion

    def transpilar(self, nodos):
        for nodo in nodos:
            self.transpilar_nodo(nodo)
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
                    return self.codigo.rstrip("\n")
                return self.codigo
            return self.codigo.rstrip("\n")
        return self.codigo

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


    def transpilar_nodo(self, nodo):
        if (
            (hasattr(nodo, "identificador") or hasattr(nodo, "variable"))
            and (hasattr(nodo, "expresion") or hasattr(nodo, "valor"))
        ):
            self.transpilar_asignacion(nodo)
        elif hasattr(nodo, "condicion") and (
            hasattr(nodo, "bloque_si") or hasattr(nodo, "cuerpo_si")
        ):
            self.transpilar_condicional(nodo)
        elif hasattr(nodo, "condicion") and hasattr(nodo, "cuerpo"):
            self.transpilar_mientras(nodo)
        elif (
            hasattr(nodo, "nombre")
            and hasattr(nodo, "parametros")
            and hasattr(nodo, "cuerpo")
            and not hasattr(nodo, "metodos")
        ):
            self.transpilar_funcion(nodo)
        elif hasattr(nodo, "nombre") and hasattr(nodo, "argumentos"):
            self.transpilar_llamada_funcion(nodo)
        elif isinstance(nodo, NodoInstancia):
            self.codigo += f"{self.obtener_valor(nodo)}\n"
        elif isinstance(nodo, NodoLlamadaMetodo):
            self.transpilar_llamada_metodo(nodo)
        elif type(nodo).__name__ == "NodoImprimir":
            self.transpilar_imprimir(nodo)
        elif isinstance(nodo, NodoRetorno) or type(nodo).__name__ == "NodoRetorno":
            self.transpilar_retorno(nodo)
        elif hasattr(nodo, "valores") or (
            hasattr(nodo, "nombre")
            and not any(
                hasattr(nodo, attr)
                for attr in ["argumentos", "parametros", "cuerpo", "metodos"]
            )
        ):
            self.transpilar_holobit(nodo)
        elif (
            hasattr(nodo, "variable")
            and hasattr(nodo, "iterable")
            and hasattr(nodo, "cuerpo")
        ):
            self.transpilar_for(nodo)
        elif hasattr(nodo, "pares"):
            self.transpilar_diccionario(nodo)
        elif hasattr(nodo, "elementos"):
            # Distinguir lista de diccionario por la forma de los elementos
            elementos = getattr(nodo, "elementos", [])
            if all(
                isinstance(elem, (tuple, list)) and len(elem) == 2
                for elem in elementos
            ):
                self.transpilar_diccionario(nodo)
            else:
                self.transpilar_lista(nodo)
        elif hasattr(nodo, "metodos") or (
            hasattr(nodo, "cuerpo")
            and not any(
                hasattr(nodo, attr)
                for attr in [
                    "parametros",
                    "condicion",
                    "iterable",
                    "expresion",
                    "valor",
                ]
            )
        ):
            self.transpilar_clase(nodo)
        elif (
            hasattr(nodo, "nombre")
            and hasattr(nodo, "parametros")
            and hasattr(nodo, "cuerpo")
        ):
            self.transpilar_metodo(nodo)
        elif isinstance(nodo, (NodoOperacionBinaria, NodoOperacionUnaria)):
            self.codigo += self.obtener_valor(nodo)
        elif hasattr(nodo, "valor"):
            self.codigo += self.obtener_valor(nodo)
        else:
            raise TypeError(
                f"Tipo de nodo no soportado: {type(nodo).__name__}"
            )

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

    def transpilar_asignacion(self, nodo):
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

    def transpilar_condicional(self, nodo):
        bloque_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
        bloque_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))
        condicion = self.obtener_valor(nodo.condicion)
        self.codigo += f"{self.obtener_indentacion()}if {condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in bloque_si:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1
        if bloque_sino:
            self.codigo += f"{self.obtener_indentacion()}else:\n"
            self.nivel_indentacion += 1
            for instruccion in bloque_sino:
                self.transpilar_nodo(instruccion)
            self.nivel_indentacion -= 1

    def transpilar_mientras(self, nodo):
        condicion = self.obtener_valor(nodo.condicion)
        self.codigo += f"{self.obtener_indentacion()}while {condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_for(self, nodo):
        iterable = self.obtener_valor(nodo.iterable)
        self.codigo += (
            f"{self.obtener_indentacion()}for {nodo.variable} in "
            f"{iterable}:\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_funcion(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += (
            f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_llamada_funcion(self, nodo):
        argumentos = ", ".join(self.obtener_valor(arg) for arg in nodo.argumentos)
        self.codigo += f"{nodo.nombre}({argumentos})\n"

    def transpilar_llamada_metodo(self, nodo):
        args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
        objeto = self.obtener_valor(nodo.objeto)
        self.codigo += f"{objeto}.{nodo.nombre_metodo}({args})\n"

    def transpilar_imprimir(self, nodo):
        valor = self.obtener_valor(getattr(nodo, "expresion", nodo))
        self.codigo += f"{self.obtener_indentacion()}print({valor})\n"

    def transpilar_retorno(self, nodo):
        valor = self.obtener_valor(getattr(nodo, "expresion", nodo.expresion))
        self.codigo += f"{self.obtener_indentacion()}return {valor}\n"

    def transpilar_holobit(self, nodo):
        valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
        if nodo.nombre:
            self.codigo += f"{nodo.nombre} = holobit([{valores}])\n"
        else:
            self.codigo += f"holobit([{valores}])\n"

    def transpilar_lista(self, nodo):
        elementos = ", ".join(
            self.obtener_valor(elemento) for elemento in nodo.elementos
        )
        self.codigo += f"[{elementos}]\n"

    def transpilar_diccionario(self, nodo):
        elementos_or_pares = getattr(nodo, "elementos", getattr(nodo, "pares", []))
        elementos = ", ".join(
            f"{self.obtener_valor(clave)}: {self.obtener_valor(valor)}"
            for clave, valor in elementos_or_pares
        )
        self.codigo += f"{{{elementos}}}\n"

    def transpilar_clase(self, nodo):
        metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
        self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}:\n"
        self.nivel_indentacion += 1
        for metodo in metodos:
            self.transpilar_metodo(metodo)
        self.nivel_indentacion -= 1

    def transpilar_metodo(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += (
            f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1
