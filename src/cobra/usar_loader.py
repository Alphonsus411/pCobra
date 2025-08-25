import importlib
import importlib.util
import os
import re
import subprocess
from pathlib import Path
import sys

# Intentamos cargar configuración dinámica desde pcobra.toml
try:
    import tomli
except ImportError:
    tomli = None  # Tomli no es necesario en Python ≥ 3.11

USAR_WHITELIST: dict[str, str] = {}

# Nombre de la variable de entorno que habilita la instalación automática
USAR_INSTALL_ENV = "COBRA_USAR_INSTALL"

# Regex de validación para los nombres de paquetes
_VALID_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


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
    match = re.match(r"([A-Za-z0-9_\-]+)", entrada)
    if not match:
        raise ValueError(f"Entrada de paquete '{entrada}' inválida")
    nombre_base = _validar_nombre(match.group(1))
    return nombre_base, entrada


def cargar_lista_blanca():
    """Carga la lista blanca de paquetes permitidos desde pcobra.toml si existe"""
    global USAR_WHITELIST

    # Por defecto incluye paquetes clave del proyecto
    default_pkgs = [
        "numpy",
        "pandas",
        "requests",
        "matplotlib",
        "holobit-sdk",
        "smooth-criminal",
        "agix",
    ]

    USAR_WHITELIST = {}
    for item in default_pkgs:
        nombre_base, spec = _parsear_entrada(item)
        USAR_WHITELIST[nombre_base] = spec

    # Cargar desde configuración si se encuentra
    config_path = Path(__file__).resolve().parent.parent.parent / "pcobra.toml"
    if config_path.exists() and tomli:
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)
            permitidos = config.get("usar", {}).get("permitidos", [])
            if isinstance(permitidos, list):
                for item in permitidos:
                    nombre_base, spec = _parsear_entrada(item)
                    USAR_WHITELIST[nombre_base] = spec
        except Exception as e:
            print(f"Advertencia: no se pudo leer pcobra.toml: {e}")


# Ejecutar al importar
cargar_lista_blanca()


def obtener_modulo(nombre: str):
    """Importa y devuelve un módulo.

    Si el paquete no está instalado se intentará ejecutar ``pip install``
    siempre que la variable de entorno ``COBRA_USAR_INSTALL`` esté definida.
    De lo contrario se lanza :class:`RuntimeError`.
    """
    nombre = _validar_nombre(nombre)
    if not USAR_WHITELIST:
        raise PermissionError(
            "La lista blanca de paquetes está vacía. No se puede usar 'usar'."
        )
    if nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete '{nombre}' no está permitido.")
    spec = USAR_WHITELIST[nombre]

    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError:
        # Buscar primero en corelibs
        base = Path(__file__).resolve()
        for parent in base.parents:
            corelibs = parent / "corelibs"
            if corelibs.exists():
                mod_path = corelibs / f"{nombre}.py"
                pkg_path = corelibs / nombre / "__init__.py"
                if mod_path.exists() or pkg_path.exists():
                    ruta = mod_path if mod_path.exists() else pkg_path
                    mod_spec = importlib.util.spec_from_file_location(nombre, ruta)
                    modulo = importlib.util.module_from_spec(mod_spec)
                    sys.modules[nombre] = modulo
                    mod_spec.loader.exec_module(modulo)
                    return modulo
                break

        # Buscar también en standard_library
        for parent in base.parents:
            stdlib = parent / "standard_library"
            if stdlib.exists():
                mod_path = stdlib / f"{nombre}.py"
                pkg_path = stdlib / nombre / "__init__.py"
                if mod_path.exists() or pkg_path.exists():
                    ruta = mod_path if mod_path.exists() else pkg_path
                    mod_spec = importlib.util.spec_from_file_location(nombre, ruta)
                    modulo = importlib.util.module_from_spec(mod_spec)
                    sys.modules[nombre] = modulo
                    mod_spec.loader.exec_module(modulo)
                    return modulo
                break

        # Si no se encontró, verificar si la instalación está permitida
        if not os.environ.get(USAR_INSTALL_ENV):
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
                "--require-hashes",
            ] + spec.split()
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
