# Código generado (TranspiladorPython):
from core.nativos import *
from corelibs import *
from standard_library import *


def principal():
    referentes = [
        {"Nombre": "Ada", "Rol": "Pionera"},
        {"Nombre": "Grace", "Rol": "Arquitecta"},
    ]

    mostrar_tabla(referentes, titulo="Referentes Cobra")
    imprimir_aviso("Tabla generada", nivel="exito")

    with barra_progreso(total=3, descripcion="Preparando demo") as (progreso, tarea):
        for _ in range(3):
            progreso.advance(tarea)


principal()
