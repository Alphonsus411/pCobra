from core.nativos import *
from corelibs import *
from standard_library import *
def sumar(a, b):
    c = (NodoIdentificador(a) + NodoIdentificador(b))
    print(c)
sumar(2, 3)
