from pcobra.cobra.core.nativos import *
import pcobra.corelibs as _pcobra_corelibs
import pcobra.standard_library as _pcobra_standard_library
globals().update({name: getattr(_pcobra_corelibs, name) for name in dir(_pcobra_corelibs) if not name.startswith('_')})
globals().update({name: getattr(_pcobra_standard_library, name) for name in dir(_pcobra_standard_library) if not name.startswith('_')})
def sumar_matriz():
    a11 = 1
    a12 = 2
    a21 = 3
    a22 = 4
    b11 = 5
    b12 = 6
    b21 = 7
    b22 = 8
    print(a11 + b11)
    print(a12 + b12)
    print(a21 + b21)
    print(a22 + b22)
sumar_matriz()
