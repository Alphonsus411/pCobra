import logging
import os
import subprocess
import tempfile
import venv
from pathlib import Path
from typing import List, Optional

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

logger = logging.getLogger(__name__)

class DependenciasCommand(BaseCommand):
    """Gestiona las dependencias del proyecto.
    
    Este comando permite listar e instalar las dependencias definidas en 
    requirements.txt y pyproject.toml.
    """

    name = "dependencias"

    def register_subparser(self, subparsers) -> None:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
        """
        parser = subparsers.add_parser(
            self.name, help=_("Gestiona las dependencias del proyecto")
        )
        dep_sub = parser.add_subparsers(dest="accion", required=True)
        dep_sub.add_parser("listar", help=_("Lista las dependencias"))
        dep_sub.add_parser("instalar", help=_("Instala las dependencias"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        accion = args.accion
        try:
            if accion == "listar":
                return self._listar_dependencias()
            elif accion == "instalar":
                return self._instalar_dependencias()
            else:
                mostrar_error(_("Acción de dependencias no reconocida"))
                return 1
        except Exception as e:
            logger.exception("Error ejecutando comando de dependencias")
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _get_project_root() -> Path:
        """Obtiene la ruta raíz del proyecto.
        
        Returns:
            Path: Ruta absoluta a la raíz del proyecto
        """
        return Path(__file__).resolve().parents[4]

    @classmethod
    def _ruta_requirements(cls) -> Path:
        """Obtiene la ruta al archivo requirements.txt.
        
        Returns:
            Path: Ruta absoluta al archivo requirements.txt
        """
        return cls._get_project_root() / "requirements.txt"

    @classmethod
    def _ruta_pyproject(cls) -> Path:
        """Obtiene la ruta al archivo pyproject.toml.
        
        Returns:
            Path: Ruta absoluta al archivo pyproject.toml
        """
        return cls._get_project_root() / "pyproject.toml"

    @classmethod
    def _leer_requirements(cls) -> List[str]:
        """Lee las dependencias del archivo requirements.txt.
        
        Returns:
            List[str]: Lista de dependencias encontradas
            
        Raises:
            IOError: Si hay problemas leyendo el archivo
        """
        deps: List[str] = []
        ruta = cls._ruta_requirements()
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    deps = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
            except IOError as e:
                logger.error(f"Error leyendo requirements.txt: {e}")
                raise
        return deps

    @classmethod
    def _leer_pyproject(cls) -> List[str]:
        """Lee las dependencias del archivo pyproject.toml.
        
        Returns:
            List[str]: Lista de dependencias encontradas
            
        Raises:
            IOError: Si hay problemas leyendo el archivo
            tomllib.TOMLDecodeError: Si hay errores en el formato TOML
        """
        deps: List[str] = []
        ruta = cls._ruta_pyproject()
        if ruta.exists():
            try:
                with open(ruta, "rb") as f:
                    data = tomllib.load(f)
                project = data.get("project", {})
                deps.extend(project.get("dependencies", []))
                for extra in project.get("optional-dependencies", {}).values():
                    deps.extend(extra)
            except (IOError, tomllib.TOMLDecodeError) as e:
                logger.error(f"Error leyendo pyproject.toml: {e}")
                raise
        return deps

    @classmethod
    def _obtener_dependencias(cls) -> List[str]:
        """Obtiene la lista combinada de dependencias sin duplicados.
        
        Returns:
            List[str]: Lista de dependencias únicas
        """
        deps = cls._leer_requirements() + cls._leer_pyproject()
        return list(dict.fromkeys(deps))  # Preserva orden y elimina duplicados

    @classmethod
    def _crear_entorno_virtual(cls) -> Optional[str]:
        """Crea un entorno virtual para instalar las dependencias.
        
        Returns:
            Optional[str]: Ruta al entorno virtual o None si falla
        """
        venv_path = cls._get_project_root() / ".venv"
        try:
            venv.create(venv_path, with_pip=True)
            return str(venv_path)
        except Exception as e:
            logger.error(f"Error creando entorno virtual: {e}")
            return None

    @classmethod
    def _listar_dependencias(cls) -> int:
        """Lista todas las dependencias encontradas.
        
        Returns:
            int: 0 si la ejecución fue exitosa
        """
        try:
            deps = cls._obtener_dependencias()
            if not deps:
                mostrar_info(_("No hay dependencias listadas"))
            else:
                for dep in deps:
                    mostrar_info(dep)
            return 0
        except Exception as e:
            mostrar_error(str(e))
            return 1

    @classmethod
    def _instalar_dependencias(cls) -> int:
        """Instala las dependencias en un entorno virtual.
        
        Returns:
            int: 0 si la instalación fue exitosa, 1 en caso de error
        """
        try:
            deps = cls._obtener_dependencias()
            if not deps:
                mostrar_info(_("No hay dependencias listadas"))
                return 0

            venv_path = cls._crear_entorno_virtual()
            if not venv_path:
                mostrar_error(_("No se pudo crear el entorno virtual"))
                return 1

            with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
                for dep in deps:
                    tmp.write(f"{dep}\n")
                tmp_path = tmp.name

            try:
                pip_path = str(Path(venv_path) / "Scripts" / "pip.exe") \
                    if os.name == "nt" else str(Path(venv_path) / "bin" / "pip")
                
                subprocess.run(
                    [pip_path, "install", "-r", tmp_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                mostrar_info(_("Dependencias instaladas en el entorno virtual"))
                return 0
            except subprocess.CalledProcessError as e:
                mostrar_error(_("Error instalando dependencias: {err}").format(err=e.stderr))
                return 1
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            mostrar_error(str(e))
            return 1