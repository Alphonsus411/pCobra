class NodoSinValidacion:
    def __post_init__(self):
        self.valor = 1


class NodoAssertAjeno:
    def __post_init__(self):
        self.valor = 1

    def validar(self):
        assert isinstance(self.valor, int)
