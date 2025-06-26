import importlib
import subprocess

# Lista blanca de paquetes que se pueden instalar con ``usar``.
USAR_WHITELIST: set[str] = set()


def obtener_modulo(nombre: str):
    """Importa y devuelve un módulo. Si no está instalado intenta
    instalarlo usando pip y lo importa nuevamente.
    """
    if USAR_WHITELIST and nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete '{nombre}' no permitido")

    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError:
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
