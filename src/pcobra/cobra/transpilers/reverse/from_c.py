# -*- coding: utf-8 -*-
"""Transpilador inverso desde C a Cobra usando tree-sitter.

Este módulo implementa la conversión de código C a nodos AST de Cobra
utilizando el parser tree-sitter. Soporta las principales construcciones
del lenguaje C incluyendo:

- Tipos básicos y estructuras
- Declaraciones de funciones y variables 
- Expresiones y operadores
- Control de flujo (if, while, for, etc.)
- Directivas de preprocesador básicas

Ejemplos:
    Uso básico del transpilador:

    >>> from pcobra.cobra.transpilers.reverse.from_c import ReverseFromC
    >>> transpiler = ReverseFromC()
    >>> ast = transpiler.generate_ast("int main() { return 0; }")

Nota:
    Requiere que el parser tree-sitter para C esté instalado y configurado.
"""

from typing import Any, List, Optional

from pcobra.cobra.core.ast_nodes import (
    NodoBloque,
    NodoDeclaracion,
    NodoExpresion,
    NodoFuncion,
    NodoIdentificador,
    NodoRetorno,
    NodoTipo,
    NodoValor
)
from pcobra.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromC(TreeSitterReverseTranspiler):
    """Transpilador inverso de C a Cobra usando tree-sitter.
    
    Este transpilador convierte código fuente C en nodos AST de Cobra,
    manteniendo la semántica del código original tanto como sea posible.
    
    Attributes:
        LANGUAGE (str): Identificador del lenguaje para tree-sitter
    """
    
    LANGUAGE = "c"

    def visit_function_definition(self, node: Any) -> NodoFuncion:
        """Procesa una definición de función C.
        
        Args:
            node: Nodo tree-sitter de definición de función
            
        Returns:
            NodoFuncion: Nodo AST Cobra equivalente
        """
        nombre = node.child_by_field_name("declarator")
        params = node.child_by_field_name("parameters")
        cuerpo = node.child_by_field_name("body")
        
        nombre_func = self.visit(nombre) if nombre else NodoIdentificador("")
        params_lista = []
        if params:
            for p in params.children:
                if p.is_named:
                    params_lista.append(self.visit(p))
                    
        cuerpo_lista = []
        if cuerpo:
            for stmt in cuerpo.children:
                if stmt.is_named:
                    cuerpo_lista.append(self.visit(stmt))
                    
        return NodoFuncion(
            nombre=nombre_func.nombre,
            parametros=params_lista,
            cuerpo=cuerpo_lista
        )

    def visit_parameter_declaration(self, node: Any) -> NodoDeclaracion:
        """Procesa una declaración de parámetro.
        
        Args:
            node: Nodo tree-sitter de parámetro
            
        Returns:
            NodoDeclaracion: Nodo AST Cobra equivalente
        """
        tipo = node.child_by_field_name("type")
        nombre = node.child_by_field_name("declarator")
        
        tipo_nodo = self.visit(tipo) if tipo else NodoTipo("void")
        nombre_nodo = self.visit(nombre) if nombre else NodoIdentificador("")
        
        return NodoDeclaracion(
            nombre=nombre_nodo.nombre,
            tipo=tipo_nodo
        )

    def visit_compound_statement(self, node: Any) -> NodoBloque:
        """Procesa un bloque de código.
        
        Args:
            node: Nodo tree-sitter de bloque
            
        Returns:
            NodoBloque: Nodo AST Cobra equivalente
        """
        sentencias = []
        for child in node.children:
            if child.is_named:
                sentencias.append(self.visit(child))
        return NodoBloque(sentencias)

    def visit_return_statement(self, node: Any) -> NodoRetorno:
        """Procesa una sentencia return.
        
        Args:
            node: Nodo tree-sitter de return
            
        Returns:
            NodoRetorno: Nodo AST Cobra equivalente
        """
        valor = node.child_by_field_name("value")
        return NodoRetorno(
            self.visit(valor) if valor else NodoValor(None)
        )

    def visit_expression_statement(self, node: Any) -> NodoExpresion:
        """Procesa una expresión.
        
        Args:
            node: Nodo tree-sitter de expresión
            
        Returns:
            NodoExpresion: Nodo AST Cobra equivalente
        """
        expr = node.child_by_field_name("expression")
        return self.visit(expr) if expr else NodoExpresion([])

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código C.
        
        Args:
            code: Código fuente en C
            
        Returns:
            List[Any]: Lista de nodos AST de Cobra
            
        Raises:
            ValueError: Si el código C es inválido
            NotImplementedError: Si se encuentra una construcción no soportada
        """
        try:
            return super().generate_ast(code)
        except Exception as e:
            raise ValueError(f"Error procesando código C: {str(e)}") from e