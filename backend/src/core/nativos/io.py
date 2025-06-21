import urllib.request


def leer_archivo(ruta):
    """Devuelve el contenido de un archivo de texto."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def escribir_archivo(ruta, datos):
    """Escribe datos en un archivo de texto."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(datos)


def obtener_url(url):
    """Devuelve el contenido de una URL como texto."""
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")
