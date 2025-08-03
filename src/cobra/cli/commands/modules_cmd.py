import os
import shutil
import logging
from typing import Any, Dict, Optional
from argparse import _SubParsersAction
from pathlib import Path
from filelock import FileLock
import yaml

from cobra.semantico import mod_validator
from cobra.transpilers.module_map import MODULE_MAP_PATH
from cobra.cli.cobrahub_client import descargar_modulo, publicar_modulo
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from cobra.cli.utils.semver import es_nueva_version, es_version_valida

# Configuración de logging
logger = logging.getLogger(__name__)

# Constantes
MODULES_PATH = Path(os.path.dirname(__file__)) / ".." / "modules"
LOCK_FILE = MODULE_MAP_PATH
LOCK_KEY = "lock"
MODULE_EXTENSION = ".co"

# Crear directorio de módulos si no existe
MODULES_PATH.mkdir(parents=True, exist_ok=True)

class ModulesCommand(BaseCommand):
    """Gestiona los módulos instalados."""

    name = "modulos"

    def register_subparser(self, subparsers: _SubParsersAction) -> _SubParsersAction:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            Parser configurado para el subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Gestiona módulos instalados"))
        mod_sub = parser.add_subparsers(dest="accion")
        mod_sub.add_parser("listar", help=_("Lista módulos"))
        inst = mod_sub.add_parser("instalar", help=_("Instala un módulo"))
        inst.add_argument("ruta", help=_("Ruta al archivo del módulo"))
        rem = mod_sub.add_parser("remover", help=_("Elimina un módulo"))
        rem.add_argument("nombre", help=_("Nombre del módulo a eliminar"))
        pub = mod_sub.add_parser("publicar", help=_("Publica un módulo en CobraHub"))
        pub.add_argument("ruta", help=_("Ruta al archivo del módulo"))
        bus = mod_sub.add_parser("buscar", help=_("Descarga un módulo desde CobraHub"))
        bus.add_argument("nombre", help=_("Nombre del módulo a buscar"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error

        Raises:
            ValueError: Si la acción no es válida
        """
        accion = args.accion
        if not accion:
            mostrar_error(_("Debe especificar una acción"))
            return 1

        acciones = {
            "listar": self._listar_modulos,
            "instalar": lambda: self._instalar_modulo(args.ruta),
            "remover": lambda: self._remover_modulo(args.nombre),
            "publicar": lambda: 0 if publicar_modulo(args.ruta) else 1,
            "buscar": lambda: self._buscar_modulo(args.nombre)
        }

        try:
            if accion not in acciones:
                raise ValueError(_("Acción de módulos no reconocida"))
            return acciones[accion]()
        except Exception as e:
            logger.error(f"Error en comando de módulos: {str(e)}")
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _obtener_version(ruta: str) -> Optional[str]:
        """Obtiene la versión de un módulo.

        Args:
            ruta: Ruta al archivo del módulo

        Returns:
            Versión del módulo o None si no se encuentra

        Raises:
            IOError: Si hay error al leer el archivo
            yaml.YAMLError: Si hay error en el formato YAML
        """
        try:
            if os.path.exists(MODULE_MAP_PATH):
                with open(MODULE_MAP_PATH, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    for mod_path, info in data.items():
                        if mod_path == LOCK_KEY:
                            continue
                        if os.path.basename(mod_path) == os.path.basename(ruta):
                            return info.get("version")
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Error al leer versión: {str(e)}")
            mostrar_error(_("Error al leer versión: {err}").format(err=str(e)))
        return None

    @staticmethod
    def _cargar_lock() -> Dict:
        """Carga el archivo de lock.

        Returns:
            Diccionario con datos del archivo lock

        Raises:
            IOError: Si hay error al leer el archivo
            yaml.YAMLError: Si hay error en el formato YAML
        """
        data: Dict = {}
        try:
            if os.path.exists(LOCK_FILE):
                with FileLock(f"{LOCK_FILE}.lock"):
                    with open(LOCK_FILE, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Error al cargar lock: {str(e)}")
            mostrar_error(_("Error al cargar lock: {err}").format(err=str(e)))
        data.setdefault(LOCK_KEY, {})
        return data

    @staticmethod
    def _validar_nombre_modulo(nombre: str) -> bool:
        """Valida que el nombre del módulo sea válido.

        Args:
            nombre: Nombre del módulo a validar

        Returns:
            bool: True si el nombre es válido, False en caso contrario
        """
        return bool(nombre and not any(c in nombre for c in r'<>:"/\|?*'))

    @staticmethod
    def _validar_ruta(ruta: str) -> bool:
        """Valida que la ruta sea segura.

        Args:
            ruta: Ruta a validar

        Returns:
            bool: True si la ruta es segura, False en caso contrario
        """
        try:
            ruta_abs = os.path.abspath(ruta)
            return not any(
                parte.startswith('.') for parte in Path(ruta_abs).parts
            )
        except Exception:
            return False

    @staticmethod
    def _obtener_version_lock(nombre: str) -> Optional[str]:
        """Obtiene la versión de un módulo del archivo lock.

        Args:
            nombre: Nombre del módulo

        Returns:
            Versión del módulo o None si no existe
        """
        if not nombre or not ModulesCommand._validar_nombre_modulo(nombre):
            return None
        data = ModulesCommand._cargar_lock()
        return data.get(LOCK_KEY, {}).get(nombre)

    @staticmethod
    def _actualizar_lock(nombre: str, version: Optional[str]) -> None:
        """Actualiza la información de un módulo en el archivo lock.

        Args:
            nombre: Nombre del módulo
            version: Nueva versión del módulo

        Raises:
            IOError: Si hay error al escribir el archivo
            yaml.YAMLError: Si hay error en el formato YAML
        """
        if not nombre or not ModulesCommand._validar_nombre_modulo(nombre):
            return
        try:
            with FileLock(f"{LOCK_FILE}.lock"):
                data = ModulesCommand._cargar_lock()
                data[LOCK_KEY][nombre] = version
                with open(LOCK_FILE, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Error al actualizar lock: {str(e)}")
            mostrar_error(_("Error al actualizar lock: {err}").format(err=str(e)))

    @staticmethod
    def _listar_modulos() -> int:
        """Lista los módulos instalados.

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error
        """
        try:
            mod_validator.validar_mod(MODULE_MAP_PATH)
            mods = [f for f in os.listdir(MODULES_PATH) if f.endswith(MODULE_EXTENSION)]
            if not mods:
                mostrar_info(_("No hay módulos instalados"))
            else:
                for m in sorted(mods):
                    mostrar_info(m)
            return 0
        except (ValueError, OSError) as e:
            logger.error(f"Error al listar módulos: {str(e)}")
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _instalar_modulo(ruta: str) -> int:
        """Instala un módulo.

        Args:
            ruta: Ruta al archivo del módulo

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error

        Raises:
            ValueError: Si la ruta o el módulo no son válidos
        """
        try:
            if not ModulesCommand._validar_ruta(ruta):
                raise ValueError(_("Ruta de módulo inválida"))

            mod_validator.validar_mod(MODULE_MAP_PATH)
            ruta_abs = os.path.abspath(ruta)

            if not os.path.exists(ruta_abs):
                raise ValueError(_("No se encontró el módulo {path}").format(path=ruta))

            if os.path.islink(ruta_abs) or not os.path.isfile(ruta_abs) or not ruta.endswith(MODULE_EXTENSION):
                raise ValueError(_("Ruta de módulo inválida"))

            nombre = os.path.basename(ruta_abs)
            if not ModulesCommand._validar_nombre_modulo(nombre):
                raise ValueError(_("Nombre de módulo inválido"))

            destino = MODULES_PATH / nombre
            if destino.exists() and destino.is_symlink():
                raise ValueError(_("El destino {dest} es un enlace simbólico").format(dest=destino))

            shutil.copy2(ruta_abs, destino)
            mostrar_info(_("Módulo instalado en {dest}").format(dest=destino))

            version = ModulesCommand._obtener_version(ruta_abs)
            if version and not es_version_valida(version):
                raise ValueError(_("Versión de módulo inválida"))

            actual = ModulesCommand._obtener_version_lock(nombre)
            if actual and version and not es_nueva_version(version, actual):
                raise ValueError(
                    _("La nueva versión {v} no supera a {a}").format(v=version, a=actual)
                )

            ModulesCommand._actualizar_lock(nombre, version)
            return 0

        except Exception as e:
            logger.error(f"Error al instalar módulo: {str(e)}")
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _remover_modulo(nombre: str) -> int:
        """Elimina un módulo instalado.

        Args:
            nombre: Nombre del módulo a eliminar

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error

        Raises:
            ValueError: Si el nombre no es válido o el módulo no existe
        """
        if not nombre or not ModulesCommand._validar_nombre_modulo(nombre):
            mostrar_error(_("Nombre de módulo inválido"))
            return 1

        try:
            archivo = MODULES_PATH / nombre
            if not archivo.exists():
                raise ValueError(_("El módulo {name} no existe").format(name=nombre))

            try:
                archivo.unlink()
            except OSError as e:
                raise ValueError(_("Error al eliminar módulo: {err}").format(err=str(e)))

            mostrar_info(_("Módulo {name} eliminado").format(name=nombre))

            with FileLock(f"{LOCK_FILE}.lock"):
                data = ModulesCommand._cargar_lock()
                if nombre in data.get(LOCK_KEY, {}):
                    del data[LOCK_KEY][nombre]
                    with open(LOCK_FILE, "w", encoding="utf-8") as f:
                        yaml.safe_dump(data, f)
            return 0

        except Exception as e:
            logger.error(f"Error al remover módulo: {str(e)}")
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _buscar_modulo(nombre: str) -> int:
        """Busca y descarga un módulo desde CobraHub.

        Args:
            nombre: Nombre del módulo a buscar

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error

        Raises:
            ValueError: Si el nombre no es válido
        """
        if not nombre or not ModulesCommand._validar_nombre_modulo(nombre):
            mostrar_error(_("Nombre de módulo inválido"))
            return 1

        try:
            destino = str(MODULES_PATH / nombre)
            ok = descargar_modulo(nombre, destino)
            if ok:
                ModulesCommand._actualizar_lock(nombre, None)
            return 0 if ok else 1
        except Exception as e:
            logger.error(f"Error al buscar módulo: {str(e)}")
            mostrar_error(str(e))
            return 1