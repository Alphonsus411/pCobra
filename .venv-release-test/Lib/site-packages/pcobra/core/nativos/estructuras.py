class Pila:
    """Implementa una estructura de pila simple."""

    def __init__(self):
        self._datos = []

    def apilar(self, valor):
        self._datos.append(valor)

    def desapilar(self):
        return self._datos.pop() if self._datos else None


class Cola:
    """Implementa una cola simple."""

    def __init__(self):
        self._datos = []

    def encolar(self, valor):
        self._datos.append(valor)

    def desencolar(self):
        return self._datos.pop(0) if self._datos else None
