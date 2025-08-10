"""Utilidades para ejecutar código en distintos lenguajes durante los tests."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Dict

from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js


def _run_python(code: str) -> str:
    """Ejecuta código Python en la sandbox interna y devuelve la salida."""
    return ejecutar_en_sandbox(code)


def _run_js(code: str) -> str:
    """Ejecuta código JavaScript usando Node.js y devuelve la salida."""
    return ejecutar_en_sandbox_js(code)


def _run_go(code: str) -> str:
    """Compila y ejecuta código Go usando ``go run``."""
    with tempfile.NamedTemporaryFile("w", suffix=".go", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            ["go", "run", tmp_path], capture_output=True, text=True, check=True
        )
        return proc.stdout
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error simple
        return exc.stderr or f"Error: {exc}"
    finally:
        os.unlink(tmp_path)


def _run_rust(code: str) -> str:
    """Compila y ejecuta código Rust usando ``rustc``."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "main.rs"
        src.write_text(code)
        bin_path = Path(tmpdir) / "main"
        try:
            subprocess.run(
                ["rustc", str(src), "-o", str(bin_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            proc = subprocess.run(
                [str(bin_path)], capture_output=True, text=True, check=True
            )
            return proc.stdout
        except subprocess.CalledProcessError as exc:  # pragma: no cover - error simple
            return exc.stderr or f"Error: {exc}"


def _run_ruby(code: str) -> str:
    """Ejecuta código Ruby mediante el intérprete ``ruby``."""
    with tempfile.NamedTemporaryFile("w", suffix=".rb", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            ["ruby", tmp_path], capture_output=True, text=True, check=True
        )
        return proc.stdout
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error simple
        return exc.stderr or f"Error: {exc}"
    finally:
        os.unlink(tmp_path)


_RUNNERS: Dict[str, Callable[[str], str]] = {
    "python": _run_python,
    "js": _run_js,
    "go": _run_go,
    "rust": _run_rust,
    "ruby": _run_ruby,
}


def run_code(lang: str, code: str) -> str:
    """Ejecuta *code* en el lenguaje indicado y devuelve la salida estándar.

    Parameters
    ----------
    lang: str
        Identificador del lenguaje (por ejemplo ``"python"`` o ``"js"``).
    code: str
        Código fuente a ejecutar.

    Returns
    -------
    str
        Salida producida por el programa.

    Raises
    ------
    ValueError
        Si el lenguaje no está soportado.
    """
    try:
        runner = _RUNNERS[lang]
    except KeyError as exc:  # pragma: no cover - caso simple
        raise ValueError(f"Lenguaje no soportado: {lang}") from exc

    # Realiza una comprobación de sintaxis previa a la ejecución para los
    # lenguajes interpretados más comunes. Esto permite detectar errores de
    # forma explícita antes de invocar al *runner* correspondiente.
    if lang in {"python", "js"}:
        suffix = ".py" if lang == "python" else ".js"
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / f"snippet{suffix}"
            src.write_text(code)
            cmd = (
                ["python", "-m", "py_compile", str(src)]
                if lang == "python"
                else ["node", "--check", str(src)]
            )
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.strip()
                stdout = exc.stdout.strip()
                return f"Error de sintaxis: {stderr or stdout or exc}"

    return runner(code)

