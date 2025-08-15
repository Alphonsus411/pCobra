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

    Devuelve la salida producida por ``print`` o lanza ``SyntaxError`` si
    la compilación segura falla. El código se compila con
    :func:`compile_restricted` y, de tener éxito, se ejecuta usando
    ``exec``.  Este paso implica riesgo, por lo que **no** se intenta
    recompilar con ``compile``. Mantén el diccionario ``env`` lo más
    reducido posible para minimizar la superficie de ataque.
    """
    try:
        byte_code = compile_restricted(codigo, "<string>", "exec")
    except SyntaxError as se:  # pragma: no cover - comportamiento simple
        raise SyntaxError(f"compile_restricted falló: {se}") from se

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


def ejecutar_en_sandbox_js(codigo: str, timeout: int = 5) -> str:
    """Ejecuta código JavaScript de forma aislada usando Node.

    Utiliza ``vm2`` para crear un entorno seguro que no expone objetos como
    ``process`` o ``require``. ``timeout`` especifica el tiempo límite en
    segundos para la ejecución.
    """
    import json
    import os

    codigo_serializado = json.dumps(codigo)
    script = f"""
const {{ NodeVM }} = require('vm2');
let output = '';
const vm = new NodeVM({{
    console: 'redirect',
    sandbox: {{ process: undefined }},
    timeout: {timeout * 1000},
    eval: false,
    wasm: false,
    require: false,
    env: {{}},
}});
vm.on('console.log', (msg) => {{ output += String(msg) + '\\n'; }});
vm.run('delete global.process;');
try {{
    vm.run({codigo_serializado});
}} catch (err) {{
    output += String(err);
}}
process.stdout.write(output);
"""

    base_dir = Path(__file__).resolve().parent
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, dir=base_dir) as tmp:
        tmp.write(script)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            ["node", "--no-experimental-fetch", tmp_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=base_dir,
            timeout=timeout,
        )  # nosec B603
        return proc.stdout
    except subprocess.CalledProcessError as exc:
        return exc.stderr or f"Error: {exc}"
    except subprocess.TimeoutExpired:
        return "Error: tiempo de ejecuci\u00f3n agotado"
    finally:
        os.unlink(tmp_path)


def compilar_en_sandbox_cpp(codigo: str) -> str:
    """Compila y ejecuta código C++ de forma segura utilizando Docker.

    Si el contenedor ``cobra-cpp-sandbox`` no está disponible o Docker no está
    instalado se lanza ``RuntimeError`` con un mensaje descriptivo.
    """
    try:
        return ejecutar_en_contenedor(codigo, "cpp")
    except RuntimeError as exc:
        raise RuntimeError(f"Contenedor de C++ no disponible: {exc}") from exc


def ejecutar_en_contenedor(
    codigo: str, backend: str, timeout: int | None = 30
) -> str:
    """Ejecuta ``codigo`` dentro de un contenedor Docker según ``backend``.

    Los backends soportados son ``python``, ``js``, ``cpp`` y ``rust``. Cada
    backend utiliza una imagen específica que debe estar construida
    previamente. ``timeout`` define el límite de tiempo en segundos para la
    ejecución del contenedor.

    El contenedor se lanza sin acceso a la red (``--network=none``) y con
    límites de recursos básicos mediante ``--pids-limit`` y ``--memory`` para
    evitar abusos del sistema.
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
            [
                "docker",
                "run",
                "--rm",
                "--network=none",
                "--pids-limit=128",
                "--memory=256m",
                "-i",
                imagenes[backend],
            ],
            input=codigo,
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout,
        )  # nosec B607 B603
    except FileNotFoundError as e:
        raise RuntimeError("Docker no está instalado o no se encuentra en PATH") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip()) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Tiempo de ejecución agotado") from e

    return proc.stdout


def validar_dependencias(backend: str, mod_info: dict) -> None:
    """Verifica que las rutas de *mod_info* para *backend* existan y sean seguras."""
    if not mod_info:
        return
    base = os.path.realpath(os.getcwd())
    for mod, data in mod_info.items():
        ruta = data.get(backend)
        if not ruta:
            continue
        abs_path = os.path.realpath(ruta)
        if os.path.commonpath([base, abs_path]) != base:
            raise ValueError(f"Ruta no permitida: {ruta}")
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Dependencia no encontrada: {ruta}")


class SecurityError(Exception):
    pass
