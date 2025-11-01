"""Analizador semántico que construye la tabla de símbolos y verifica errores."""

from __future__ import annotations

import os
from typing import List, Optional, Any, Set

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoFuncion,
    NodoIdentificador,
    NodoMetodo,
    NodoGarantia,
    NodoRetorno,
    NodoThrow,
    NodoContinuar,
    NodoRomper,
    NodoCondicional,
    NodoImport,
)
from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.semantico.tabla import Ambito
from pcobra.core.import_utils import obtener_simbolos_modulo


class AnalizadorSemantico(NodeVisitor):
    """Analiza el AST para construir y validar la tabla de símbolos."""

    def __init__(self):
        """Inicializa el analizador con un ámbito global."""
        self.global_scope = Ambito()
        self.current_scope = self.global_scope
        self.herencia: dict[str, List[str]] = {}
        self._import_cache: dict[str, Set[tuple[str, str]]] = {}

    def analizar(self, ast: List) -> None:
        """Analiza el AST completo visitando cada nodo.

        Args:
            ast: Lista de nodos del AST a analizar
        """
        for nodo in ast:
            nodo.aceptar(self)

    def _simbolos_importados(self, ruta: str) -> Set[tuple[str, str]]:
        """Obtiene y memoriza los símbolos declarados en un módulo importado."""

        ruta_abs = os.path.abspath(ruta)
        ruta_real = os.path.realpath(ruta_abs)
        cache_key = ruta_real
        if cache_key not in self._import_cache:
            try:
                self._sincronizar_config_import()
                simbolos = obtener_simbolos_modulo(ruta)
            except FileNotFoundError as exc:
                raise FileNotFoundError(f"Módulo no encontrado: {ruta}") from exc
            except PermissionError as exc:
                raise ImportError(str(exc)) from exc
            except Exception as exc:
                raise ImportError(
                    f"Error al analizar el módulo importado '{ruta}': {exc}"
                ) from exc
            self._import_cache[cache_key] = simbolos
        return self._import_cache[cache_key]

    def _sincronizar_config_import(self) -> None:
        """Alinea la configuración compartida de importaciones con el intérprete."""

        try:
            from pcobra.core import interpreter as _interpreter
        except Exception:  # pragma: no cover - importación opcional
            return

        sincronizar = getattr(_interpreter, "_sincronizar_config_import", None)
        if callable(sincronizar):
            sincronizar()

    # Utilidades ---------------------------------------------------------
    def _con_nuevo_ambito(self) -> Ambito:
        """Crea y establece un nuevo ámbito anidado.

        Returns:
            El nuevo ámbito creado
        """
        nuevo = Ambito(self.current_scope)
        self.current_scope = nuevo
        return nuevo

    def _salir_ambito(self) -> Optional[Ambito]:
        """Sale del ámbito actual al ámbito padre.
        
        Returns:
            El ámbito padre o None si ya estamos en el ámbito global
        """
        if self.current_scope.padre is not None:
            anterior = self.current_scope
            self.current_scope = self.current_scope.padre
            return anterior
        return None

    def _validar_parametros(self, parametros: List[str]) -> None:
        """Valida que no haya parámetros duplicados.
        
        Args:
            parametros: Lista de nombres de parámetros
            
        Raises:
            ValueError: Si hay parámetros duplicados
        """
        vistos = set()
        for param in parametros:
            if param in vistos:
                raise ValueError(f"Parámetro duplicado: {param}")
            vistos.add(param)

    def _validar_nombre(self, nombre: Any) -> None:
        """Valida que el nombre sea una cadena válida.
        
        Args:
            nombre: Nombre a validar
            
        Raises:
            TypeError: Si el nombre no es una cadena
        """
        if not isinstance(nombre, str):
            raise TypeError(f"El nombre debe ser string, no {type(nombre)}")

    def _procesar_bloque_codigo(self, parametros: List[str], cuerpo: List[Any]) -> None:
        """Procesa un bloque de código (función o método).
        
        Args:
            parametros: Lista de parámetros
            cuerpo: Lista de instrucciones
        """
        self._validar_parametros(parametros)
        self._con_nuevo_ambito()
        try:
            for param in parametros:
                self.current_scope.declarar(param, "variable")
            for instruccion in cuerpo:
                instruccion.aceptar(self)
        finally:
            self._salir_ambito()

    def _hay_camino(self, origen: str, destino: str, visitados: Optional[Set[str]] = None) -> bool:
        """Verifica si existe un camino de herencia entre dos clases."""
        if visitados is None:
            visitados = set()
        if origen == destino:
            return True
        if origen in visitados:
            return False
        visitados.add(origen)
        for base in self.herencia.get(origen, []):
            if self._hay_camino(base, destino, visitados):
                return True
        return False

    def _bloque_termina(self, bloque: List[Any]) -> bool:
        if not bloque:
            return False
        terminadores = (NodoRetorno, NodoThrow, NodoContinuar, NodoRomper)
        ultimo = bloque[-1]
        if isinstance(ultimo, terminadores):
            return True
        if isinstance(ultimo, NodoCondicional):
            if not ultimo.bloque_sino:
                return False
            return self._bloque_termina(ultimo.bloque_si) and self._bloque_termina(
                ultimo.bloque_sino
            )
        if isinstance(ultimo, NodoGarantia):
            return self._bloque_termina(ultimo.bloque_escape)
        return False

    # Visitas ------------------------------------------------------------
    def visit_asignacion(self, nodo: NodoAsignacion) -> None:
        """Visita un nodo de asignación."""
        nombre = nodo.variable
        self._validar_nombre(nombre)

        if not self.current_scope.resolver_local(nombre):
            self.current_scope.declarar(nombre, "variable")

        if hasattr(nodo.expresion, "aceptar"):
            nodo.expresion.aceptar(self)

    def visit_import(self, nodo: NodoImport) -> None:
        """Registra los símbolos declarados por un módulo importado."""

        for nombre, tipo in self._simbolos_importados(nodo.ruta):
            if not self.current_scope.resolver_local(nombre):
                self.current_scope.declarar(nombre, tipo)

    def visit_identificador(self, nodo: NodoIdentificador) -> None:
        """Visita un nodo identificador."""
        if not self.current_scope.resolver(nodo.nombre):
            raise NameError(f"Variable no declarada: {nodo.nombre}")

    def visit_funcion(self, nodo: NodoFuncion) -> None:
        """Visita un nodo función."""
        self._validar_nombre(nodo.nombre)
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")

        self.current_scope.declarar(nodo.nombre, "funcion")
        self._procesar_bloque_codigo(nodo.parametros, nodo.cuerpo)

    def visit_garantia(self, nodo: NodoGarantia) -> None:
        """Verifica las garantías semánticas del bloque ``sino``."""
        if not self._bloque_termina(nodo.bloque_escape):
            raise ValueError(
                "El bloque 'sino' de 'garantia' debe terminar con 'retorno', 'romper', 'continuar' o 'throw'"
            )
        for instruccion in nodo.bloque_escape:
            instruccion.aceptar(self)
        for instruccion in nodo.bloque_continuacion:
            instruccion.aceptar(self)

    def visit_metodo(self, nodo: NodoMetodo) -> None:
        """Visita un nodo método."""
        self._validar_nombre(nodo.nombre)
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")
            
        self.current_scope.declarar(nodo.nombre, "funcion")
        self._procesar_bloque_codigo(nodo.parametros, nodo.cuerpo)

    def visit_clase(self, nodo: NodoClase) -> None:
        """Visita un nodo clase."""
        self._validar_nombre(nodo.nombre)
        if self.current_scope.resolver_local(nodo.nombre):
            raise ValueError(f"Símbolo ya declarado: {nodo.nombre}")

        self.current_scope.declarar(nodo.nombre, "clase")

        for base in nodo.bases:
            self._validar_nombre(base)
            simbolo = self.current_scope.resolver(base)
            if not simbolo or simbolo.tipo != "clase":
                raise ValueError(f"Clase base no encontrada: {base}")
            if base == nodo.nombre or self._hay_camino(base, nodo.nombre):
                raise ValueError(f"Herencia circular detectada: {nodo.nombre} -> {base}")

        self.herencia[nodo.nombre] = list(nodo.bases)
        self._con_nuevo_ambito()
        try:
            for metodo in nodo.metodos:
                metodo.aceptar(self)
        finally:
            self._salir_ambito()

    def generic_visit(self, node: Any) -> None:
        """Visita genérica para nodos sin visita específica."""
        try:
            for valor in getattr(node, "__dict__", {}).values():
                if isinstance(valor, list):
                    for elem in valor:
                        if hasattr(elem, "aceptar"):
                            elem.aceptar(self)
                elif hasattr(valor, "aceptar"):
                    valor.aceptar(self)
        except AttributeError:
            pass  # Ignorar atributos inválidos
