from pcobra.core.nativos import *
import pcobra.corelibs as _pcobra_corelibs
import pcobra.standard_library as _pcobra_standard_library
globals().update({name: getattr(_pcobra_corelibs, name) for name in dir(_pcobra_corelibs) if not name.startswith('_')})
globals().update({name: getattr(_pcobra_standard_library, name) for name in dir(_pcobra_standard_library) if not name.startswith('_')})
def sumar(a, b):
    c = (NodoIdentificador(a) + NodoIdentificador(b))
    print(c)
sumar(2, 3)
