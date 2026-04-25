import logging
import os
import shutil
import sys
from importlib import import_module
from pathlib import Path
from typing import Iterable, List, Optional

if __package__ in {None, ""}:
    # Permite ejecutar ``python src/pcobra/cli.py`` sin errores de importación.
    paquete_raiz = Path(__file__).resolve().parent.parent
    ruta_paquete = str(paquete_raiz)
    if ruta_paquete not in sys.path:
        sys.path.insert(0, ruta_paquete)
    __package__ = "pcobra"

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - rama dependiente del entorno
    load_dotenv = None

logger = logging.getLogger(__name__)
_CLI_BOOTSTRAP_PATH_ENV = "PCOBRA_CLI_BOOTSTRAP_PATH"
_CLI_BOOTSTRAP_PATH_ENV_ALIAS = "COBRA_CLI_BOOTSTRAP_PATH"
_DEFAULT_DB_PATH = str(Path("~/.cobra/sqliteplus/core.db").expanduser())
_ENV_FILE = Path(".env")
_ENV_EXAMPLE_FILE = Path(".env.example")
_LEGACY_SHIM_ALIAS_CONTRACT = {
    # Siempre preservamos el módulo canónico para los wrappers legacy.
    "always": ("pcobra.cli",),
    # Alias adicionales que se registran únicamente para rutas legacy concretas.
    "cli.cli": ("cli", "cli.cli"),
    "cobra.cli.cli": (),
}

# Habilita imports de submódulos canónicos como ``pcobra.cli.commands`` y
# ``pcobra.cli.cli`` sin reemplazar ``pcobra.cli`` por otro objeto.
_CANONICAL_CLI_PACKAGE_DIR = Path(__file__).resolve().parent / "cobra" / "cli"
if _CANONICAL_CLI_PACKAGE_DIR.is_dir():
    __path__ = [str(_CANONICAL_CLI_PACKAGE_DIR)]


def configure_encoding() -> None:
    import sys
    import os

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.environ["PYTHONIOENCODING"] = "utf-8"


def configure_logging(debug: bool) -> None:
    """Configura logging de CLI con un único handler efectivo de consola.

    Contrato de logging del proyecto:
    - El *único* ``StreamHandler`` de consola vive en el logger raíz.
    - Los módulos (incluido ``pcobra`` y sus submódulos) **no** deben adjuntar
      handlers locales; sólo deben obtener su logger con ``getLogger(__name__)``
      y propagar al root.
    """

    level = logging.DEBUG if debug else logging.WARNING
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for existing_handler in list(root_logger.handlers):
        root_logger.removeHandler(existing_handler)
        existing_handler.close()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    app_logger = logging.getLogger("pcobra")
    app_logger.handlers = []
    app_logger.setLevel(logging.NOTSET)
    app_logger.propagate = True


def _activar_compatibilidad_legacy_si_corresponde(ruta_modulo: str) -> None:
    """Activa alias legacy mínimos solo para entrypoints heredados."""

    if ruta_modulo == "cli":
        # ``src/cli/__init__.py`` ya es el paquete legacy; no lo sustituimos.
        return

    if ruta_modulo == "cli.cli":
        sys.modules.setdefault("cli", sys.modules.get("cli", sys.modules[__name__]))
        sys.modules.setdefault("cli.cli", get_cli_module())


def build_legacy_cli_shim_main(ruta_modulo_legacy: str):
    """Construye ``main`` para wrappers legacy con un contrato único.

    Contrato de compatibilidad:
    - siempre registra ``pcobra.cli`` en ``sys.modules``;
    - aplica alias extra sólo para las rutas definidas en
      ``_LEGACY_SHIM_ALIAS_CONTRACT``.
    """

    import importlib

    aliases_extra = _LEGACY_SHIM_ALIAS_CONTRACT.get(ruta_modulo_legacy)
    if aliases_extra is None:
        rutas = ", ".join(
            sorted(k for k in _LEGACY_SHIM_ALIAS_CONTRACT if k != "always")
        )
        raise ValueError(
            f"Ruta legacy no soportada: {ruta_modulo_legacy!r}. Rutas válidas: {rutas}"
        )

    modulo_pcobra_cli = importlib.import_module("pcobra.cli")
    sys.modules.setdefault("pcobra.cli", modulo_pcobra_cli)
    modulo_pcobra_cli._activar_compatibilidad_legacy_si_corresponde(ruta_modulo_legacy)

    modulo_cli_canonico = get_cli_module()
    modulo_main = import_module("pcobra.cobra.cli.cli").main
    for alias in aliases_extra:
        if alias == "cli":
            sys.modules.setdefault(alias, sys.modules.get(alias, sys.modules[__name__]))
            continue
        if alias == "cli.cli":
            sys.modules.setdefault(alias, modulo_cli_canonico)
    return modulo_main


def _bootstrap_path_opt_in_value() -> str:
    """Resuelve el valor opt-in para bootstrap PATH con alias de compatibilidad."""

    valor_canonico = os.environ.get(_CLI_BOOTSTRAP_PATH_ENV)
    if valor_canonico is not None:
        return valor_canonico
    return os.environ.get(_CLI_BOOTSTRAP_PATH_ENV_ALIAS, "")


def _bootstrap_dev_path_si_opt_in() -> None:
    """Añade ``scripts/bin`` al PATH únicamente cuando se solicita explícitamente."""

    if _bootstrap_path_opt_in_value() != "1":
        return

    repo_root = Path(__file__).resolve().parents[2]
    bin_path = repo_root / "scripts" / "bin"
    if not bin_path.is_dir():
        logger.debug(
            "%s=1/%s=1 pero %s no existe; se omite bootstrap PATH",
            _CLI_BOOTSTRAP_PATH_ENV,
            _CLI_BOOTSTRAP_PATH_ENV_ALIAS,
            bin_path,
        )
        return

    current_path = os.environ.get("PATH", "")
    bin_path_text = str(bin_path)
    if bin_path_text in current_path.split(os.pathsep):
        return
    os.environ["PATH"] = (
        f"{bin_path_text}{os.pathsep}{current_path}" if current_path else bin_path_text
    )


def get_cli_module():
    """Carga diferida del entrypoint canónico ``pcobra.cli.cli``."""

    return import_module("pcobra.cli.cli")


def __getattr__(name: str):
    """Compatibilidad lazy para ``from pcobra.cli import cli``."""

    if name == "cli":
        return get_cli_module()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def configurar_entorno() -> None:
    """Carga variables de entorno y valida precondiciones críticas del runtime."""
    if not _ENV_FILE.exists() and _ENV_EXAMPLE_FILE.exists():
        shutil.copyfile(_ENV_EXAMPLE_FILE, _ENV_FILE)
        logger.info(
            "No se encontró .env; se creó automáticamente desde %s",
            _ENV_EXAMPLE_FILE,
        )

    if load_dotenv is None:
        logger.debug(
            "python-dotenv no está instalado; se omite la carga automática del archivo .env"
        )
    else:
        try:
            load_dotenv(dotenv_path=_ENV_FILE if _ENV_FILE.exists() else None)
        except OSError as exc:
            logger.error("No se pudo acceder al archivo .env: %s", exc)
            return
        except Exception:  # pragma: no cover - registro y propagación
            logger.exception("Error inesperado al cargar variables de entorno")
            raise

    if not (os.environ.get("SQLITE_DB_KEY") or "").strip():
        raise RuntimeError(
            "Falta SQLITE_DB_KEY en el entorno. Defínela en .env o en variables de entorno antes de ejecutar la CLI."
        )

    os.environ.setdefault("COBRA_DB_PATH", _DEFAULT_DB_PATH)


def _normalizar_argumentos(argumentos: Optional[Iterable[str]]) -> Optional[List[str]]:
    """Devuelve una copia de ``argumentos`` con alias habituales corregidos."""

    if argumentos is None:
        return None

    normalizados = list(argumentos)
    if not normalizados:
        return normalizados

    primer_argumento = normalizados[0].lower()
    if primer_argumento in {"ayuda", "help"}:
        normalizados[0:1] = ["--ayuda"]

    return normalizados


def _preprocesar_argumentos_cli(argumentos: Optional[Iterable[str]]) -> Optional[List[str]]:
    """Aplica saneamiento Unicode y normalización de alias a ``argumentos``."""
    from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input

    normalizados = _normalizar_argumentos(argumentos)
    if normalizados is None:
        return None
    return [sanitize_input(arg) for arg in normalizados]


def main(argumentos: Optional[List[str]] = None) -> int:
    """Punto de entrada principal para la ejecución del CLI."""
    configure_encoding()
    _bootstrap_dev_path_si_opt_in()
    argv_entrada: Iterable[str] = argumentos if argumentos is not None else sys.argv[1:]
    argv = _preprocesar_argumentos_cli(argv_entrada)
    debug = bool(argv and "--debug" in argv)
    configure_logging(debug=debug)
    if debug:
        os.environ["PCOBRA_DEBUG_TRACES"] = "1"
    else:
        os.environ.pop("PCOBRA_DEBUG_TRACES", None)

    flag_legacy_imports = argv is not None and "--legacy-imports" in argv
    env_legacy_imports = os.environ.get("PCOBRA_ENABLE_LEGACY_IMPORTS") == "1"
    if flag_legacy_imports:
        os.environ["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"

    if flag_legacy_imports or env_legacy_imports:
        from pcobra import activar_aliases_legacy

        activar_aliases_legacy()

    from .cobra.cli.cli import CliApplication

    try:
        configurar_entorno()
    except RuntimeError as exc:
        if debug:
            raise
        logger.error("%s", exc)
        return 1
    aplicacion = CliApplication()
    return aplicacion.run(argv)
