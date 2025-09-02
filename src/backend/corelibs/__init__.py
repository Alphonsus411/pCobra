"""Compatibilidad hacia atrás para las librerías de núcleo.
Reexporta las utilidades desde ``pcobra.corelibs`` y expone sus
submódulos para facilitar pruebas."""

from pcobra.corelibs import *  # noqa: F401,F403
import pcobra.corelibs.archivo as archivo
import pcobra.corelibs.coleccion as coleccion
import pcobra.corelibs.numero as numero
import pcobra.corelibs.red as red
import pcobra.corelibs.seguridad as seguridad
import pcobra.corelibs.sistema as sistema
import pcobra.corelibs.tiempo as tiempo
import pcobra.corelibs.texto as texto
