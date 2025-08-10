from argparse import ArgumentParser

from cobra.cli.i18n import _
from cobra.cli.utils import messages


class CustomArgumentParser(ArgumentParser):
    """ArgumentParser personalizado que usa mostrar_error y muestra la ayuda."""

    def error(self, message: str) -> None:  # type: ignore[override]
        """Muestra un mensaje de error localizado y la ayuda."""
        messages.mostrar_error(_(message))
        self.print_help()
        raise SystemExit(2)
