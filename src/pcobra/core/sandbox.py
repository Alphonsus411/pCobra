"""Ejecución de código Python en un entorno restringido."""

import os
import marshal
import multiprocessing
import shutil
import subprocess
import tempfile
import string
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

# Límite máximo de salida permitida en la sandbox de JS (8 KB)
MAX_JS_OUTPUT_BYTES = 8 * 1024

# Límite máximo de salida permitida para la ejecución en contenedores (8 KB)
MAX_CONTAINER_OUTPUT_BYTES = 8 * 1024


def _worker(
    code_bytes: bytes, queue: multiprocessing.Queue, memoria_mb: int | None
) -> None:
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


def ejecutar_en_sandbox_js(
    codigo: str,
    timeout: int = 5,
    env_vars: dict[str, str] | None = None,
    memoria_mb: int | None = 128,
) -> str:
    """Ejecuta código JavaScript de forma aislada usando Node.

    Utiliza ``vm2`` para crear un entorno seguro que no expone objetos como
    ``process`` o ``require``. ``timeout`` especifica el tiempo límite en
    segundos para la ejecución. ``vm2`` debe mantenerse actualizado; se
    comprueba que la versión instalada sea al menos ``3.9.19``. La sandbox
    se ejecuta con un entorno minimizado cuyo ``PATH`` apunta únicamente a
    ``/usr/bin`` o al directorio que contiene el ejecutable de Node; se pueden
    añadir variables específicas mediante ``env_vars``. ``memoria_mb`` limita
    la memoria disponible para la ejecución de Node estableciendo
    ``--max-old-space-size``.
    """
    import json
    import os

    node_path = shutil.which("node")
    env_path = os.path.dirname(node_path) if node_path else "/usr/bin"
    env = {"PATH": env_path}
    if env_vars:
        claves_sensibles = {
            "PATH",
            "NODE_OPTIONS",
            "NODE_PATH",
            "LD_PRELOAD",
            "LD_LIBRARY_PATH",
        }
        prefijos_sensibles = ("LD_",)
        allowed = set(string.ascii_letters + string.digits + "_")
        filtradas = {
            k: v
            for k, v in env_vars.items()
            if all(c in allowed for c in k)
            and k not in claves_sensibles
            and not any(k.startswith(pref) for pref in prefijos_sensibles)
        }
        env.update(filtradas)

    try:
        version = subprocess.run(
            [node_path, "-e", "console.log(require('vm2/package.json').version)"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
    except (TypeError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("vm2 no disponible") from exc

    vm2_version = Version(version.stdout.strip())
    if vm2_version < MIN_VM2_VERSION:
        raise RuntimeError(
            f"vm2 {vm2_version} es vulnerable; se requiere {MIN_VM2_VERSION} o superior"
        )

    codigo_serializado = json.dumps(codigo)
    timeout_ms = "undefined" if timeout is None else str(int(timeout * 1000))
    script = f"""
const {{ NodeVM }} = require('vm2');
let output = '';
const vm = new NodeVM({{
    console: 'redirect',
    sandbox: {{ process: undefined }},
    timeout: {timeout_ms},
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
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", delete=False, dir=base_dir
    ) as tmp:
        tmp.write(script)
        tmp_path = tmp.name

    inode = os.stat(node_path).st_ino

    try:
        args = [node_path, "--no-experimental-fetch"]
        if memoria_mb is not None:
            args.append(f"--max-old-space-size={memoria_mb}")
        args.append(tmp_path)
        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=base_dir,
            env=env,
        ) as proc:  # nosec B603
            if os.stat(node_path).st_ino != inode:
                proc.kill()
                raise SecurityError("El binario de Node ha cambiado")
            salida = bytearray()
            truncado = False
            assert proc.stdout is not None  # para type checkers
            if os.name == "nt":
                import threading

                def leer_salida() -> None:
                    nonlocal salida, truncado
                    for linea in iter(proc.stdout.readline, b""):
                        if not linea:
                            break
                        salida.extend(linea)
                        if len(salida) > MAX_JS_OUTPUT_BYTES:
                            truncado = True
                            proc.kill()
                            salida = salida[:MAX_JS_OUTPUT_BYTES]
                            break

                lector = threading.Thread(target=leer_salida)
                lector.start()
                lector.join(timeout)
                if lector.is_alive():
                    proc.kill()
                    lector.join()
                    return "Error: tiempo de ejecuci\u00f3n agotado"
            else:
                import select
                import time

                inicio = time.monotonic()
                while True:
                    if timeout is None:
                        restante = None
                    else:
                        restante = inicio + timeout - time.monotonic()
                        if restante <= 0:
                            proc.kill()
                            return "Error: tiempo de ejecuci\u00f3n agotado"
                    rlist, _, _ = select.select([proc.stdout], [], [], restante)
                    if timeout is not None and not rlist:
                        proc.kill()
                        return "Error: tiempo de ejecuci\u00f3n agotado"
                    chunk = proc.stdout.read(1024)
                    if not chunk:
                        if proc.poll() is not None:
                            break
                        continue
                    salida.extend(chunk)
                    if len(salida) > MAX_JS_OUTPUT_BYTES:
                        truncado = True
                        proc.kill()
                        salida = salida[:MAX_JS_OUTPUT_BYTES]
                        break

            proc.wait()
            resultado = salida.decode(errors="ignore")
            if proc.returncode and not truncado:
                resultado = resultado.strip()
                if resultado:
                    return f"Error: {resultado}"
                return f"Error: {proc.returncode}"
            if truncado:
                resultado += "\n[output truncated]"
            return resultado
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass


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
    ejecución del contenedor o ``None`` para desactivar el límite.

    El contenedor se lanza sin acceso a la red (``--network=none``), como el
    usuario ``nobody`` (``--user 65534:65534``), con el sistema de archivos en
    modo solo lectura (``--read-only`` y ``--tmpfs /tmp``) y sin capacidades
    adicionales (``--cap-drop=ALL``). Además, se aplican límites de recursos
    mediante ``--pids-limit``, ``--memory`` y ``--cpus`` para evitar abusos del sistema.
    """

    imagenes = {
        "python": "cobra-python-sandbox",
        "js": "cobra-js-sandbox",
        "cpp": "cobra-cpp-sandbox",
        "rust": "cobra-rust-sandbox",
    }

    if backend not in imagenes:
        raise ValueError(f"Backend no soportado: {backend}")

    docker_path = shutil.which("docker")
    if not docker_path:
        raise RuntimeError(
            "Docker no está disponible: no se encontró el ejecutable en PATH"
        )

    docker_path = os.path.realpath(docker_path)
    if not os.path.exists(docker_path):
        raise RuntimeError(
            f"Docker no está disponible: el ejecutable '{docker_path}' no existe"
        )

    try:
        docker_inode = os.stat(docker_path).st_ino
    except OSError as exc:  # pragma: no cover - fallo inesperado de acceso
        raise RuntimeError(
            f"Docker no está disponible: no se pudo acceder a '{docker_path}'"
        ) from exc

    docker_dir = os.path.dirname(docker_path) or os.defpath
    env = {"PATH": docker_dir}

    args = [
        docker_path,
        "run",
        "--rm",
        "--network=none",
        "--pids-limit=128",
        "--memory=256m",
        "--cpus=1",
        "--user",
        "65534:65534",
        "--read-only",
        "--tmpfs",
        "/tmp",
        "--cap-drop=ALL",
        "-i",
        imagenes[backend],
    ]

    try:
        with subprocess.Popen(  # nosec B607 B603
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        ) as proc:
            try:
                if os.stat(docker_path).st_ino != docker_inode:
                    proc.kill()
                    proc.wait()
                    raise SecurityError("El binario de Docker ha cambiado")
            except OSError as exc:  # pragma: no cover - condición de carrera
                proc.kill()
                proc.wait()
                raise SecurityError(
                    "No se pudo verificar la integridad del binario de Docker"
                ) from exc
            assert proc.stdin is not None
            assert proc.stdout is not None

            try:
                proc.stdin.write(codigo.encode())
            except BrokenPipeError:
                pass
            finally:
                proc.stdin.close()

            salida = bytearray()
            truncado = False

            if os.name == "nt":
                import threading

                def leer_salida() -> None:
                    nonlocal salida, truncado
                    for linea in iter(proc.stdout.readline, b""):
                        if not linea:
                            break
                        salida.extend(linea)
                        if len(salida) > MAX_CONTAINER_OUTPUT_BYTES:
                            truncado = True
                            proc.kill()
                            salida = salida[:MAX_CONTAINER_OUTPUT_BYTES]
                            break

                lector = threading.Thread(target=leer_salida)
                lector.start()
                lector.join(timeout)
                if timeout is not None and lector.is_alive():
                    proc.kill()
                    lector.join()
                    proc.wait()
                    raise RuntimeError("Tiempo de ejecución agotado")
            else:
                import select
                import time

                deadline: float | None = None
                if timeout is not None:
                    deadline = time.monotonic() + timeout

                while True:
                    restante: float | None = None
                    if deadline is not None:
                        restante = deadline - time.monotonic()
                        if restante <= 0:
                            proc.kill()
                            proc.wait()
                            raise RuntimeError("Tiempo de ejecución agotado")
                    rlist, _, _ = select.select([proc.stdout], [], [], restante)
                    if deadline is not None and not rlist:
                        proc.kill()
                        proc.wait()
                        raise RuntimeError("Tiempo de ejecución agotado")
                    if not rlist:
                        continue
                    chunk = proc.stdout.read(1024)
                    if not chunk:
                        if proc.poll() is not None:
                            break
                        continue
                    salida.extend(chunk)
                    if len(salida) > MAX_CONTAINER_OUTPUT_BYTES:
                        truncado = True
                        proc.kill()
                        salida = salida[:MAX_CONTAINER_OUTPUT_BYTES]
                        break

            proc.wait()
            resultado = salida.decode(errors="ignore")
            if proc.returncode and not truncado:
                mensaje = resultado.strip() or f"Error: {proc.returncode}"
                raise RuntimeError(mensaje)
            if truncado:
                resultado += "\n[output truncated]"
            return resultado
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Docker no está disponible: no se pudo invocar el ejecutable"
        ) from exc


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
