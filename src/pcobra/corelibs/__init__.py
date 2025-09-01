"""Colección de utilidades estándar para Cobra."""

from corelibs.texto import mayusculas, minusculas, invertir, concatenar
from corelibs.numero import es_par, es_primo, factorial, promedio
from corelibs.archivo import leer, escribir, existe, eliminar
from corelibs.tiempo import ahora, formatear, dormir
from corelibs.coleccion import ordenar, maximo, minimo, sin_duplicados
from corelibs.seguridad import hash_sha256, generar_uuid
from corelibs.red import obtener_url, enviar_post
from corelibs.sistema import obtener_os, ejecutar, obtener_env, listar_dir

__all__ = [
    "mayusculas",
    "minusculas",
    "invertir",
    "concatenar",
    "es_par",
    "es_primo",
    "factorial",
    "promedio",
    "leer",
    "escribir",
    "existe",
    "eliminar",
    "ahora",
    "formatear",
    "dormir",
    "ordenar",
    "maximo",
    "minimo",
    "sin_duplicados",
    "hash_sha256",
    "generar_uuid",
    "obtener_url",
    "enviar_post",
    "obtener_os",
    "ejecutar",
    "obtener_env",
    "listar_dir",
]
