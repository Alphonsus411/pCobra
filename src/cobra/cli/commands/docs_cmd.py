from pathlib import Path
import subprocess
from typing import Any, Optional
from argparse import ArgumentParser

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class DocsCommand(BaseCommand):
    """Genera la documentación HTML del proyecto."""
    name = "docs"
    
    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Genera la documentación del proyecto")
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        try:
            import sphinx
        except ImportError:
            mostrar_error(_("Sphinx no está instalado. Ejecuta 'pip install sphinx sphinx-rtd-theme'."))
            return 1

        raiz = Path(__file__).resolve().parents[3]
        source = raiz / "frontend" / "docs"
        build = raiz / "frontend" / "build" / "html"
        api = source / "api"
        codigo = raiz / "backend" / "src"

        # Validar todos los directorios necesarios
        if not self._validar_directorios(source, codigo):
            return 1

        # Crear directorios si no existen
        for dir in (build.parent, api):
            try:
                dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                mostrar_error(_("Error al crear directorio {dir}: {err}").format(dir=dir, err=e))
                return 1

        try:
            self._ejecutar_sphinx(api, codigo, source, build)
            mostrar_info(_("Documentación generada en {path}").format(path=build))
            return 0
        except Exception as e:
            mostrar_error(_("Error generando la documentación: {err}").format(err=e))
            return 1

    def _validar_directorios(self, source: Path, codigo: Path) -> bool:
        """Valida la existencia de directorios requeridos."""
        if not source.exists():
            mostrar_error(_("No se encuentra el directorio de documentación"))
            return False
        if not codigo.exists():
            mostrar_error(_("No se encuentra el directorio de código fuente"))
            return False
        return True

    def _ejecutar_sphinx(self, api: Path, codigo: Path, source: Path, build: Path) -> None:
        """Ejecuta los comandos de Sphinx."""
        for cmd in [
            ["sphinx-apidoc", "-o", str(api), str(codigo)],
            ["sphinx-build", "-b", "html", str(source), str(build)]
        ]:
            resultado = subprocess.run(cmd, capture_output=True, text=True)
            if resultado.returncode != 0:
                raise RuntimeError(f"Error ejecutando {cmd[0]}: {resultado.stderr}")