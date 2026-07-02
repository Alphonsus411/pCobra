"""Ejecución controlada de PyInstaller para CobraInstaller.

El módulo encapsula toda la interacción con PyInstaller para que las capas de
CLI/IDLE no tengan que pedir al usuario que invoque ``pyinstaller`` a mano.
Todas las llamadas a procesos pasan por ``subprocess`` y aceptan fábricas
inyectables, lo que permite mockearlas por completo en tests.
"""

from __future__ import annotations

import queue
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .project import CobraInstallerError

__all__ = [
    "PyInstallerInfo",
    "PyInstallerRunResult",
    "detect_pyinstaller",
    "install_pyinstaller_if_allowed",
    "run_pyinstaller",
]


@dataclass(frozen=True, slots=True)
class PyInstallerInfo:
    """Información detectada de PyInstaller."""

    available: bool
    version: str | None = None
    executable: str | None = None
    command: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PyInstallerRunResult:
    """Resultado de una ejecución de PyInstaller."""

    success: bool
    version: str
    returncode: int
    command: tuple[str, ...]
    stdout: str = ""
    stderr: str = ""


def detect_pyinstaller(
    *,
    run_factory: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    which: Callable[[str], str | None] = shutil.which,
) -> PyInstallerInfo:
    """Comprueba si PyInstaller está disponible y devuelve su versión.

    Primero intenta ejecutar ``python -m PyInstaller --version`` para no depender
    de que el binario ``pyinstaller`` esté en ``PATH``. Si falla, prueba el
    ejecutable localizado por ``shutil.which``. Los errores se convierten en un
    resultado ``available=False`` para que el llamador decida si puede instalar.
    """

    commands: list[tuple[str, ...]] = [(sys.executable, "-m", "PyInstaller", "--version")]
    executable = which("pyinstaller")
    if executable:
        commands.append((executable, "--version"))

    for command in commands:
        try:
            completed = run_factory(
                list(command),
                check=False,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, OSError):
            continue
        if completed.returncode == 0:
            version = _first_non_empty_line(completed.stdout, completed.stderr)
            if version:
                return PyInstallerInfo(
                    available=True,
                    version=version,
                    executable=executable,
                    command=command,
                )
    return PyInstallerInfo(available=False, executable=executable)


def install_pyinstaller_if_allowed(
    options: Any,
    logger: Any | None = None,
    *,
    run_factory: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PyInstallerInfo:
    """Instala PyInstaller solo cuando las opciones lo permiten.

    La instalación se habilita con cualquiera de estos atributos booleanos en
    ``options``: ``install_pyinstaller``, ``allow_pyinstaller_install`` o
    ``auto_install_pyinstaller``. Si PyInstaller ya existe no instala nada.
    """

    detected = detect_pyinstaller(run_factory=run_factory)
    if detected.available:
        return detected

    if not _option_enabled(
        options,
        "install_pyinstaller",
        "allow_pyinstaller_install",
        "auto_install_pyinstaller",
    ):
        raise CobraInstallerError(
            "PyInstaller no está instalado. Habilita la instalación automática "
            "en las opciones del build o instala la dependencia en el entorno."
        )

    _log(logger, "info", "PyInstaller no está disponible; instalando con pip...")
    command = [sys.executable, "-m", "pip", "install", "pyinstaller"]
    try:
        completed = run_factory(command, check=False, capture_output=True, text=True)
    except (FileNotFoundError, OSError) as exc:
        raise CobraInstallerError(
            f"No se pudo ejecutar pip para instalar PyInstaller: {exc}"
        ) from exc

    if completed.returncode != 0:
        detail = _translate_pyinstaller_error(completed.stderr or completed.stdout)
        raise CobraInstallerError(f"No se pudo instalar PyInstaller: {detail}")

    detected = detect_pyinstaller(run_factory=run_factory)
    if not detected.available:
        raise CobraInstallerError(
            "PyInstaller se instaló, pero no se pudo verificar su versión."
        )
    return detected


def run_pyinstaller(
    spec_path: str | Path,
    options: Any,
    logger: Any,
    *,
    popen_factory: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    run_factory: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PyInstallerRunResult:
    """Ejecuta PyInstaller sobre ``spec_path`` con salida en tiempo real."""

    spec = Path(spec_path).expanduser().resolve()
    if not spec.is_file():
        raise CobraInstallerError(f"El archivo spec de PyInstaller no existe: {spec}")

    info = install_pyinstaller_if_allowed(options, logger, run_factory=run_factory)
    version = info.version or "desconocida"
    command = [sys.executable, "-m", "PyInstaller", str(spec), *_extra_args(options)]
    _log(logger, "info", f"Ejecutando PyInstaller {version}: {' '.join(command)}")

    try:
        process = popen_factory(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except (FileNotFoundError, OSError) as exc:
        raise CobraInstallerError(f"No se pudo iniciar PyInstaller: {exc}") from exc

    stdout, stderr = _stream_process_output(process, logger)
    returncode = process.wait()
    if returncode != 0:
        message = _translate_pyinstaller_error(stderr or stdout)
        raise CobraInstallerError(f"PyInstaller falló con código {returncode}: {message}")

    return PyInstallerRunResult(
        success=True,
        version=version,
        returncode=returncode,
        command=tuple(command),
        stdout=stdout,
        stderr=stderr,
    )


def _stream_process_output(process: subprocess.Popen[str], logger: Any) -> tuple[str, str]:
    events: queue.Queue[tuple[str, str]] = queue.Queue()

    def reader(name: str, stream: Iterable[str] | None) -> None:
        if stream is None:
            return
        for line in stream:
            events.put((name, line))

    threads = [
        threading.Thread(target=reader, args=("stdout", process.stdout), daemon=True),
        threading.Thread(target=reader, args=("stderr", process.stderr), daemon=True),
    ]
    for thread in threads:
        thread.start()

    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    while any(thread.is_alive() for thread in threads):
        _drain_events(events, logger, stdout_parts, stderr_parts)
    for thread in threads:
        thread.join()
    _drain_events(events, logger, stdout_parts, stderr_parts)
    return "".join(stdout_parts), "".join(stderr_parts)


def _drain_events(
    events: queue.Queue[tuple[str, str]],
    logger: Any,
    stdout_parts: list[str],
    stderr_parts: list[str],
) -> None:
    while True:
        try:
            name, line = events.get_nowait()
        except queue.Empty:
            return
        if name == "stdout":
            stdout_parts.append(line)
            _log(logger, "info", line.rstrip("\n"))
        else:
            stderr_parts.append(line)
            _log(logger, "error", line.rstrip("\n"))


def _translate_pyinstaller_error(output: str) -> str:
    text = output.strip()
    lowered = text.lower()
    if not text:
        return "PyInstaller no devolvió detalles del error."
    if "no module named pyinstaller" in lowered:
        return "PyInstaller no está instalado o no es importable en este intérprete de Python."
    if "permission denied" in lowered or "access is denied" in lowered:
        return (
            "Permiso denegado al leer/escribir archivos del build. "
            "Revisa permisos y antivirus."
        )
    if "file not found" in lowered or "no such file or directory" in lowered:
        return "Falta un archivo requerido por el spec o por los recursos del proyecto."
    if "syntaxerror" in lowered:
        return "PyInstaller encontró un error de sintaxis en el spec o en el código incluido."
    if "recursion" in lowered and "maximum" in lowered:
        return (
            "PyInstaller agotó el límite de recursión; revisa imports circulares "
            "o aumenta el límite en el spec."
        )
    if "failed to execute script" in lowered:
        return (
            "El ejecutable generado no pudo iniciar el script empaquetado. "
            "Revisa imports y datos incluidos."
        )
    return text


def _extra_args(options: Any) -> tuple[str, ...]:
    raw = getattr(options, "extra_args", ()) if options is not None else ()
    if isinstance(raw, str):
        return (raw,)
    return tuple(str(value) for value in raw)


def _option_enabled(options: Any, *names: str) -> bool:
    if options is None:
        return False
    if isinstance(options, Mapping):
        return any(bool(options.get(name)) for name in names)
    return any(bool(getattr(options, name, False)) for name in names)


def _first_non_empty_line(*chunks: str | None) -> str | None:
    for chunk in chunks:
        for line in (chunk or "").splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
    return None


def _log(logger: Any | None, level: str, message: str) -> None:
    if logger is None:
        return
    method = getattr(logger, level, None) or getattr(logger, "write", None)
    if callable(method):
        method(message)
