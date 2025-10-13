import logging
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional, Any

try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

logger = logging.getLogger(__name__)

class DependenciasCommand(BaseCommand):
    """Gestiona las dependencias del proyecto.
    
    Este comando permite listar e instalar las dependencias definidas en 
    requirements.txt y pyproject.toml.
    
    Ejemplos:
        cobra dependencias listar
        cobra dependencias instalar
    """

    name = "dependencias"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado para este subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Gestiona las dependencias del proyecto")
        )
        dep_sub = parser.add_subparsers(dest="accion", required=True)
        dep_sub.add_parser("listar", help=_("Lista las dependencias"))
        dep_sub.add_parser("instalar", help=_("Instala las dependencias"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
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
            
        Raises:
            RuntimeError: Si no se puede determinar la ruta del proyecto
        """
        try:
            return Path(__file__).resolve().parents[4]
        except Exception as e:
            raise RuntimeError("No se pudo determinar la ruta del proyecto") from e

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
    def _validar_dependencia(cls, dep: str) -> bool:
        """Valida el formato de una dependencia.
        
        Args:
            dep: Dependencia a validar
            
        Returns:
            bool: True si la dependencia es válida
        """
        return bool(dep and not dep.startswith(("#", "-")))

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
                        if cls._validar_dependencia(line.strip())
                    ]
            except IOError as e:
                logger.exception("Error leyendo requirements.txt")
                raise IOError(f"Error leyendo requirements.txt: {e}") from e
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
                deps.extend(d for d in project.get("dependencies", []) if cls._validar_dependencia(d))
                for extra in project.get("optional-dependencies", {}).values():
                    deps.extend(d for d in extra if cls._validar_dependencia(d))
            except (IOError, tomllib.TOMLDecodeError) as e:
                logger.exception("Error leyendo pyproject.toml")
                raise

        return deps

    @classmethod
    def _obtener_dependencias(cls) -> List[str]:
        """Obtiene la lista combinada de dependencias sin duplicados.
        
        Returns:
            List[str]: Lista de dependencias únicas
            
        Raises:
            Exception: Si hay error leyendo algún archivo de dependencias
        """
        deps = cls._leer_requirements() + cls._leer_pyproject()
        return list(dict.fromkeys(deps))

    @classmethod
    def _crear_entorno_virtual(cls) -> Optional[str]:
        """Crea un entorno virtual para instalar las dependencias.
        
        Returns:
            Optional[str]: Ruta al entorno virtual o None si falla
            
        Raises:
            OSError: Si no hay suficiente espacio en disco
        """
        venv_path = cls._get_project_root() / ".venv"
        
        if venv_path.exists():
            logger.info("Eliminando entorno virtual existente")
            try:
                shutil.rmtree(str(venv_path))
            except OSError as e:
                logger.error(f"Error eliminando entorno virtual: {e}")
                return None

        try:
            # Verificar espacio en disco (100MB mínimo)
            free_space = shutil.disk_usage(str(venv_path.parent)).free
            if free_space < 100 * 1024 * 1024:
                raise OSError("Espacio insuficiente en disco")
                
            venv.create(venv_path, with_pip=True)
            return str(venv_path)
        except OSError as e:
            logger.exception("Error creando entorno virtual")
            return None

    @classmethod
    def _listar_dependencias(cls) -> int:
        """Lista todas las dependencias encontradas.
        
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
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
            logger.exception("Error listando dependencias")
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

            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
                for dep in deps:
                    tmp.write(f"{dep}\n")
                tmp_path = tmp.name

            try:
                scripts_dir = "Scripts" if sys.platform == "win32" else "bin"
                pip_path = str(Path(venv_path) / scripts_dir / ("pip.exe" if sys.platform == "win32" else "pip"))

                if not Path(pip_path).exists():
                    mostrar_error(_("No se encontró pip en el entorno virtual"))
                    return 1

                subprocess.run(
                    [pip_path, "install", "-r", tmp_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                mostrar_info(_("Dependencias instaladas en el entorno virtual"))
                return 0

            except subprocess.CalledProcessError as e:
                logger.exception("Error en la instalación de dependencias")
                mostrar_error(_("Error instalando dependencias: {err}").format(err=e.stderr))
                return 1
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        except Exception as e:
            logger.exception("Error en el proceso de instalación")
            mostrar_error(str(e))
            return 1
