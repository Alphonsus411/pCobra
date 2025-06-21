class BaseCommand:
    """Clase base para subcomandos de la CLI."""

    #: Nombre del subcomando
    name: str = ""

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando en el parser."""
        raise NotImplementedError

    def run(self, args):
        """Ejecuta la lógica del comando."""
        raise NotImplementedError
