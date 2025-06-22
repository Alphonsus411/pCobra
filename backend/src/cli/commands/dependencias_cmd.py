import os
import subprocess
from .base import BaseCommand


class DependenciasCommand(BaseCommand):
    """Gestiona las dependencias del proyecto."""

    name = "dependencias"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help="Gestiona las dependencias del proyecto"
        )
        dep_sub = parser.add_subparsers(dest="accion")
        dep_sub.add_parser("listar", help="Lista las dependencias")
        dep_sub.add_parser("instalar", help="Instala las dependencias")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        accion = args.accion
        if accion == "listar":
            return self._listar_dependencias()
        elif accion == "instalar":
            return self._instalar_dependencias()
        else:
            print("Acci\u00f3n de dependencias no reconocida")
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
            print("No se encontr\u00f3 requirements.txt")
            return 1
        with open(archivo, "r") as f:
            deps = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        if not deps:
            print("No hay dependencias listadas")
        else:
            for dep in deps:
                print(dep)
        return 0

    @classmethod
    def _instalar_dependencias(cls):
        archivo = cls._ruta_requirements()
        try:
            subprocess.run(["pip", "install", "-r", archivo], check=True)
            print("Dependencias instaladas")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Error instalando dependencias: {e}")
            return 1
