from core.nativos import *
from corelibs import *
from standard_library import *
def factorial(n):
    if (NodoIdentificador(n) <= 1):
        return 1
    else:
        return (NodoIdentificador(n) * factorial((NodoIdentificador(n) - 1)))
print(factorial(5))
