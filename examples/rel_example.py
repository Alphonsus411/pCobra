"""Ejemplo práctico del context manager ``rel`` de pcobra."""

from __future__ import annotations

import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROYECTO / "src"))
sys.path.insert(0, str(PROYECTO / "src" / "pcobra"))

from standard_library.util import rel


class Contador:
    """Pequeña clase para mostrar cómo ``rel`` modifica un atributo temporalmente."""

    def __init__(self, valor: int = 0) -> None:
        self.valor = valor

    def incrementar(self) -> None:
        self.valor += 1


def saludar() -> str:
    """Función que se modificará temporalmente durante el ejemplo."""

    return "Hola desde la versión original"


def _parchear_saludo(modulo):
    """Cambia la implementación de ``saludar`` y devuelve cómo restaurarla."""

    saludo_original = modulo.saludar

    def saludo_temporal() -> str:
        return "Hola desde la versión temporal"

    modulo.saludar = saludo_temporal

    def restaurar() -> None:
        modulo.saludar = saludo_original

    return restaurar


def main() -> None:
    contador = Contador(valor=1)
    print(f"Valor original del contador: {contador.valor}")

    with rel(contador, {"valor": 99}) as parcheado:
        # Paso 1) Aplicar: al entrar en el bloque ``with`` se guarda el valor original
        #                y se sustituye por el temporal (99).
        print(f"Valor dentro del parche: {parcheado.valor}")
        parcheado.incrementar()
        # Paso 2) Usar: operamos normalmente con el objeto mientras el parche está activo.
        print(f"Valor tras incrementar en el parche: {parcheado.valor}")

    # Paso 3) Restaurar: al salir del bloque ``with`` se recupera el valor inicial.
    print(f"Valor restaurado fuera del parche: {contador.valor}")

    print(saludar())

    modulo_actual = sys.modules[__name__]
    with rel(modulo_actual, _parchear_saludo):
        # Paso 1) Aplicar: se reemplaza la función ``saludar`` por la versión temporal.
        print(saludar())
        # Paso 2) Usar: llamamos a la función mientras dura el parche.

    # Paso 3) Restaurar: tras el ``with`` vuelve la implementación original.
    print(saludar())


if __name__ == "__main__":
    main()
