"""Utilidades deterministas para ejecutar procesos externos.

El modo predeterminado evita el shell del sistema.  Activar ``shell=True`` es
riesgoso porque delega el análisis del comando al intérprete de órdenes y puede
habilitar expansión de variables, comodines, tuberías o inyección de comandos si
la entrada no es confiable.
"""

from __future__ import annotations

import asyncio
import shlex
import subprocess
from collections.abc import Sequence
from typing import Any

ResultadoProceso = dict[str, int | str]

__all__ = [
    "ejecutar",
    "capturar",
    "ejecutar_async",
    "ejecutar_stream",
    "codigo_salida",
    "salida",
    "errores",
]


def _normalizar_argumentos(argumentos: Sequence[object] | None) -> list[str]:
    if argumentos is None:
        return []
    if isinstance(argumentos, (str, bytes)):
        raise TypeError("argumentos debe ser una secuencia explícita, no texto plano")
    return [str(argumento) for argumento in argumentos]


def _preparar_comando(
    comando: str | Sequence[object],
    *,
    argumentos: Sequence[object] | None,
    shell: bool,
) -> str | list[str]:
    args = _normalizar_argumentos(argumentos)

    if shell:
        if not isinstance(comando, str):
            raise TypeError("con shell=True, comando debe ser texto explícito")
        if args:
            argumentos_escapados = " ".join(
                shlex.quote(argumento) for argumento in args
            )
            return f"{comando} {argumentos_escapados}"
        return comando

    if isinstance(comando, str):
        if not comando:
            raise ValueError("comando no puede estar vacío")
        return [comando, *args]

    if isinstance(comando, (bytes, bytearray)):
        raise TypeError("comando debe ser str o una lista explícita de argumentos")

    lista = [str(parte) for parte in comando]
    if not lista:
        raise ValueError("comando no puede estar vacío")
    if args:
        raise ValueError(
            "argumentos solo puede usarse cuando comando es str con shell=False"
        )
    return lista


def _resultado(codigo: int, stdout: str = "", stderr: str = "") -> ResultadoProceso:
    return {"codigo": codigo, "salida": stdout, "error": stderr}


def ejecutar(
    comando: str | Sequence[object],
    *,
    argumentos: Sequence[object] | None = None,
    shell: bool = False,
    autorizar_shell: bool = False,
    cwd: str | None = None,
    entorno: dict[str, str] | None = None,
    timeout: int | float | None = None,
) -> ResultadoProceso:
    """Ejecuta un proceso y devuelve ``codigo``, ``salida`` y ``error``.

    Por defecto usa ``shell=False`` y pasa una lista explícita a
    :func:`subprocess.run`, sin expansión de shell.  En ese modo ``comando``
    puede ser una ruta/nombre de ejecutable como ``str`` acompañado de
    ``argumentos`` explícitos, o una secuencia completa como
    ``["python", "--version"]``.

    ``shell=True`` debe solicitarse de forma explícita.  Es riesgoso: permite
    que el shell interprete metacaracteres, expansión de variables, tuberías y
    redirecciones, por lo que no debe usarse con entradas no confiables.

    Los comandos inexistentes y los timeouts no lanzan excepciones de
    ``subprocess``: se transforman en resultados deterministas con códigos
    ``127`` y ``124`` respectivamente.
    """

    if not isinstance(shell, bool) or not isinstance(autorizar_shell, bool):
        raise TypeError("shell y autorizar_shell deben ser booleanos")
    if shell and not autorizar_shell:
        raise PermissionError("shell=True requiere autorizar_shell=True explícito")
    comando_preparado = _preparar_comando(comando, argumentos=argumentos, shell=shell)
    try:
        completado = subprocess.run(
            comando_preparado,
            shell=shell,
            cwd=cwd,
            env=entorno,
            timeout=timeout,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _resultado(
            124,
            stdout=(exc.stdout or ""),
            stderr=(exc.stderr or "Tiempo de espera agotado"),
        )
    except FileNotFoundError as exc:
        return _resultado(127, stderr=f"Comando no encontrado: {exc.filename}")
    except OSError as exc:
        return _resultado(126, stderr=str(exc))

    return _resultado(completado.returncode, completado.stdout, completado.stderr)


def capturar(
    comando: str | Sequence[object],
    *,
    argumentos: Sequence[object] | None = None,
    shell: bool = False,
    autorizar_shell: bool = False,
    cwd: str | None = None,
    entorno: dict[str, str] | None = None,
    timeout: int | float | None = None,
) -> ResultadoProceso:
    """Alias explícito de :func:`ejecutar` para capturar salida y errores."""

    return ejecutar(
        comando,
        argumentos=argumentos,
        shell=shell,
        autorizar_shell=autorizar_shell,
        cwd=cwd,
        entorno=entorno,
        timeout=timeout,
    )


async def ejecutar_async(
    comando: str | Sequence[object],
    **opciones: Any,
) -> ResultadoProceso:
    """Ejecuta sin bloquear el bucle de eventos, con el mismo contrato seguro."""

    return await asyncio.to_thread(ejecutar, comando, **opciones)


async def ejecutar_stream(
    comando: str | Sequence[object],
    **opciones: Any,
):
    """Produce por líneas la salida capturada de un proceso terminado."""

    resultado = await ejecutar_async(comando, **opciones)
    for linea in str(resultado["salida"]).splitlines(keepends=True):
        yield linea


def codigo_salida(resultado: dict[str, Any]) -> int:
    """Devuelve el código de salida de una estructura de resultado."""

    return int(resultado.get("codigo", 0))


def salida(resultado: dict[str, Any]) -> str:
    """Devuelve la salida estándar de una estructura de resultado."""

    return str(resultado.get("salida", ""))


def errores(resultado: dict[str, Any]) -> str:
    """Devuelve la salida de error de una estructura de resultado."""

    return str(resultado.get("error", ""))
