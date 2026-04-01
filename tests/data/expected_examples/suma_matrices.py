from core.nativos import *
from corelibs import *
from standard_library import *
def sumar_matriz():
    a11 = 1
    a12 = 2
    a21 = 3
    a22 = 4
    b11 = 5
    b12 = 6
    b21 = 7
    b22 = 8
    print((NodoIdentificador(a11) + NodoIdentificador(b11)))
    print((NodoIdentificador(a12) + NodoIdentificador(b12)))
    print((NodoIdentificador(a21) + NodoIdentificador(b21)))
    print((NodoIdentificador(a22) + NodoIdentificador(b22)))
sumar_matriz()
