import importlib
import importlib.util
import os
import re
import shlex
import subprocess
from pathlib import Path
import sys


# Intentamos cargar configuración dinámica desde cobra.toml
try:
    import tomli
except ImportError:
    tomli = None  # Tomli no es necesario en Python ≥ 3.11

USAR_WHITELIST: dict[str, str] = {}

# Nombre de la variable de entorno que habilita la instalación automática
USAR_INSTALL_ENV = "COBRA_USAR_INSTALL"

# Variable para habilitar specs flexibles (menos seguras) de forma explícita
USAR_INSTALL_UNSAFE_ENV = "COBRA_USAR_INSTALL_UNSAFE_SPECS"

# Regex de validación para los nombres de paquetes
_VALID_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")
_VALID_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+\-]*$")
_VALID_STRICT_SPEC_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_\-]+)"
    r"(?:(?:==(?P<pin>[A-Za-z0-9][A-Za-z0-9._+\-]*))"
    r"|(?:>=(?P<min>[A-Za-z0-9][A-Za-z0-9._+\-]*),<(?P<max>[A-Za-z0-9][A-Za-z0-9._+\-]*)))?$"
)
_URL_PREFIXES = ("http://", "https://", "git+", "file://")
_unsafe_warning_printed = False


def _validar_nombre(nombre: str) -> str:
    """Valida el nombre del paquete y devuelve una versión saneada.

    Se rechazan nombres con guiones iniciales, barras u otros caracteres
    sospechosos. Solo se permiten letras, dígitos, guiones y guiones bajos.
    """

    nombre = nombre.strip()
    if not _VALID_NAME_RE.fullmatch(nombre):
        raise ValueError(
            f"Nombre de paquete '{nombre}' contiene caracteres no permitidos"
        )
    if nombre.startswith("-") or "/" in nombre or "\\" in nombre:
        raise ValueError(f"Nombre de paquete '{nombre}' no es seguro")
    return nombre


def _parsear_entrada(entrada: str) -> tuple[str, str]:
    """Devuelve el nombre base y la especificación completa de la entrada."""

    entrada = entrada.strip()
    if not entrada:
        raise ValueError("Entrada vacía en lista blanca")

    if os.environ.get(USAR_INSTALL_UNSAFE_ENV):
        global _unsafe_warning_printed
        if not _unsafe_warning_printed:
            print(
                "ADVERTENCIA: modo inseguro de specs activado "
                f"({USAR_INSTALL_UNSAFE_ENV}=1). "
                "Se permiten argumentos avanzados de pip bajo tu propio riesgo."
            )
            _unsafe_warning_printed = True

        match = re.match(r"([A-Za-z0-9_\-]+)", entrada)
        if not match:
            raise ValueError(f"Entrada de paquete '{entrada}' inválida")
        nombre_base = _validar_nombre(match.group(1))
        return nombre_base, entrada

    tokens = [tok for tok in re.split(r"[\s,]+", entrada) if tok]
    for token in tokens:
        if token.startswith("-"):
            raise ValueError(
                f"Entrada de paquete '{entrada}' contiene flags no permitidos: '{token}'"
            )
        token_lower = token.lower()
        if token_lower.startswith(_URL_PREFIXES):
            raise ValueError(
                f"Entrada de paquete '{entrada}' contiene una URL directa no permitida"
            )

    if "@" in entrada:
        raise ValueError(f"Entrada de paquete '{entrada}' usa formato no permitido con '@'")
    if "#" in entrada:
        raise ValueError(f"Entrada de paquete '{entrada}' contiene hash no permitido")

    match = _VALID_STRICT_SPEC_RE.fullmatch(entrada)
    if not match:
        raise ValueError(
            f"Entrada de paquete '{entrada}' no cumple formato permitido: "
            "nombre | nombre==x.y.z | nombre>=x,<y"
        )

    nombre_base = _validar_nombre(match.group("name"))
    for version in (match.group("pin"), match.group("min"), match.group("max")):
        if version is not None and not _VALID_VERSION_RE.fullmatch(version):
            raise ValueError(f"Versión '{version}' no es válida en '{entrada}'")

    return nombre_base, entrada


def cargar_lista_blanca():
    """Carga la lista blanca de paquetes permitidos desde cobra.toml si existe"""
    global USAR_WHITELIST

    # Por defecto incluye paquetes clave del proyecto
    default_pkgs = [
        "numpy",
        "pandas",
        "requests",
        "matplotlib",
        "holobit-sdk",
        "agix",
    ]

    USAR_WHITELIST = {}
    for item in default_pkgs:
        nombre_base, spec = _parsear_entrada(item)
        USAR_WHITELIST[nombre_base] = spec

    # Cargar desde configuración si se encuentra en algún padre del archivo
    config_path = None
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "cobra.toml"
        if candidate.exists():
            config_path = candidate
            break

    if config_path and tomli:
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)
            permitidos = config.get("usar", {}).get("permitidos", [])
            if isinstance(permitidos, list):
                for item in permitidos:
                    nombre_base, spec = _parsear_entrada(item)
                    USAR_WHITELIST[nombre_base] = spec
        except Exception as e:
            print(f"Advertencia: no se pudo leer cobra.toml: {e}")


# Ejecutar al importar
cargar_lista_blanca()


def _cargar_modulo_local_desde_directorio(nombre: str, directorio: Path):
    """Carga un módulo Python desde un directorio local dado."""

    mod_path = directorio / f"{nombre}.py"
    pkg_path = directorio / nombre / "__init__.py"
    if not (mod_path.exists() or pkg_path.exists()):
        return None

    ruta = mod_path if mod_path.exists() else pkg_path
    mod_spec = importlib.util.spec_from_file_location(nombre, ruta)
    if mod_spec is None or mod_spec.loader is None:
        raise ImportError(f"No se pudo crear spec para el módulo '{nombre}'")
    modulo = importlib.util.module_from_spec(mod_spec)
    sys.modules[nombre] = modulo
    mod_spec.loader.exec_module(modulo)
    return modulo


def obtener_modulo_cobra_oficial(nombre: str):
    """Carga módulos oficiales de Cobra solo desde ``corelibs`` o ``standard_library``."""

    nombre = _validar_nombre(nombre)
    base = Path(__file__).resolve()

    for parent in base.parents:
        corelibs = parent / "corelibs"
        if corelibs.exists():
            modulo = _cargar_modulo_local_desde_directorio(nombre, corelibs)
            if modulo is not None:
                return modulo
            break

    for parent in base.parents:
        stdlib = parent / "standard_library"
        if stdlib.exists():
            modulo = _cargar_modulo_local_desde_directorio(nombre, stdlib)
            if modulo is not None:
                return modulo
            break

    raise ModuleNotFoundError(
        f"Módulo oficial Cobra '{nombre}' no encontrado en corelibs/standard_library"
    )


def obtener_modulo(nombre: str, *, permitir_instalacion: bool = True):
    """Importa y devuelve un módulo.

    Si el paquete no está instalado se intentará ejecutar ``pip install``
    siempre que la variable de entorno ``COBRA_USAR_INSTALL`` esté definida.
    De lo contrario se lanza :class:`RuntimeError`.
    """
    nombre = _validar_nombre(nombre)
    # Política runtime general: whitelist + resolver + import local/stdlib + pip opcional.
    if not USAR_WHITELIST:
        raise PermissionError(
            "La lista blanca de paquetes está vacía. No se puede usar 'usar'."
        )
    if nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete '{nombre}' no está permitido.")
    spec = USAR_WHITELIST[nombre]

    base = Path(__file__).resolve()
    from pcobra.cobra.imports.resolver import CobraImportResolver, ImportResolutionError

    resolver = CobraImportResolver(project_root=base.parents[3])
    try:
        _, module = resolver.load_module(nombre, fallback_backend="python")
    except ImportResolutionError:
        module = None
    else:
        if module is not None:
            return module

    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError:
        try:
            return obtener_modulo_cobra_oficial(nombre)
        except ModuleNotFoundError:
            pass

        # Si no se encontró, verificar si la instalación está permitida
        if not permitir_instalacion or not os.environ.get(USAR_INSTALL_ENV):
            raise RuntimeError(
                "Instalación automática no permitida. "
                f"Define {USAR_INSTALL_ENV}=1 para habilitarla."
            )

        print(f"Paquete '{spec}' no encontrado. Instalando con pip...")

        try:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
            ]

            if os.environ.get(USAR_INSTALL_UNSAFE_ENV):
                print(
                    "ADVERTENCIA: instalación en modo inseguro; "
                    "se aceptan argumentos avanzados de pip."
                )
                argumentos = shlex.split(spec)
            else:
                argumentos = [spec]

            cmd += argumentos
            subprocess.run(cmd, check=True)
            print(f"Paquete instalado: {spec}")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Fallo al instalar '{spec}': {exc}") from exc

        try:
            return importlib.import_module(nombre)
        except ModuleNotFoundError as exc:
            raise ImportError(
                f"No se pudo importar el módulo '{nombre}' tras la instalación"
            ) from exc
