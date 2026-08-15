class NodoValidadoConAssert:
    def __post_init__(self):
        assert isinstance(self.valor, int)


class NodoValidadoConIsinstance:
    def __post_init__(self):
        isinstance(self.valor, int)
