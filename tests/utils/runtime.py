"""Utilidades para ejecutar código en distintos lenguajes durante los tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Dict

import pytest

from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js
from tests.utils.targets import EXPERIMENTAL_RUNTIME_TARGETS, OFFICIAL_RUNTIME_TARGETS


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


_RUNNERS: Dict[str, Callable[[str], str]] = {
    "python": _run_python,
    "javascript": _run_js,
    "go": _run_go,
    "rust": _run_rust,
}


def run_code(lang: str, code: str) -> str:
    """Ejecuta *code* en el lenguaje indicado y devuelve la salida estándar.

    Parameters
    ----------
    lang: str
        Identificador del lenguaje (por ejemplo ``"python"`` o ``"javascript"``).
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
    if lang in {"python", "javascript"}:
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


def execute_transpiled_code(
    lang: str,
    code: str,
    tmp_path: Path,
    *,
    allow_experimental: bool = False,
) -> str:
    """Ejecuta código transpilado respetando la política oficial de runtime.

    Por defecto solo permite el runtime oficial definido por
    ``pcobra.cobra.cli.target_policies``. Los runtimes ``go`` y ``java`` se
    conservan únicamente como cobertura experimental/best-effort.
    """
    if lang == "python":
        src = tmp_path / "prog.py"
        src.write_text(code)
        env = os.environ.copy()
        pythonpath_entries = [
            str(Path(__file__).resolve().parents[2]),
            str(Path(__file__).resolve().parents[2] / "src"),
        ]
        current_pythonpath = env.get("PYTHONPATH")
        if current_pythonpath:
            pythonpath_entries.append(current_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
        try:
            proc = subprocess.run(
                [shutil.which("python") or "python", str(src)],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
        except subprocess.CalledProcessError as exc:
            if exc.returncode == -9:
                pytest.skip("python finalizado por SIGKILL del entorno durante la ejecución")
            raise
        return proc.stdout

    if lang == "javascript":
        if not shutil.which("node"):
            pytest.skip("node no disponible")
        return run_code(lang, code)

    if lang == "cpp":
        comp = shutil.which("g++")
        if not comp:
            pytest.skip("g++ no disponible")
        src = tmp_path / "prog.cpp"
        src.write_text(code)
        exe = tmp_path / "prog"
        subprocess.run([comp, str(src), "-o", str(exe)], check=True)
        proc = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
        return proc.stdout

    if lang == "rust":
        comp = shutil.which("rustc")
        if not comp:
            pytest.skip("rustc no disponible")
        src = tmp_path / "prog.rs"
        src.write_text(code)
        exe = tmp_path / "prog"
        subprocess.run([comp, str(src), "-o", str(exe)], check=True)
        proc = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
        return proc.stdout

    if lang in EXPERIMENTAL_RUNTIME_TARGETS and not allow_experimental:
        pytest.skip(
            f"{lang} se conserva solo como runtime experimental/best-effort; "
            "no forma parte del contrato oficial"
        )

    if lang == "go":
        comp = shutil.which("go")
        if not comp:
            pytest.skip("go no disponible")
        src = tmp_path / "prog.go"
        src.write_text(code)
        proc = subprocess.run([comp, "run", str(src)], capture_output=True, text=True, check=True)
        return proc.stdout

    if lang == "java":
        comp = shutil.which("javac")
        if not comp:
            pytest.skip("javac no disponible")
        src = tmp_path / "Main.java"
        src.write_text(code)
        subprocess.run([comp, str(src)], cwd=tmp_path, check=True)
        proc = subprocess.run(
            ["java", "-cp", str(tmp_path), "Main"],
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout

    if lang in OFFICIAL_RUNTIME_TARGETS:
        pytest.fail(f"Falta implementar ejecución oficial para {lang}")

    pytest.skip(f"ejecución no soportada para {lang}")
