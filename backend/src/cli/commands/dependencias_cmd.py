import os
import subprocess
import tempfile
import tomllib
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info


class DependenciasCommand(BaseCommand):
    """Gestiona las dependencias del proyecto."""

    name = "dependencias"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Gestiona las dependencias del proyecto")
        )
        dep_sub = parser.add_subparsers(dest="accion")
        dep_sub.add_parser("listar", help=_("Lista las dependencias"))
        dep_sub.add_parser("instalar", help=_("Instala las dependencias"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
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

    @staticmethod
    def _ruta_pyproject():
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "pyproject.toml")
        )

    @classmethod
    def _leer_requirements(cls):
        archivo = cls._ruta_requirements()
        deps: list[str] = []
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                deps = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        return deps

    @classmethod
    def _leer_pyproject(cls):
        archivo = cls._ruta_pyproject()
        deps: list[str] = []
        if os.path.exists(archivo):
            with open(archivo, "rb") as f:
                data = tomllib.load(f)
            project = data.get("project", {})
            deps.extend(project.get("dependencies", []))
            for extra in project.get("optional-dependencies", {}).values():
                deps.extend(extra)
        return deps

    @classmethod
    def _obtener_dependencias(cls):
        deps = cls._leer_requirements() + cls._leer_pyproject()
        # Eliminar duplicados preservando orden
        vista = set()
        unicos = []
        for d in deps:
            if d not in vista:
                vista.add(d)
                unicos.append(d)
        return unicos

    @classmethod
    def _listar_dependencias(cls):
        deps = cls._obtener_dependencias()
        if not deps:
            mostrar_info(_("No hay dependencias listadas"))
        else:
            for dep in deps:
                mostrar_info(dep)
        return 0

    @classmethod
    def _instalar_dependencias(cls):
        deps = cls._obtener_dependencias()
        if not deps:
            mostrar_info(_("No hay dependencias listadas"))
            return 0
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            for dep in deps:
                tmp.write(dep + "\n")
            tmp_path = tmp.name
        try:
            subprocess.run(["pip", "install", "-r", tmp_path], check=True)
            mostrar_info(_("Dependencias instaladas"))
            return 0
        except subprocess.CalledProcessError as e:
            mostrar_error(
                _("Error instalando dependencias: {err}").format(err=e)
            )
            return 1
        finally:
            os.unlink(tmp_path)
