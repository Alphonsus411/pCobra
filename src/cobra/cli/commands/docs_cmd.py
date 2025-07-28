import sys
from pathlib import Path
import subprocess
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class DocsCommand(BaseCommand):
    """Genera la documentación HTML del proyecto."""
    name = "docs"
    
    def register_subparser(self, subparsers: Any) -> Any:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Genera la documentación del proyecto")
        )
        parser.set_defaults(cmd=self)
        return parser
        
    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        try:
            # Verificar que sphinx esté instalado
            import sphinx
        except ImportError:
            mostrar_error(_("Sphinx no está instalado. Ejecuta 'pip install sphinx'."))
            return 1
            
        # Usar pathlib para manejo de rutas
        raiz = Path(__file__).resolve().parents[3]
        source = raiz / "frontend" / "docs"
        build = raiz / "frontend" / "build" / "html"
        api = source / "api"
        codigo = raiz / "backend" / "src"

        # Validar existencia de directorios
        if not codigo.exists():
            mostrar_error(_("No se encuentra el directorio de código fuente"))
            return 1
            
        # Crear directorio de build si no existe
        build.parent.mkdir(parents=True, exist_ok=True)
            
        try:
            subprocess.run(["sphinx-apidoc", "-o", str(api), str(codigo)], 
                         check=True, capture_output=True, text=True)
            subprocess.run(["sphinx-build", "-b", "html", str(source), str(build)],
                         check=True, capture_output=True, text=True)
            mostrar_info(_("Documentación generada en {path}").format(path=build))
            return 0
            
        except (subprocess.CalledProcessError, OSError) as e:
            mostrar_error(_("Error generando la documentación: {err}").format(err=e))
            return 1