"""Transpilador muy básico que genera código WebAssembly en formato WAT."""

from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoOperacionBinaria,
    NodoRetorno,
    NodoValor,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
)
from pcobra.cobra.core import TipoToken
from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.common.utils import BaseTranspiler, get_runtime_hooks
from pcobra.core.optimizations import optimize_constants, remove_dead_code
from pcobra.cobra.macro import expandir_macros


class TranspiladorWasm(BaseTranspiler):
    """Transpila el AST de Cobra a WebAssembly (WAT) de forma sencilla."""

    def __init__(self):
        self.codigo = []
        self.indent = 0
        self.usa_runtime_holobit = False

    def generate_code(self, ast):
        self.codigo = self.transpilar(ast)
        return self.codigo

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor) or isinstance(nodo, int):
            valor = nodo.valor if hasattr(nodo, "valor") else nodo
            return f"(i32.const {valor})"
        elif isinstance(nodo, NodoIdentificador):
            return f"(local.get ${nodo.nombre})"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {
                TipoToken.SUMA: "i32.add",
                TipoToken.RESTA: "i32.sub",
                TipoToken.MULT: "i32.mul",
                TipoToken.DIV: "i32.div_s",
            }
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"({op} {izq} {der})"
        else:
            return str(getattr(nodo, "valor", nodo))

    def visit_asignacion(self, nodo: NodoAsignacion):
        nombre = getattr(nodo, "identificador", nodo.variable)
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"(local.set ${nombre} {valor})")

    def visit_funcion(self, nodo: NodoFuncion):
        params = " ".join(f"(param ${p} i32)" for p in nodo.parametros)
        self.agregar_linea(f"(func ${nodo.nombre} {params}")
        self.indent += 1
        for inst in nodo.cuerpo:
            inst.aceptar(self)
        self.indent -= 1
        self.agregar_linea(")")

    def visit_retorno(self, nodo: NodoRetorno):
        valor = self.obtener_valor(nodo.expresion) if nodo.expresion else ""
        if valor:
            self.agregar_linea(f"(return {valor})")
        else:
            self.agregar_linea("(return)")


    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
        self.agregar_linea(f";; call {nodo.nombre} {args}")

    def visit_holobit(self, nodo: NodoHolobit):
        nombre = nodo.nombre or "hb"
        valores = ", ".join(str(v) for v in nodo.valores or [])
        self.agregar_linea(f";; holobit {nombre} [{valores}]")

    def visit_proyectar(self, nodo: NodoProyectar):
        self.usa_runtime_holobit = True
        self.agregar_linea(";; call runtime cobra_proyectar")

    def visit_transformar(self, nodo: NodoTransformar):
        self.usa_runtime_holobit = True
        self.agregar_linea(";; call runtime cobra_transformar")

    def visit_graficar(self, nodo: NodoGraficar):
        self.usa_runtime_holobit = True
        self.agregar_linea(";; call runtime cobra_graficar")

    def transpilar(self, nodos):
        nodos = expandir_macros(nodos)
        # Evitamos el uso de ``inline_functions`` para no eliminar funciones
        # sencillas (como ``main``) que no tengan llamadas directas.
        nodos = remove_dead_code(optimize_constants(nodos))
        self.usa_runtime_holobit = False
        for nodo in nodos:
            nodo.aceptar(self)
        if self.usa_runtime_holobit:
            hooks = get_runtime_hooks("wasm")
            if hooks:
                self.codigo = hooks + self.codigo
        return "\n".join(self.codigo)
