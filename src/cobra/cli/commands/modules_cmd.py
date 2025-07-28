import os
import shutil
from typing import Any, Dict, Optional
from filelock import FileLock
import yaml

from cobra.semantico import mod_validator
from cobra.transpilers.module_map import MODULE_MAP_PATH
from cobra.cli.cobrahub_client import descargar_modulo, publicar_modulo
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from cobra.cli.utils.semver import es_nueva_version, es_version_valida

# Constantes
MODULES_PATH = os.path.join(os.path.dirname(__file__), "..", "modules")
LOCK_FILE = MODULE_MAP_PATH
LOCK_KEY = "lock"
MODULE_EXTENSION = ".co"

# Crear directorio de módulos si no existe
os.makedirs(MODULES_PATH, exist_ok=True)

class ModulesCommand(BaseCommand):
    """Gestiona los módulos instalados."""

    name = "modulos"

    def register_subparser(self, subparsers: Any) -> Any:
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
        """
        accion = args.accion
        if not accion:
            mostrar_error(_("Debe especificar una acción"))
            return 1

        try:
            if accion == "listar":
                return self._listar_modulos()
            elif accion == "instalar":
                return self._instalar_modulo(args.ruta)
            elif accion == "remover":
                return self._remover_modulo(args.nombre)
            elif accion == "publicar":
                return 0 if publicar_modulo(args.ruta) else 1
            elif accion == "buscar":
                return self._buscar_modulo(args.nombre)
            else:
                mostrar_error(_("Acción de módulos no reconocida"))
                return 1
        except Exception as e:
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _obtener_version(ruta: str) -> Optional[str]:
        """Obtiene la versión de un módulo.

        Args:
            ruta: Ruta al archivo del módulo

        Returns:
            Versión del módulo o None si no se encuentra
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
            mostrar_error(_("Error al leer versión: {err}").format(err=str(e)))
        return None

    @staticmethod
    def _cargar_lock() -> Dict:
        """Carga el archivo de lock.

        Returns:
            Diccionario con datos del archivo lock
        """
        data: Dict = {}
        try:
            if os.path.exists(LOCK_FILE):
                with FileLock(f"{LOCK_FILE}.lock"):
                    with open(LOCK_FILE, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
        except (IOError, yaml.YAMLError) as e:
            mostrar_error(_("Error al cargar lock: {err}").format(err=str(e)))
        data.setdefault(LOCK_KEY, {})
        return data

    @staticmethod
    def _obtener_version_lock(nombre: str) -> Optional[str]:
        """Obtiene la versión de un módulo del archivo lock.

        Args:
            nombre: Nombre del módulo

        Returns:
            Versión del módulo o None si no existe
        """
        if not nombre:
            return None
        data = ModulesCommand._cargar_lock()
        return data.get(LOCK_KEY, {}).get(nombre)

    @staticmethod
    def _actualizar_lock(nombre: str, version: Optional[str]) -> None:
        """Actualiza la información de un módulo en el archivo lock.

        Args:
            nombre: Nombre del módulo
            version: Nueva versión del módulo
        """
        if not nombre:
            return
        try:
            with FileLock(f"{LOCK_FILE}.lock"):
                data = ModulesCommand._cargar_lock()
                data[LOCK_KEY][nombre] = version
                with open(LOCK_FILE, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
        except (IOError, yaml.YAMLError) as e:
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
                for m in mods:
                    mostrar_info(m)
            return 0
        except (ValueError, OSError) as e:
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _instalar_modulo(ruta: str) -> int:
        """Instala un módulo.

        Args:
            ruta: Ruta al archivo del módulo

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error
        """
        try:
            mod_validator.validar_mod(MODULE_MAP_PATH)

            if not ruta or not os.path.exists(ruta):
                mostrar_error(_("No se encontró el módulo {path}").format(path=ruta))
                return 1

            if os.path.islink(ruta) or not os.path.isfile(ruta) or not ruta.endswith(MODULE_EXTENSION):
                mostrar_error(_("Ruta de módulo inválida"))
                return 1

            nombre = os.path.basename(ruta)
            destino = os.path.join(MODULES_PATH, nombre)

            if os.path.exists(destino):
                if os.path.islink(destino):
                    mostrar_error(_("El destino {dest} es un enlace simbólico").format(dest=destino))
                    return 1

            try:
                shutil.copy2(ruta, destino)
            except (shutil.Error, IOError) as e:
                mostrar_error(_("Error al copiar módulo: {err}").format(err=str(e)))
                return 1

            mostrar_info(_("Módulo instalado en {dest}").format(dest=destino))

            version = ModulesCommand._obtener_version(ruta)
            if version and not es_version_valida(version):
                mostrar_error(_("Versión de módulo inválida"))
                return 1

            actual = ModulesCommand._obtener_version_lock(nombre)
            if actual and version and not es_nueva_version(version, actual):
                mostrar_error(
                    _("La nueva versión {v} no supera a {a}").format(v=version, a=actual)
                )
                return 1

            ModulesCommand._actualizar_lock(nombre, version)
            return 0

        except Exception as e:
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _remover_modulo(nombre: str) -> int:
        """Elimina un módulo instalado.

        Args:
            nombre: Nombre del módulo a eliminar

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error
        """
        if not nombre:
            mostrar_error(_("Debe especificar el nombre del módulo"))
            return 1

        try:
            archivo = os.path.join(MODULES_PATH, nombre)
            if not os.path.exists(archivo):
                mostrar_error(_("El módulo {name} no existe").format(name=nombre))
                return 1

            try:
                os.remove(archivo)
            except OSError as e:
                mostrar_error(_("Error al eliminar módulo: {err}").format(err=str(e)))
                return 1

            mostrar_info(_("Módulo {name} eliminado").format(name=nombre))

            with FileLock(f"{LOCK_FILE}.lock"):
                data = ModulesCommand._cargar_lock()
                if nombre in data.get(LOCK_KEY, {}):
                    del data[LOCK_KEY][nombre]
                    with open(LOCK_FILE, "w", encoding="utf-8") as f:
                        yaml.safe_dump(data, f)
            return 0

        except Exception as e:
            mostrar_error(str(e))
            return 1

    @staticmethod
    def _buscar_modulo(nombre: str) -> int:
        """Busca y descarga un módulo desde CobraHub.

        Args:
            nombre: Nombre del módulo a buscar

        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error
        """
        if not nombre:
            mostrar_error(_("Debe especificar el nombre del módulo"))
            return 1

        try:
            destino = os.path.join(MODULES_PATH, nombre)
            ok = descargar_modulo(nombre, destino)
            if ok:
                ModulesCommand._actualizar_lock(nombre, None)
            return 0 if ok else 1
        except Exception as e:
            mostrar_error(str(e))
            return 1