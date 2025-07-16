import os
import shutil
import yaml
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from ..utils.semver import es_version_valida, es_nueva_version
from ..cobrahub_client import publicar_modulo, descargar_modulo
from cobra.transpilers.module_map import MODULE_MAP_PATH
from cobra.semantico import mod_validator

MODULES_PATH = os.path.join(os.path.dirname(__file__), "..", "modules")
os.makedirs(MODULES_PATH, exist_ok=True)
LOCK_FILE = MODULE_MAP_PATH
LOCK_KEY = "lock"


class ModulesCommand(BaseCommand):
    """Gestiona los módulos instalados."""

    name = "modulos"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Gestiona módulos instalados"))
        mod_sub = parser.add_subparsers(dest="accion")
        mod_sub.add_parser("listar", help=_("Lista módulos"))
        inst = mod_sub.add_parser("instalar", help=_("Instala un módulo"))
        inst.add_argument("ruta")
        rem = mod_sub.add_parser("remover", help=_("Elimina un módulo"))
        rem.add_argument("nombre")
        pub = mod_sub.add_parser("publicar", help=_("Publica un módulo en CobraHub"))
        pub.add_argument("ruta")
        bus = mod_sub.add_parser("buscar", help=_("Descarga un módulo desde CobraHub"))
        bus.add_argument("nombre")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        accion = args.accion
        if accion == "listar":
            return self._listar_modulos()
        elif accion == "instalar":
            return self._instalar_modulo(args.ruta)
        elif accion == "remover":
            return self._remover_modulo(args.nombre)
        elif accion == "publicar":
            return 0 if publicar_modulo(args.ruta) else 1
        elif accion == "buscar":
            destino = os.path.join(MODULES_PATH, args.nombre)
            ok = descargar_modulo(args.nombre, destino)
            if ok:
                ModulesCommand._actualizar_lock(args.nombre, None)
            return 0 if ok else 1
        else:
            mostrar_error(_("Acción de módulos no reconocida"))
            return 1

    @staticmethod
    def _obtener_version(ruta: str):
        if os.path.exists(MODULE_MAP_PATH):
            with open(MODULE_MAP_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for mod_path, info in data.items():
                if mod_path == LOCK_KEY:
                    continue
                if os.path.basename(mod_path) == os.path.basename(ruta):
                    return info.get("version")
        return None

    @staticmethod
    def _cargar_lock() -> dict:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        data.setdefault(LOCK_KEY, {})
        return data

    @staticmethod
    def _obtener_version_lock(nombre: str) -> str | None:
        data = ModulesCommand._cargar_lock()
        return data.get(LOCK_KEY, {}).get(nombre)

    @staticmethod
    def _actualizar_lock(nombre: str, version: str | None):
        data = ModulesCommand._cargar_lock()
        data[LOCK_KEY][nombre] = version
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

    @staticmethod
    def _listar_modulos():
        try:
            mod_validator.validar_mod(MODULE_MAP_PATH)
        except ValueError as e:
            mostrar_error(str(e))
            return 1
        mods = [f for f in os.listdir(MODULES_PATH) if f.endswith(".co")]
        if not mods:
            mostrar_info(_("No hay módulos instalados"))
        else:
            for m in mods:
                mostrar_info(m)
        return 0

    @staticmethod
    def _instalar_modulo(ruta):
        try:
            mod_validator.validar_mod(MODULE_MAP_PATH)
        except ValueError as e:
            mostrar_error(str(e))
            return 1
        if not os.path.exists(ruta):
            mostrar_error(_("No se encontró el módulo {path}").format(path=ruta))
            return 1
        destino = os.path.join(MODULES_PATH, os.path.basename(ruta))
        shutil.copy(ruta, destino)
        mostrar_info(_("Módulo instalado en {dest}").format(dest=destino))
        version = ModulesCommand._obtener_version(ruta)
        if version and not es_version_valida(version):
            mostrar_error(_("Versión de módulo inválida"))
            return 1
        nombre = os.path.basename(ruta)
        actual = ModulesCommand._obtener_version_lock(nombre)
        if actual and version and not es_nueva_version(version, actual):
            mostrar_error(
                _("La nueva versión {v} no supera a {a}").format(v=version, a=actual)
            )
            return 1
        ModulesCommand._actualizar_lock(nombre, version)
        return 0

    @staticmethod
    def _remover_modulo(nombre):
        archivo = os.path.join(MODULES_PATH, nombre)
        if os.path.exists(archivo):
            os.remove(archivo)
            mostrar_info(_("Módulo {name} eliminado").format(name=nombre))
            data = ModulesCommand._cargar_lock()
            if nombre in data.get(LOCK_KEY, {}):
                del data[LOCK_KEY][nombre]
                with open(LOCK_FILE, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
            return 0
        else:
            mostrar_error(_("El módulo {name} no existe").format(name=nombre))
            return 1
