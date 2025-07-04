import importlib
import importlib.util
import subprocess
from pathlib import Path
import sys

# Lista blanca de paquetes que se pueden instalar con ``usar``.
USAR_WHITELIST: set[str] = set()


def obtener_modulo(nombre: str):
    """Importa y devuelve un módulo. Si no está instalado intenta
    instalarlo usando pip y lo importa nuevamente.
    """
    if not USAR_WHITELIST:
        raise PermissionError(
            "USAR_WHITELIST vacía: es necesario listar los paquetes permitidos"
        )
    if nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete '{nombre}' no permitido")

    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError:
        # Verificar si el módulo existe dentro de ``backend/corelibs``
        corelibs = Path(__file__).resolve().parents[2] / "corelibs"
        mod_path = corelibs / f"{nombre}.py"
        pkg_path = corelibs / nombre / "__init__.py"
        if mod_path.exists() or pkg_path.exists():
            ruta = mod_path if mod_path.exists() else pkg_path
            spec = importlib.util.spec_from_file_location(nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            sys.modules[nombre] = modulo
            spec.loader.exec_module(modulo)
            return modulo

        # Buscar también en ``standard_library``
        stdlib = Path(__file__).resolve().parents[2].parent / "standard_library"
        mod_path = stdlib / f"{nombre}.py"
        pkg_path = stdlib / nombre / "__init__.py"
        if mod_path.exists() or pkg_path.exists():
            ruta = mod_path if mod_path.exists() else pkg_path
            spec = importlib.util.spec_from_file_location(nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            sys.modules[nombre] = modulo
            spec.loader.exec_module(modulo)
            return modulo

        print(f"Paquete '{nombre}' no encontrado. Instalando...")
        try:
            subprocess.run(["pip", "install", nombre], check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Fallo al instalar '{nombre}': {exc}") from exc
        try:
            return importlib.import_module(nombre)
        except ModuleNotFoundError as exc:
            raise ImportError(
                f"No se pudo importar el módulo '{nombre}' tras la instalación"
            ) from exc
