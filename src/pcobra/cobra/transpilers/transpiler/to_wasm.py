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
from pcobra.cobra.transpilers.common.utils import (
    BaseTranspiler,
    get_runtime_hooks,
    get_standard_imports,
)
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
            if isinstance(valor, str):
                return "(i32.const 0)"
            if valor is None:
                return "(i32.const 0)"
            if isinstance(valor, bool):
                return f"(i32.const {1 if valor else 0})"
            return f"(i32.const {valor})"
        elif isinstance(nodo, NodoHolobit):
            primer_valor = nodo.valores[0] if nodo.valores else 0
            self.usa_runtime_holobit = True
            return f"(call $cobra_holobit {self._obtener_i32(primer_valor, 'holobit.expr')})"
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

    def _obtener_i32(self, nodo, contexto: str) -> str:
        valor = self.obtener_valor(nodo)
        if isinstance(valor, str) and valor.startswith("(") and valor.endswith(")"):
            return valor
        raise RuntimeError(
            "WASM_CONTRACT_ERROR: lowering i32 no soportado; "
            f"contexto={contexto}; nodo={type(nodo).__name__}"
        )

    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion):
        args = " ".join(self._obtener_i32(a, "llamada_funcion") for a in nodo.argumentos)
        sufijo = f" {args}" if args else ""
        self.agregar_linea(f"(call ${nodo.nombre}{sufijo})")

    def visit_holobit(self, nodo: NodoHolobit):
        self.usa_runtime_holobit = True
        primer_valor = nodo.valores[0] if nodo.valores else 0
        self.agregar_linea(
            f"(drop (call $cobra_holobit {self._obtener_i32(primer_valor, 'holobit')}))"
        )

    def visit_proyectar(self, nodo: NodoProyectar):
        self.usa_runtime_holobit = True
        hb = self._obtener_i32(nodo.holobit, "proyectar.holobit")
        modo = self._obtener_i32(nodo.modo, "proyectar.modo")
        self.agregar_linea(f"(drop (call $cobra_proyectar {hb} {modo}))")

    def visit_transformar(self, nodo: NodoTransformar):
        self.usa_runtime_holobit = True
        hb = self._obtener_i32(nodo.holobit, "transformar.holobit")
        op = self._obtener_i32(nodo.operacion, "transformar.operacion")
        params_len = len(getattr(nodo, 'parametros', []))
        self.agregar_linea(
            f"(drop (call $cobra_transformar {hb} {op} (i32.const {params_len})))"
        )

    def visit_graficar(self, nodo: NodoGraficar):
        self.usa_runtime_holobit = True
        hb = self._obtener_i32(nodo.holobit, "graficar.holobit")
        self.agregar_linea(f"(drop (call $cobra_graficar {hb}))")

    def transpilar(self, nodos):
        self.codigo = list(get_standard_imports("wasm"))
        if self.codigo:
            self.codigo.append("")
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
                self.codigo = hooks + [""] + self.codigo
        return "\n".join(self.codigo)
