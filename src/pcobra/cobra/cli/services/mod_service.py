import logging
import os
import shutil
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, Optional

from pcobra.cobra.cli.cobrahub_client import CobraHubClient
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.contracts import ModRequest, normalize_mod_request
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.semver import es_nueva_version, es_version_valida
from pcobra.cobra.semantico import mod_validator
from pcobra.cobra.transpilers.module_map import MODULE_MAP_PATH

try:  # pragma: no cover
    from filelock import FileLock
except ModuleNotFoundError:  # pragma: no cover
    FileLock = None  # type: ignore[assignment]

try:  # pragma: no cover
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)
_client: Optional[CobraHubClient] = None

USER_CONFIG_DIR = Path.home() / ".cobra"
MODULES_PATH: Path = USER_CONFIG_DIR / "modules"
LOCK_FILE: Path = USER_CONFIG_DIR / "module_map.toml"
LOCK_KEY = "lock"
MODULE_EXTENSION = ".co"


def get_client() -> CobraHubClient:
    global _client
    if _client is None:
        _client = CobraHubClient()
    return _client


def lock_context(path: Path):
    if FileLock is None:
        return nullcontext()
    return FileLock(f"{path}.lock")


def ensure_modules_dir() -> bool:
    modules_dir = Path(MODULES_PATH)
    try:
        modules_dir.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError as exc:
        logger.error("Sin permisos para crear directorio de módulos: %s", exc)
        mostrar_error(_("No se pudo preparar el directorio de módulos en {ruta}: {err}").format(ruta=modules_dir, err=str(exc)))
    except OSError as exc:
        logger.error("Error al preparar directorio de módulos: %s", exc)
        mostrar_error(_("Error al preparar el directorio de módulos en {ruta}: {err}").format(ruta=modules_dir, err=str(exc)))
    return False


def ensure_lock_parent() -> bool:
    lock_parent = Path(LOCK_FILE).parent
    try:
        lock_parent.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError as exc:
        logger.error("Sin permisos para preparar lock de módulos: %s", exc)
        mostrar_error(_("No se pudo preparar el archivo de lock en {ruta}: {err}").format(ruta=lock_parent, err=str(exc)))
    except OSError as exc:
        logger.error("Error al preparar lock de módulos: %s", exc)
        mostrar_error(_("Error al preparar el archivo de lock en {ruta}: {err}").format(ruta=lock_parent, err=str(exc)))
    return False


def validar_nombre_modulo(nombre: str) -> bool:
    return bool(nombre and not any(c in nombre for c in r'<>:"/\\|?*'))


def validar_ruta(ruta: str) -> bool:
    try:
        ruta_abs = os.path.abspath(ruta)
        return not any(parte.startswith(".") for parte in Path(ruta_abs).parts)
    except Exception:
        return False


def cargar_lock() -> Dict:
    data: Dict = {}
    if yaml is None:
        mostrar_error(_("La gestión del archivo lock requiere la dependencia 'PyYAML'."))
        return {LOCK_KEY: {}}

    try:
        lock_path = Path(LOCK_FILE)
        if lock_path.exists():
            with lock_context(lock_path):
                with open(lock_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
    except (IOError, yaml.YAMLError) as e:
        logger.error("Error al cargar lock: %s", e)
        mostrar_error(_("Error al cargar lock: {err}").format(err=str(e)))
    data.setdefault(LOCK_KEY, {})
    return data


def obtener_version_lock(nombre: str) -> Optional[str]:
    if not nombre or not validar_nombre_modulo(nombre):
        return None
    data = cargar_lock()
    return data.get(LOCK_KEY, {}).get(nombre)


def actualizar_lock(nombre: str, version: Optional[str]) -> None:
    if yaml is None:
        mostrar_error(_("Actualizar el lock de módulos requiere la dependencia 'PyYAML'."))
        return

    if not nombre or not validar_nombre_modulo(nombre):
        return
    if not ensure_lock_parent():
        return

    try:
        lock_path = Path(LOCK_FILE)
        with lock_context(lock_path):
            data = cargar_lock()
            data[LOCK_KEY][nombre] = version
            with open(lock_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f)
    except (IOError, yaml.YAMLError) as e:
        logger.error("Error al actualizar lock: %s", e)
        mostrar_error(_("Error al actualizar lock: {err}").format(err=str(e)))


def obtener_version(ruta: str) -> Optional[str]:
    if yaml is None:
        mostrar_error(_("La lectura de versiones de módulos requiere la dependencia 'PyYAML'."))
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
        logger.error("Error al leer versión: %s", e)
        mostrar_error(_("Error al leer versión: {err}").format(err=str(e)))
    return None


class ModService:
    def run(self, request: ModRequest) -> int:
        try:
            request = normalize_mod_request(request)
        except ValueError as err:
            mostrar_error(str(err))
            return 1

        accion = request.accion

        if yaml is None and accion in {"publicar", "buscar"}:
            mostrar_error(_("El comando de módulos requiere la dependencia opcional 'PyYAML' para la acción solicitada."))
            return 1

        acciones = {
            "listar": listar_modulos,
            "instalar": lambda: instalar_modulo(request.ruta),
            "remover": lambda: remover_modulo(request.nombre),
            "publicar": lambda: 0 if get_client().publicar_modulo(request.ruta) else 1,
            "buscar": lambda: buscar_modulo(request.nombre),
        }

        try:
            if accion not in acciones:
                raise ValueError(_("Acción de módulos no reconocida"))
            return acciones[accion]()
        except Exception as e:
            logger.error("Error en comando de módulos: %s", e)
            mostrar_error(str(e))
            return 1


def listar_modulos() -> int:
    try:
        mod_validator.validar_mod(MODULE_MAP_PATH)
        modules_dir = Path(MODULES_PATH)
        if not modules_dir.exists():
            mostrar_info(_("No hay módulos instalados"))
            return 0

        mods = [f.name for f in modules_dir.iterdir() if f.is_file() and f.name.endswith(MODULE_EXTENSION)]
        if not mods:
            mostrar_info(_("No hay módulos instalados"))
        else:
            for m in sorted(mods):
                mostrar_info(m)
        return 0
    except (ValueError, OSError) as e:
        logger.error("Error al listar módulos: %s", e)
        mostrar_error(str(e))
        return 1


def instalar_modulo(ruta: str) -> int:
    try:
        if not validar_ruta(ruta):
            raise ValueError(_("Ruta de módulo inválida"))

        if yaml is not None:
            mod_validator.validar_mod(MODULE_MAP_PATH)
        ruta_abs = os.path.abspath(ruta)

        if not os.path.exists(ruta_abs):
            raise ValueError(_("No se encontró el módulo {path}").format(path=ruta))

        if os.path.islink(ruta_abs) or not os.path.isfile(ruta_abs) or not ruta.endswith(MODULE_EXTENSION):
            raise ValueError(_("Ruta de módulo inválida"))

        nombre = os.path.basename(ruta_abs)
        if not validar_nombre_modulo(nombre):
            raise ValueError(_("Nombre de módulo inválido"))

        if not ensure_modules_dir():
            return 1

        modules_dir = Path(MODULES_PATH)
        destino = modules_dir / nombre
        if destino.exists() and destino.is_symlink():
            raise ValueError(_("El destino {dest} es un enlace simbólico").format(dest=destino))

        try:
            shutil.copy2(ruta_abs, destino)
        except PermissionError as exc:
            raise ValueError(_("Sin permisos para copiar a {dest}: {err}").format(dest=destino, err=str(exc))) from exc
        except OSError as exc:
            raise ValueError(_("No se pudo copiar el módulo a {dest}: {err}").format(dest=destino, err=str(exc))) from exc
        mostrar_info(_("Módulo instalado en {dest}").format(dest=destino))

        version = None
        if yaml is not None:
            version = obtener_version(ruta_abs)
            if version and not es_version_valida(version):
                raise ValueError(_("Versión de módulo inválida"))

            actual = obtener_version_lock(nombre)
            if actual and version and not es_nueva_version(version, actual):
                raise ValueError(_("La nueva versión {v} no supera a {a}").format(v=version, a=actual))

            actualizar_lock(nombre, version)
        return 0

    except Exception as e:
        logger.error("Error al instalar módulo: %s", e)
        mostrar_error(str(e))
        return 1


def remover_modulo(nombre: str) -> int:
    if not nombre or not validar_nombre_modulo(nombre):
        mostrar_error(_("Nombre de módulo inválido"))
        return 1

    try:
        if not ensure_modules_dir():
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
            if not ensure_lock_parent():
                return 1

            lock_path = Path(LOCK_FILE)
            with lock_context(lock_path):
                data = cargar_lock()
                if nombre in data.get(LOCK_KEY, {}):
                    del data[LOCK_KEY][nombre]
                    with open(lock_path, "w", encoding="utf-8") as f:
                        yaml.safe_dump(data, f)
        return 0

    except Exception as e:
        logger.error("Error al remover módulo: %s", e)
        mostrar_error(str(e))
        return 1


def buscar_modulo(nombre: str) -> int:
    if not nombre or not validar_nombre_modulo(nombre):
        mostrar_error(_("Nombre de módulo inválido"))
        return 1

    try:
        if not ensure_modules_dir():
            return 1

        modules_dir = Path(MODULES_PATH).resolve()
        destino = str((modules_dir / nombre).resolve(strict=False))
        ok = get_client().descargar_modulo(nombre, destino, base_permitida=str(modules_dir))
        if ok:
            actualizar_lock(nombre, None)
        return 0 if ok else 1
    except Exception as e:
        logger.error("Error al buscar módulo: %s", e)
        mostrar_error(str(e))
        return 1
