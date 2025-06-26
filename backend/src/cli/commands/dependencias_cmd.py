import os
import subprocess
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info


class DependenciasCommand(BaseCommand):
    """Gestiona las dependencias del proyecto."""

    name = "dependencias"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help=_("Gestiona las dependencias del proyecto")
        )
        dep_sub = parser.add_subparsers(dest="accion")
        dep_sub.add_parser("listar", help=_("Lista las dependencias"))
        dep_sub.add_parser("instalar", help=_("Instala las dependencias"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        accion = args.accion
        if accion == "listar":
            return self._listar_dependencias()
        elif accion == "instalar":
            return self._instalar_dependencias()
        else:
            mostrar_error(_("Acción de dependencias no reconocida"))
            return 1

    @staticmethod
    def _ruta_requirements():
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "requirements.txt")
        )

    @classmethod
    def _listar_dependencias(cls):
        archivo = cls._ruta_requirements()
        if not os.path.exists(archivo):
            mostrar_error(_("No se encontró requirements.txt"))
            return 1
        with open(archivo, "r") as f:
            deps = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        if not deps:
            mostrar_info(_("No hay dependencias listadas"))
        else:
            for dep in deps:
                mostrar_info(dep)
        return 0

    @classmethod
    def _instalar_dependencias(cls):
        archivo = cls._ruta_requirements()
        try:
            subprocess.run(["pip", "install", "-r", archivo], check=True)
            mostrar_info(_("Dependencias instaladas"))
            return 0
        except subprocess.CalledProcessError as e:
            mostrar_error(
                _("Error instalando dependencias: {err}").format(err=e)
            )
            return 1
