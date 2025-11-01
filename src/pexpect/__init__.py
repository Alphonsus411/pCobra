"""Implementación ligera de :mod:`pexpect` para entornos limitados.

Esta versión minimalista proporciona la funcionalidad necesaria para las
pruebas de integración del proyecto sin requerir la dependencia externa.
Solo implementa un subconjunto reducido de la API real: ``spawn``,
``expect``, ``sendline`` y ``wait`` junto con la constante ``EOF``. El
objetivo es ofrecer compatibilidad básica para escenarios interactivos en
línea de comandos, utilizando ``subprocess`` detrás de escena.
"""

from __future__ import annotations

import queue
import shlex
import subprocess
import threading
import time
from collections.abc import Sequence
from typing import Any, Optional, Union


class _EOFType:
    """Sentinela que representa el final del flujo de salida."""

    def __repr__(self) -> str:  # pragma: no cover - representación trivial
        return "<PEXPECT_EOF>"


EOF = _EOFType()


class TIMEOUT(RuntimeError):
    """Excepción lanzada cuando se supera el tiempo de espera."""


class spawn:
    """Proceso interactivo simplificado inspirado en :class:`pexpect.spawn`."""

    def __init__(
        self,
        command: Union[str, Sequence[str]],
        *,
        env: Optional[dict[str, str]] = None,
        encoding: str = "utf-8",
        timeout: float = 5.0,
    ) -> None:
        self.timeout = timeout
        self._encoding = encoding
        if isinstance(command, str):
            cmd = shlex.split(command)
        else:
            cmd = [
                arg.decode(encoding) if isinstance(arg, bytes) else str(arg)
                for arg in command
            ]
        self._process = subprocess.Popen(
            cmd,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            encoding=encoding,
            bufsize=1,
        )
        self.before = ""
        self.after = ""
        self.exitstatus: Optional[int] = None
        self._buffer = ""
        self._queue: "queue.Queue[str | None]" = queue.Queue()
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()

    # Compatibilidad con la API real: atributo alias
    child_fd = None  # pragma: no cover - mantenido por compatibilidad

    def _read_stdout(self) -> None:
        """Lee el flujo del proceso y lo coloca en la cola interna."""

        assert self._process.stdout is not None
        while True:
            chunk = self._process.stdout.read(1)
            if chunk == "" and self._process.poll() is not None:
                break
            if chunk:
                self._queue.put(chunk)
        self._queue.put(None)

    def sendline(self, data: str) -> None:
        """Escribe ``data`` seguido de un salto de línea en el proceso."""

        if self._process.stdin is None:
            raise RuntimeError("El proceso no tiene stdin disponible")
        self._process.stdin.write(data + "\n")
        self._process.stdin.flush()

    def expect(self, pattern: Any, timeout: Optional[float] = None) -> int:
        """Espera a que aparezca ``pattern`` en la salida del proceso."""

        deadline = time.monotonic() + (timeout if timeout is not None else self.timeout)

        if pattern is EOF:
            while True:
                if self._process.poll() is not None:
                    self.exitstatus = self._process.returncode
                    return 0
                if time.monotonic() > deadline:
                    raise TIMEOUT("Expiró el tiempo de espera esperando EOF")
                time.sleep(0.05)

        while True:
            index = self._buffer.find(pattern)
            if index != -1:
                end = index + len(pattern)
                self.before = self._buffer[:index]
                self.after = self._buffer[index:end]
                self._buffer = self._buffer[end:]
                return index

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TIMEOUT(f"No se encontró el patrón {pattern!r} en la salida")

            try:
                chunk = self._queue.get(timeout=remaining)
            except queue.Empty as exc:  # pragma: no cover - protección adicional
                raise TIMEOUT("No se recibió salida del proceso a tiempo") from exc

            if chunk is None:
                self.exitstatus = self._process.poll()
                raise EOFError("El proceso finalizó antes de encontrar el patrón")

            self._buffer += chunk

    def wait(self, timeout: Optional[float] = None) -> int:
        """Bloquea hasta que el proceso termine y devuelve su código de salida."""

        try:
            self.exitstatus = self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover - caso excepcional
            raise TIMEOUT("El proceso no terminó en el tiempo esperado") from exc
        return self.exitstatus


__all__ = ["EOF", "spawn", "TIMEOUT"]

