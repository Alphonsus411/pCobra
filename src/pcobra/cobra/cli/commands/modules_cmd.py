import logging
import os
import shutil
from argparse import ArgumentParser
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - dependencias opcionales
    from filelock import FileLock
except ModuleNotFoundError:  # pragma: no cover - entornos sin filelock
    FileLock = None  # type: ignore[assignment]

try:  # pragma: no cover - dependencia opcional
    import yaml
except ModuleNotFoundError:  # pragma: no cover - entornos sin PyYAML
    yaml = None  # type: ignore[assignment]
from pcobra.cobra.semantico import mod_validator
from pcobra.cobra.transpilers.module_map import MODULE_MAP_PATH
from pcobra.cobra.cli.cobrahub_client import CobraHubClient
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.semver import es_nueva_version, es_version_valida

# Configuración de logging
logger = logging.getLogger(__name__)

# Cliente de CobraHub (inicializado bajo demanda)
_client: Optional[CobraHubClient] = None


def _get_client() -> CobraHubClient:
    """Obtiene una instancia única del cliente de CobraHub."""
    global _client
    if _client is None:
        _client = CobraHubClient()
    return _client


class _ClientProxy:
    """Proxy perezoso para exponer el cliente de CobraHub."""

    def __getattr__(self, name: str) -> Any:
        return getattr(_get_client(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(_get_client(), name, value)


client = _ClientProxy()

# Constantes
USER_CONFIG_DIR = Path.home() / ".cobra"
MODULES_PATH: Path = USER_CONFIG_DIR / "modules"
LOCK_FILE: Path = USER_CONFIG_DIR / "module_map.toml"
LOCK_KEY = "lock"
MODULE_EXTENSION = ".co"


def _lock_context(path: Path):
    if FileLock is None:
        return nullcontext()
    return FileLock(f"{path}.lock")


def _ensure_modules_dir() -> bool:
    """Garantiza que el directorio de módulos existe y es accesible."""

    modules_dir = Path(MODULES_PATH)
    try:
        modules_dir.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError as exc:
        logger.error(f"Sin permisos para crear directorio de módulos: {exc}")
        mostrar_error(
            _(
                "No se pudo preparar el directorio de módulos en {ruta}: {err}"
            ).format(ruta=modules_dir, err=str(exc))
        )
    except OSError as exc:
        logger.error(f"Error al preparar directorio de módulos: {exc}")
        mostrar_error(
            _(
                "Error al preparar el directorio de módulos en {ruta}: {err}"
            ).format(ruta=modules_dir, err=str(exc))
        )
    return False


def _ensure_lock_parent() -> bool:
    """Garantiza que existe el directorio del archivo de lock."""

    lock_path = Path(LOCK_FILE)
    lock_parent = lock_path.parent
    try:
        lock_parent.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError as exc:
        logger.error(f"Sin permisos para preparar lock de módulos: {exc}")
        mostrar_error(
            _("No se pudo preparar el archivo de lock en {ruta}: {err}").format(
                ruta=lock_parent, err=str(exc)
            )
        )
    except OSError as exc:
        logger.error(f"Error al preparar lock de módulos: {exc}")
        mostrar_error(
            _("Error al preparar el archivo de lock en {ruta}: {err}").format(
                ruta=lock_parent, err=str(exc)
            )
        )
    return False

class ModulesCommand(BaseCommand):
    """Gestiona los módulos instalados."""

    name = "modulos"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
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

        if yaml is None and accion in {"publicar", "buscar"}:
            mostrar_error(
                _(
                    "El comando de módulos requiere la dependencia opcional 'PyYAML' "
                    "para la acción solicitada."
                )
            )
            return 1

        acciones = {
            "listar": self._listar_modulos,
            "instalar": lambda: self._instalar_modulo(args.ruta),
            "remover": lambda: self._remover_modulo(args.nombre),
            "publicar": lambda: 0 if _get_client().publicar_modulo(args.ruta) else 1,
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
        if yaml is None:
            mostrar_error(
                _(
                    "La lectura de versiones de módulos requiere la dependencia 'PyYAML'."
                )
            )
            return None

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
        if yaml is None:
            mostrar_error(
                _("La gestión del archivo lock requiere la dependencia 'PyYAML'.")
            )
            return {LOCK_KEY: {}}

        try:
            lock_path = Path(LOCK_FILE)
            if lock_path.exists():
                with _lock_context(lock_path):
                    with open(lock_path, "r", encoding="utf-8") as f:
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
        if yaml is None:
            mostrar_error(
                _(
                    "Actualizar el lock de módulos requiere la dependencia 'PyYAML'."
                )
            )
            return

        if not nombre or not ModulesCommand._validar_nombre_modulo(nombre):
            return
        if not _ensure_lock_parent():
            return

        try:
            lock_path = Path(LOCK_FILE)
            with _lock_context(lock_path):
                data = ModulesCommand._cargar_lock()
                data[LOCK_KEY][nombre] = version
                with open(lock_path, "w", encoding="utf-8") as f:
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
            modules_dir = Path(MODULES_PATH)
            if not modules_dir.exists():
                mostrar_info(_("No hay módulos instalados"))
                return 0

            mods = [
                f.name
                for f in modules_dir.iterdir()
                if f.is_file() and f.name.endswith(MODULE_EXTENSION)
            ]
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

            if yaml is not None:
                mod_validator.validar_mod(MODULE_MAP_PATH)
            ruta_abs = os.path.abspath(ruta)

            if not os.path.exists(ruta_abs):
                raise ValueError(_("No se encontró el módulo {path}").format(path=ruta))

            if os.path.islink(ruta_abs) or not os.path.isfile(ruta_abs) or not ruta.endswith(MODULE_EXTENSION):
                raise ValueError(_("Ruta de módulo inválida"))

            nombre = os.path.basename(ruta_abs)
            if not ModulesCommand._validar_nombre_modulo(nombre):
                raise ValueError(_("Nombre de módulo inválido"))

            if not _ensure_modules_dir():
                return 1

            modules_dir = Path(MODULES_PATH)
            destino = modules_dir / nombre
            if destino.exists() and destino.is_symlink():
                raise ValueError(_("El destino {dest} es un enlace simbólico").format(dest=destino))

            try:
                shutil.copy2(ruta_abs, destino)
            except PermissionError as exc:
                raise ValueError(
                    _("Sin permisos para copiar a {dest}: {err}").format(
                        dest=destino, err=str(exc)
                    )
                ) from exc
            except OSError as exc:
                raise ValueError(
                    _("No se pudo copiar el módulo a {dest}: {err}").format(
                        dest=destino, err=str(exc)
                    )
                ) from exc
            mostrar_info(_("Módulo instalado en {dest}").format(dest=destino))

            version = None
            if yaml is not None:
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
            if not _ensure_modules_dir():
                return 1

            modules_dir = Path(MODULES_PATH)
            archivo = modules_dir / nombre
            if not archivo.exists():
                raise ValueError(_("El módulo {name} no existe").format(name=nombre))

            try:
                archivo.unlink()
            except OSError as e:
                raise ValueError(_("Error al eliminar módulo: {err}").format(err=str(e)))

            mostrar_info(_("Módulo {name} eliminado").format(name=nombre))

            if yaml is not None:
                if not _ensure_lock_parent():
                    return 1

                lock_path = Path(LOCK_FILE)
                with _lock_context(lock_path):
                    data = ModulesCommand._cargar_lock()
                    if nombre in data.get(LOCK_KEY, {}):
                        del data[LOCK_KEY][nombre]
                        with open(lock_path, "w", encoding="utf-8") as f:
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
            if not _ensure_modules_dir():
                return 1

            modules_dir = Path(MODULES_PATH).resolve()
            destino = str((modules_dir / nombre).resolve(strict=False))
            ok = _get_client().descargar_modulo(
                nombre, destino, base_permitida=str(modules_dir)
            )
            if ok:
                ModulesCommand._actualizar_lock(nombre, None)
            return 0 if ok else 1
        except Exception as e:
            logger.error(f"Error al buscar módulo: {str(e)}")
            mostrar_error(str(e))
            return 1
