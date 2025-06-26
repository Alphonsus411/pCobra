"""Ejecución de código Python en un entorno restringido."""

from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
)
from RestrictedPython.PrintCollector import PrintCollector


def ejecutar_en_sandbox(codigo: str) -> str:
    """Ejecuta una cadena de código Python de forma segura.

    Devuelve la salida producida por ``print`` o lanza una excepción si
    se intenta realizar una operación prohibida.
    """
    byte_code = compile_restricted(codigo, "<string>", "exec")
    env = {
        "__builtins__": safe_builtins,
        "_print_": PrintCollector,
        "_getattr_": getattr,
        "_getitem_": default_guarded_getitem,
        "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
        "_unpack_sequence_": guarded_unpack_sequence,
    }

    exec(byte_code, env, env)
    return env["_print"]()
