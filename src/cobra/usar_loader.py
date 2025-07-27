import importlib
import importlib.util
import os
import subprocess
from pathlib import Path
import sys

# Intentamos cargar configuración dinámica desde pcobra.toml
try:
    import tomli
except ImportError:
    tomli = None  # Tomli no es necesario en Python ≥ 3.11

USAR_WHITELIST: set[str] = set()

# Nombre de la variable de entorno que habilita la instalación automática
USAR_INSTALL_ENV = "COBRA_USAR_INSTALL"


def cargar_lista_blanca():
    """Carga la lista blanca de paquetes permitidos desde pcobra.toml si existe"""
    global USAR_WHITELIST

    # Por defecto incluye paquetes clave del proyecto
    USAR_WHITELIST = {
        "numpy",
        "pandas",
        "requests",
        "matplotlib",
        "holobit-sdk",
        "smooth-criminal",
        "agix",
    }

    # Cargar desde configuración si se encuentra
    config_path = Path(__file__).resolve().parent.parent.parent / "pcobra.toml"
    if config_path.exists() and tomli:
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)
            permitidos = config.get("usar", {}).get("permitidos", [])
            if isinstance(permitidos, list):
                USAR_WHITELIST.update(permitidos)
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
    if not USAR_WHITELIST:
        raise PermissionError(
            "La lista blanca de paquetes está vacía. No se puede usar 'usar'."
        )
    if nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete '{nombre}' no está permitido.")

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
                    spec = importlib.util.spec_from_file_location(nombre, ruta)
                    modulo = importlib.util.module_from_spec(spec)
                    sys.modules[nombre] = modulo
                    spec.loader.exec_module(modulo)
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
                    spec = importlib.util.spec_from_file_location(nombre, ruta)
                    modulo = importlib.util.module_from_spec(spec)
                    sys.modules[nombre] = modulo
                    spec.loader.exec_module(modulo)
                    return modulo
                break

        # Si no se encontró, verificar si la instalación está permitida
        if not os.environ.get(USAR_INSTALL_ENV):
            raise RuntimeError(
                "Instalación automática no permitida. "
                f"Define {USAR_INSTALL_ENV}=1 para habilitarla."
            )

        print(f"Paquete '{nombre}' no encontrado. Instalando con pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", nombre], check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Fallo al instalar '{nombre}': {exc}") from exc

        try:
            return importlib.import_module(nombre)
        except ModuleNotFoundError as exc:
            raise ImportError(
                f"No se pudo importar el módulo '{nombre}' tras la instalación"
            ) from exc
