"""Ejecución de código Python en un entorno restringido."""

import os
import marshal
import multiprocessing
import subprocess
import tempfile
from queue import Empty
from pathlib import Path
from packaging.version import Version

from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getattr
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
)
from RestrictedPython.PrintCollector import PrintCollector


MIN_VM2_VERSION = Version("3.9.19")


def _worker(code_bytes: bytes, queue: multiprocessing.Queue, memoria_mb: int | None) -> None:
    """Ejecuta ``code_bytes`` en un proceso aislado y comunica el resultado."""
    try:
        if memoria_mb is not None and os.name != "nt":
            import resource

            limite = memoria_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limite, limite))

        env = {
            "__builtins__": safe_builtins,
            "_print_": PrintCollector,
            "_getattr_": default_guarded_getattr,
            "_getitem_": default_guarded_getitem,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
        }

        byte_code = marshal.loads(code_bytes)
        exec(byte_code, env, env)
        queue.put(env["_print"]())
    except BaseException as exc:  # pragma: no cover - propagación de errores
        queue.put(exc)


def ejecutar_en_sandbox(
    codigo: str, timeout: int = 5, memoria_mb: int | None = None
) -> str:
    """Ejecuta una cadena de código Python de forma segura.

    El código se compila con :func:`compile_restricted` y se ejecuta en un
    proceso hijo. ``timeout`` especifica el tiempo límite en segundos y
    ``memoria_mb`` el máximo de memoria en megabytes. Se lanza ``TimeoutError``
    o ``MemoryError`` si se exceden estos límites.
    """
    try:
        byte_code = compile_restricted(codigo, "<string>", "exec")
    except SyntaxError as se:  # pragma: no cover - comportamiento simple
        raise SyntaxError(f"compile_restricted falló: {se}") from se

    code_bytes = marshal.dumps(byte_code)
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_worker, args=(code_bytes, queue, memoria_mb))
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        raise TimeoutError("Tiempo de ejecución agotado")

    try:
        resultado = queue.get_nowait()
    except Empty:  # pragma: no cover - no debería ocurrir
        raise RuntimeError("Fallo desconocido en sandbox")

    if isinstance(resultado, BaseException):
        raise resultado
    return resultado


def ejecutar_en_sandbox_js(codigo: str, timeout: int = 5) -> str:
    """Ejecuta código JavaScript de forma aislada usando Node.

    Utiliza ``vm2`` para crear un entorno seguro que no expone objetos como
    ``process`` o ``require``. ``timeout`` especifica el tiempo límite en
    segundos para la ejecución. ``vm2`` debe mantenerse actualizado; se
    comprueba que la versión instalada sea al menos ``3.9.19``.
    """
    import json
    import os

    env = os.environ.copy()
    env.pop("NODE_OPTIONS", None)
    env.pop("NODE_PATH", None)

    try:
        version = subprocess.run(
            ["node", "-e", "console.log(require('vm2/package.json').version)"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("vm2 no disponible") from exc

    vm2_version = Version(version.stdout.strip())
    if vm2_version < MIN_VM2_VERSION:
        raise RuntimeError(
            f"vm2 {vm2_version} es vulnerable; se requiere {MIN_VM2_VERSION} o superior"
        )

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
            [
                "node",
                "--no-experimental-fetch",
                "--max-old-space-size=128",
                tmp_path,
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=base_dir,
            timeout=timeout,
            env=env,
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

    El contenedor se lanza sin acceso a la red (``--network=none``), como el
    usuario ``nobody`` (``--user 65534:65534``), con el sistema de archivos en
    modo solo lectura (``--read-only`` y ``--tmpfs /tmp``) y sin capacidades
    adicionales (``--cap-drop=ALL``). Además, se aplican límites de recursos
    mediante ``--pids-limit`` y ``--memory`` para evitar abusos del sistema.
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
                "--user", "65534:65534",
                "--read-only",
                "--tmpfs", "/tmp",
                "--cap-drop=ALL",
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
        try:
            comun = os.path.commonpath([base, abs_path])
        except ValueError:
            raise ValueError(f"Ruta no permitida: {ruta}") from None
        if comun != base:
            raise ValueError(f"Ruta no permitida: {ruta}")
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Dependencia no encontrada: {ruta}")


class SecurityError(Exception):
    pass
