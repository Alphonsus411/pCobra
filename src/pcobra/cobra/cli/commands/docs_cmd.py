from pathlib import Path
import subprocess
from typing import Any, Optional
from argparse import ArgumentParser

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

class DocsCommand(BaseCommand):
    """Genera la documentación HTML del proyecto."""
    name = "docs"
    SPHINX_TIMEOUT = 300  # segundos

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name,
            help=_(
                "Genera la documentación del proyecto (límite {t} s)"
            ).format(t=self.SPHINX_TIMEOUT),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        raiz = self._obtener_raiz()
        source = raiz / "docs"
        build = source / "_build" / "html"
        api = source / "api"
        codigo = raiz / "src" / "pcobra"

        # Validar todos los directorios necesarios
        if not self._validar_directorios(source, codigo):
            return 1

        # Crear directorios si no existen
        for dir in (api, build):
            try:
                dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                mostrar_error(_("Error al crear directorio {dir}: {err}").format(dir=dir, err=e))
                return 1

        try:
            import sphinx
        except ImportError:
            mostrar_error(_("Sphinx no está instalado. Ejecuta 'pip install sphinx sphinx-rtd-theme'."))
            return 1

        try:
            self._ejecutar_sphinx(api, codigo, source, build)
            mostrar_info(_("Documentación generada en {path}").format(path=build))
            return 0
        except Exception as e:
            mostrar_error(_("Error generando la documentación: {err}").format(err=e))
            return 1

    def _obtener_raiz(self) -> Path:
        """Devuelve la ruta raíz del repositorio."""
        return Path(__file__).resolve().parents[5]

    def _validar_directorios(self, source: Path, codigo: Path) -> bool:
        """Valida la existencia de directorios requeridos."""
        if not source.exists():
            mostrar_error(_("No se encuentra el directorio de documentación en {path}").format(path=source))
            return False
        if not codigo.exists():
            mostrar_error(_("No se encuentra el directorio de código fuente en {path}").format(path=codigo))
            return False
        return True

    def _ejecutar_sphinx(self, api: Path, codigo: Path, source: Path, build: Path) -> None:
        """Ejecuta los comandos de Sphinx."""
        for cmd in [
            ["sphinx-apidoc", "-o", str(api), str(codigo)],
            ["sphinx-build", "-b", "html", str(source), str(build)]
        ]:
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=self.SPHINX_TIMEOUT,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Error ejecutando {cmd[0]}: {e.stderr}"
                ) from e
            except subprocess.TimeoutExpired as e:
                raise RuntimeError(
                    _( "El comando {cmd} excedió el tiempo límite de {t} s" ).format(
                        cmd=cmd[0], t=self.SPHINX_TIMEOUT
                    )
                ) from e
