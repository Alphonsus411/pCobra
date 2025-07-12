"""Ejecución de código Python en un entorno restringido."""

import os
import subprocess
import tempfile
from pathlib import Path

from RestrictedPython import compile_restricted, safe_builtins
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
    try:
        byte_code = compile_restricted(codigo, "<string>", "exec")
    except SyntaxError:
        byte_code = compile(codigo, "<string>", "exec")
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


def ejecutar_en_sandbox_js(codigo: str) -> str:
    """Ejecuta código JavaScript de forma aislada usando Node.

    El código se serializa para evitar inyección de comandos cuando se pasa a
    la opción ``-e`` de Node.
    """
    import json
    import os

    codigo_serializado = json.dumps(codigo)
    script = r"""
const vm = require('vm');
let output = '';
const console = { log: (msg) => { output += String(msg) + '\n'; } };
const codigo = CODE;
vm.runInNewContext(codigo, { console });
process.stdout.write(output);
""".replace("CODE", codigo_serializado)

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
        tmp.write(script)
        tmp_path = tmp.name
    base_dir = Path(__file__).resolve().parent

    try:
        proc = subprocess.run(
            ["node", tmp_path], capture_output=True, text=True, check=True, cwd=base_dir
        )
        return proc.stdout
    finally:
        os.unlink(tmp_path)


def compilar_en_sandbox_cpp(codigo: str) -> str:
    """Compila y ejecuta código C++ de forma segura."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "main.cpp"
        src.write_text(codigo)
        exe = Path(tmpdir) / "a.out"
        subprocess.run([
            "g++",
            "-std=c++17",
            str(src),
            "-o",
            str(exe),
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
        return proc.stdout


def ejecutar_en_contenedor(codigo: str, backend: str) -> str:
    """Ejecuta ``codigo`` dentro de un contenedor Docker según ``backend``.

    Los backends soportados son ``python``, ``js``, ``cpp`` y ``rust``. Cada
    backend utiliza una imagen específica que debe estar construida
    previamente.
    """

    imagenes = {
        "python": "cobra-python-sandbox",
        "js": "cobra-js-sandbox",
        "cpp": "cobra-cpp-sandbox",
        "rust": "cobra-rust-sandbox",
    }

    if backend not in imagenes:
        raise ValueError(f"Backend no soportado: {backend}")

    try:
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", imagenes[backend]],
            input=codigo,
            text=True,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "Docker no está instalado o no se encuentra en PATH"
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip()) from e

    return proc.stdout


def validar_dependencias(backend: str, mod_info: dict) -> None:
    """Verifica que las rutas de *mod_info* para *backend* existan y sean seguras."""
    if not mod_info:
        return
    base = os.getcwd()
    for mod, data in mod_info.items():
        ruta = data.get(backend)
        if not ruta:
            continue
        abs_path = os.path.abspath(ruta)
        if not abs_path.startswith(base):
            raise ValueError(f"Ruta no permitida: {ruta}")
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Dependencia no encontrada: {ruta}")
