from abc import ABC, abstractmethod

class PluginInterface(ABC):
    """Interfaz base que define el comportamiento de un plugin de la CLI."""

    #: Nombre del plugin o subcomando
    name: str = ""

    #: Versión del plugin
    version: str = "0.1"

    #: Autor del plugin
    author: str = ""

    #: Breve descripción del plugin
    description: str = ""

    @abstractmethod
    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando en el parser."""
        raise NotImplementedError

    @abstractmethod
    def run(self, args):
        """Ejecuta la lógica del plugin."""
        raise NotImplementedError
