from typing import Any, List, Optional


class ConstantesTranspilador:
    """Constantes utilizadas en la transpilación"""
    IF = "IF"
    ELSE = "ELSE"
    END = "END"


def visit_condicional(self, nodo: Any) -> None:
    """
    Visita y procesa un nodo condicional.

    Args:
        nodo: Nodo AST que representa una estructura condicional

    Returns:
        None

    Raises:
        ValueError: Si el nodo es None
        AttributeError: Si el nodo no tiene los atributos requeridos
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    if not hasattr(nodo, "condicion"):
        raise AttributeError("El nodo debe tener un atributo 'condicion'")

    try:
        bloque_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
        bloque_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))

        condicion = self.obtener_valor(nodo.condicion)
        self._procesar_estructura_condicional(condicion, bloque_si, bloque_sino)

    except AttributeError as e:
        raise AttributeError(f"Error en atributos del nodo condicional: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Error al procesar valores del condicional: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado al procesar el condicional: {str(e)}")


def _procesar_estructura_condicional(self, condicion: str, bloque_si: List[Any],
                                     bloque_sino: Optional[List[Any]]) -> None:
    """
    Procesa la estructura del condicional.

    Args:
        condicion: Condición evaluada en el if
        bloque_si: Lista de instrucciones para el bloque if
        bloque_sino: Lista de instrucciones para el bloque else (opcional)
    """
    self.agregar_linea(f"{ConstantesTranspilador.IF} {condicion}")
    self._procesar_bloque(bloque_si)

    if bloque_sino:
        self.agregar_linea(ConstantesTranspilador.ELSE)
        self._procesar_bloque(bloque_sino)

    self.agregar_linea(ConstantesTranspilador.END)


def _procesar_bloque(self, instrucciones: List[Any]) -> None:
    """
    Procesa un bloque de instrucciones con el manejo apropiado de la indentación.

    Args:
        instrucciones: Lista de instrucciones a procesar
    """
    self.indent += 1
    try:
        for instruccion in instrucciones:
            if instruccion is not None:
                instruccion.aceptar(self)
    finally:
        self.indent -= 1