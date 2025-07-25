"""Colección de utilidades estándar para Cobra."""

from .texto import mayusculas, minusculas, invertir, concatenar
from .numero import es_par, es_primo, factorial, promedio
from .archivo import leer, escribir, existe, eliminar
from .tiempo import ahora, formatear, dormir
from .coleccion import ordenar, maximo, minimo, sin_duplicados
from .seguridad import hash_sha256, generar_uuid
from .red import obtener_url, enviar_post
from .sistema import obtener_os, ejecutar, obtener_env, listar_dir

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
