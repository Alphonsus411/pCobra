"""Transpilador sencillo de Cobra a Go."""

import re

from pcobra.core.ast_nodes import (
    NodoValor,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoAsignacion,
    NodoFuncion,
    NodoImprimir,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoAtributo,
    NodoLlamadaMetodo,
    NodoInstancia,
    NodoHolobit,
    NodoProyectar,
    NodoTransformar,
    NodoGraficar,
)
from pcobra.cobra.core.lexer import TipoToken
from pcobra.cobra.transpilers.common.utils import (
    BaseTranspiler,
    get_runtime_hooks,
    get_standard_imports,
)
from pcobra.core.optimizations import optimize_constants, remove_dead_code, inline_functions
from pcobra.cobra.macro import expandir_macros

from pcobra.cobra.transpilers.transpiler.go_nodes.asignacion import (
    visit_asignacion as _visit_asignacion,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.funcion import (
    visit_funcion as _visit_funcion,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.llamada_funcion import (
    visit_llamada_funcion as _visit_llamada_funcion,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.imprimir import (
    visit_imprimir as _visit_imprimir,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.condicional import (
    visit_condicional as _visit_condicional,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.bucle_mientras import (
    visit_bucle_mientras as _visit_bucle_mientras,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.for_ import visit_for as _visit_for
from pcobra.cobra.transpilers.transpiler.go_nodes.clase import visit_clase as _visit_clase
from pcobra.cobra.transpilers.transpiler.go_nodes.metodo import visit_metodo as _visit_metodo
from pcobra.cobra.transpilers.transpiler.go_nodes.retorno import (
    visit_retorno as _visit_retorno,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.romper import visit_romper as _visit_romper
from pcobra.cobra.transpilers.transpiler.go_nodes.continuar import (
    visit_continuar as _visit_continuar,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.llamada_metodo import (
    visit_llamada_metodo as _visit_llamada_metodo,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.instancia import (
    visit_instancia as _visit_instancia,
)



def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores or [])
    nombre = nodo.nombre or "_hb"
    self.agregar_linea(f"{nombre} := []float64{{{valores}}}")


def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraProyectar({hb}, {modo})")


def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    args = f", {params}" if params else ""
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraTransformar({hb}, {op}{args})")


def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.usa_runtime_holobit = True
    self.agregar_linea(f"cobraGraficar({hb})")

go_nodes = {
    "asignacion": _visit_asignacion,
    "funcion": _visit_funcion,
    "llamada_funcion": _visit_llamada_funcion,
    "imprimir": _visit_imprimir,
    "condicional": _visit_condicional,
    "bucle_mientras": _visit_bucle_mientras,
    "for": _visit_for,
    "clase": _visit_clase,
    "metodo": _visit_metodo,
    "retorno": _visit_retorno,
    "romper": _visit_romper,
    "continuar": _visit_continuar,
    "llamada_metodo": _visit_llamada_metodo,
    "instancia": _visit_instancia,
    "holobit": visit_holobit,
    "proyectar": visit_proyectar,
    "transformar": visit_transformar,
    "graficar": visit_graficar,
}


class TranspiladorGo(BaseTranspiler):
    def __init__(self):
        self.codigo = []
        self.indent = 0
        self.imports: set[str] = set()
        self.usa_runtime_holobit = False

    def agregar_import(self, nombre: str) -> None:
        """Registra un paquete para importar."""
        self.imports.add(nombre)

    def agregar_linea(self, linea: str) -> None:
        self.codigo.append("    " * self.indent + linea)

    def generate_code(self, ast):
        self.codigo = []
        self.imports = set()
        self.usa_runtime_holobit = False

        nodos = expandir_macros(ast)

        cuerpo_principal = []
        tiene_principal = False
        for nodo in nodos:
            nombre = re.sub(r"(?<!^)(?=[A-Z])", "_", nodo.__class__.__name__[4:]).lower()
            metodo = getattr(self, f"visit_{nombre}", None)
            if not metodo:
                continue
            if isinstance(nodo, NodoFuncion):
                metodo(nodo)
                if getattr(nodo, "nombre", "") == "principal":
                    tiene_principal = True
            else:
                cuerpo_principal.append((metodo, nodo))

        if cuerpo_principal or tiene_principal:
            self.agregar_linea("func main() {")
            self.indent += 1
            for metodo, nodo in cuerpo_principal:
                metodo(nodo)
            if not cuerpo_principal and tiene_principal:
                self.agregar_linea("principal()")
            self.indent -= 1
            self.agregar_linea("}")

        codigo = "\n".join(self.codigo)

        imports = set(get_standard_imports("go"))
        imports.update(self.imports)
        if self.usa_runtime_holobit:
            imports.add("fmt")

        encabezado = "package main\n"
        if imports:
            encabezado += "\nimport (\n"
            for imp in sorted(imports):
                encabezado += f'    "{imp}"\n'
            encabezado += ")\n\n"
        else:
            encabezado += "\n"

        if self.usa_runtime_holobit:
            hooks = "\n".join(get_runtime_hooks("go"))
            if hooks:
                hooks += "\n\n"
            return encabezado + hooks + codigo

        return encabezado + codigo
    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            if isinstance(nodo.valor, str):
                return f'"{nodo.valor}"'
            return str(nodo.valor)
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}.{nodo.nombre}"
        elif isinstance(nodo, NodoLlamadaFuncion):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{nodo.nombre}({args})"
        elif isinstance(nodo, NodoLlamadaMetodo):
            obj = self.obtener_valor(nodo.objeto)
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"{obj}.{nodo.nombre_metodo}({args})"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"&{nodo.nombre_clase}{{{args}}}"
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            op_map = {TipoToken.AND: "&&", TipoToken.OR: "||"}
            op = op_map.get(nodo.operador.tipo, nodo.operador.valor)
            return f"{izq} {op} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            op = "!" if nodo.operador.tipo == TipoToken.NOT else nodo.operador.valor
            return f"{op}{val}" if op != "!" else f"!{val}"
        else:
            return str(getattr(nodo, "valor", nodo))

# Asignar visitantes
for nombre, funcion in go_nodes.items():
    setattr(TranspiladorGo, f"visit_{nombre}", funcion)
