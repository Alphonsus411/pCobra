"""Ejecución de código Python en un entorno restringido."""

from __future__ import annotations

import ast
import builtins
import contextlib
import io
import os
import marshal
import multiprocessing
import shutil
import subprocess
import tempfile
import string
import sys
from types import ModuleType
from queue import Empty
from pathlib import Path
from typing import Any, Callable
from packaging.version import Version

try:  # pragma: no cover - dependencia opcional
    from RestrictedPython import compile_restricted, safe_builtins
    from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getattr
    from RestrictedPython.Guards import (
        guarded_iter_unpack_sequence,
        guarded_unpack_sequence,
    )
    from RestrictedPython.PrintCollector import PrintCollector
    HAS_RESTRICTED_PYTHON = True
except ModuleNotFoundError:  # pragma: no cover - entornos sin RestrictedPython
    compile_restricted = None  # type: ignore[assignment]
    safe_builtins = {}  # type: ignore[assignment]
    default_guarded_getitem = None  # type: ignore[assignment]
    default_guarded_getattr = None  # type: ignore[assignment]
    guarded_iter_unpack_sequence = None  # type: ignore[assignment]
    guarded_unpack_sequence = None  # type: ignore[assignment]
    PrintCollector = None  # type: ignore[assignment]
    HAS_RESTRICTED_PYTHON = False


MIN_VM2_VERSION = Version("3.9.19")

# Límite máximo de salida permitida en la sandbox de JS (8 KB)
MAX_JS_OUTPUT_BYTES = 8 * 1024

# Límite máximo de salida permitida para la ejecución en contenedores (8 KB)
MAX_CONTAINER_OUTPUT_BYTES = 8 * 1024

_ORIGINAL_IMPORT = builtins.__import__
_IMPORT_DENYLIST = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "urllib",
}

_FORBIDDEN_CALLS = {"eval", "exec", "open"}
_FORBIDDEN_NAMES = _FORBIDDEN_CALLS | {"__import__"}
_FORBIDDEN_ATTRIBUTES = {"__dict__", "__class__"}
_KNOWN_MODULE_SOURCES = {"builtins", "io", "pathlib"}

if not HAS_RESTRICTED_PYTHON:
    _IMPORT_DENYLIST.add("builtins")

if HAS_RESTRICTED_PYTHON:
    _SANDBOX_BASE_BUILTINS: dict[str, Any] = dict(safe_builtins)
else:  # pragma: no cover - ejecución sin RestrictedPython
    _SANDBOX_BASE_BUILTINS = {}

_SANITIZED_BUILTINS_MODULE: ModuleType | None = None


class SandboxSecurityError(RuntimeError):
    """Excepción lanzada cuando el código viola las políticas de la sandbox."""


def _verificar_codigo_prohibido(codigo: str) -> None:
    """Analiza ``codigo`` y bloquea importaciones o llamadas peligrosas."""

    try:
        tree = ast.parse(codigo)
    except SyntaxError:
        raise

    forbidden_aliases: set[str] = set()
    module_aliases: dict[str, str] = {"__builtins__": "builtins"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in _IMPORT_DENYLIST:
                    raise SandboxSecurityError(
                        f"Importación bloqueada en sandbox: {alias.name}"
                    )
                if root in _KNOWN_MODULE_SOURCES:
                    alias_name = alias.asname or root
                    module_aliases[alias_name] = root
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0] if module else ""
            if root in _IMPORT_DENYLIST:
                raise SandboxSecurityError(
                    f"Importación bloqueada en sandbox: {module}"
                )
            if root in _KNOWN_MODULE_SOURCES:
                for alias in node.names:
                    alias_name = alias.asname or alias.name
                    if alias.name in _FORBIDDEN_CALLS:
                        forbidden_aliases.add(alias_name)
                        continue
                    module_aliases[alias_name] = root

    def _leftmost_name(expr: ast.AST | None) -> str | None:
        if expr is None:
            return None
        current = expr
        while True:
            if isinstance(current, ast.Name):
                return current.id
            if isinstance(current, ast.Attribute):
                current = current.value
                continue
            if isinstance(current, ast.Call):
                current = current.func
                continue
            if isinstance(current, ast.Subscript):
                current = current.value
                continue
            return None

    def _call_matches(func: ast.AST, nombres: set[str]) -> bool:
        """Determina si ``func`` apunta a alguna llamada en ``nombres``."""

        if isinstance(func, ast.Name):
            return func.id in nombres
        if isinstance(func, ast.Attribute) and func.attr in nombres:
            base = _leftmost_name(func.value)
            return bool(
                base
                and (
                    base in module_aliases
                    or base in _KNOWN_MODULE_SOURCES
                    or module_aliases.get(base) in _KNOWN_MODULE_SOURCES
                )
            )
        return False

    def _extract_string(expr: ast.AST | None) -> str | None:
        """Obtiene el literal de texto utilizado como índice o nombre."""

        if expr is None:
            return None
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            return expr.value
        if isinstance(expr, ast.Str):  # pragma: no cover - compatibilidad
            return expr.s
        if isinstance(expr, ast.Index):  # pragma: no cover - Python<3.9
            return _extract_string(expr.value)
        return None

    def _is_builtins_reference(expr: ast.AST | None) -> bool:
        """Comprueba si ``expr`` hace referencia (directa o indirecta) a ``builtins``."""

        if expr is None:
            return False

        nombre = _leftmost_name(expr)
        if nombre in {"builtins", "__builtins__"}:
            return True
        if nombre and module_aliases.get(nombre) == "builtins":
            return True
        if nombre == "builtins" and nombre in _KNOWN_MODULE_SOURCES:
            return True
        if isinstance(expr, ast.Call):
            if _call_matches(expr.func, {"vars"}):
                if expr.args and _is_builtins_reference(expr.args[0]):
                    return True
            if _call_matches(expr.func, {"getattr"}):
                base_expr = expr.args[0] if expr.args else None
                attr_expr = expr.args[1] if len(expr.args) > 1 else None
                attr_name = _extract_string(attr_expr)
                if (
                    attr_name in (_FORBIDDEN_ATTRIBUTES | _FORBIDDEN_NAMES)
                    and _is_builtins_reference(base_expr)
                ):
                    return True
            info = _import_call_info(expr)
            if info and info[0] == "builtins":
                return True
        return False

    def _import_call_info(expr: ast.AST) -> tuple[str, str] | None:
        if not isinstance(expr, ast.Call):
            return None

        func = expr.func
        if isinstance(func, ast.Name) and func.id == "__import__" and expr.args:
            arg0 = expr.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                module_name = arg0.value
                root = module_name.split(".", 1)[0]
                return module_name, root
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "getattr":
                if len(node.args) >= 2:
                    base = node.args[0]
                    attr_arg = node.args[1]
                    attr_name = _extract_string(attr_arg)

                    if attr_name in (_FORBIDDEN_NAMES | _FORBIDDEN_ATTRIBUTES):
                        base_name = _leftmost_name(base)
                        if base_name and (
                            base_name in module_aliases
                            or base_name in _KNOWN_MODULE_SOURCES
                            or module_aliases.get(base_name) in _KNOWN_MODULE_SOURCES
                        ):
                            raise SandboxSecurityError(
                                "Acceso bloqueado en sandbox: "
                                f"getattr({base_name}, '{attr_name}')"
                            )

            if isinstance(node.func, ast.Name):
                nombre = node.func.id
                if nombre in _FORBIDDEN_CALLS or nombre in forbidden_aliases:
                    raise SandboxSecurityError(
                        f"Llamada bloqueada en sandbox: {nombre}"
                    )
                if nombre == "__import__" and node.args:
                    arg0 = node.args[0]
                    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                        raiz = arg0.value.split(".", 1)[0]
                        if raiz in _IMPORT_DENYLIST:
                            raise SandboxSecurityError(
                                f"Importación bloqueada en sandbox: {arg0.value}"
                            )
            elif isinstance(node.func, ast.Attribute):
                info = _import_call_info(node.func.value)
                if info and node.func.attr in _FORBIDDEN_CALLS:
                    module_name, _root = info
                    raise SandboxSecurityError(
                        "Llamada bloqueada en sandbox: "
                        f"__import__('{module_name}').{node.func.attr}"
                    )
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.attr == "__import__"
                    and node.args
                ):
                    arg0 = node.args[0]
                    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                        raiz = arg0.value.split(".", 1)[0]
                        if raiz in _IMPORT_DENYLIST:
                            raise SandboxSecurityError(
                                f"Importación bloqueada en sandbox: {arg0.value}"
                            )
                elif node.func.attr in _FORBIDDEN_CALLS:
                    base_name = _leftmost_name(node.func.value)
                    if base_name and (
                        base_name in module_aliases
                        or base_name in _KNOWN_MODULE_SOURCES
                    ):
                        raise SandboxSecurityError(
                            f"Llamada bloqueada en sandbox: {base_name}.{node.func.attr}"
                        )

        elif isinstance(node, ast.Attribute):
            info = _import_call_info(node.value)
            if info and node.attr in _FORBIDDEN_CALLS:
                module_name, _root = info
                raise SandboxSecurityError(
                    "Llamada bloqueada en sandbox: "
                    f"__import__('{module_name}').{node.attr}"
                )
            base_nombre = _leftmost_name(node.value)
            if (
                node.attr in _FORBIDDEN_ATTRIBUTES
                and base_nombre
                and (
                    base_nombre in module_aliases
                    or base_nombre in _KNOWN_MODULE_SOURCES
                    or module_aliases.get(base_nombre) in _KNOWN_MODULE_SOURCES
                )
            ):
                raise SandboxSecurityError(
                    "Acceso bloqueado en sandbox: "
                    f"{base_nombre}.{node.attr}"
                )

        elif isinstance(node, ast.Subscript):
            clave = _extract_string(getattr(node, "slice", None))
            base_name = _leftmost_name(node.value)
            if (
                clave in _FORBIDDEN_NAMES
                and base_name
                and (
                    base_name in module_aliases or base_name in _KNOWN_MODULE_SOURCES
                )
            ):
                raise SandboxSecurityError(
                    "Acceso bloqueado en sandbox: "
                    f"{base_name}[{clave!r}]"
                )

            if (
                isinstance(node.value, ast.Call)
                and clave in _FORBIDDEN_NAMES
                and _call_matches(node.value.func, {"getattr", "vars"})
                and _is_builtins_reference(node.value.args[0] if node.value.args else None)
            ):
                # Bloquea patrones como vars(__builtins__)["open"] o
                # getattr(__builtins__, "__dict__")["exec"], que recuperan
                # funciones vetadas de contenedores aparentemente seguros.
                descripcion_llamada = (
                    ast.unparse(node.value)
                    if hasattr(ast, "unparse")
                    else "llamada"
                )
                raise SandboxSecurityError(
                    "Acceso bloqueado en sandbox: "
                    f"{descripcion_llamada}[{clave!r}]"
                )


def _safe_import(name: str, globals: Any | None = None, locals: Any | None = None,
                 fromlist: tuple[str, ...] = (), level: int = 0) -> Any:
    """Importador restringido que bloquea módulos peligrosos.

    Se permite importar cualquier módulo que no esté en la lista de exclusión.
    Los módulos bloqueados generan ``ImportError`` para que la sandbox se
    comporte igual que antes, pero sigue admitiendo importaciones seguras como
    ``contextlib`` que requieren las pruebas de transpilación.
    """

    root = name.split(".", 1)[0]
    if root in _IMPORT_DENYLIST or name in _IMPORT_DENYLIST:
        raise ImportError(f"Módulo bloqueado en sandbox: {name}")

    if root == "builtins":
        global _SANITIZED_BUILTINS_MODULE
        if _SANITIZED_BUILTINS_MODULE is None:
            modulo_sanitizado = ModuleType("builtins")
            atributos_permitidos = dict(_SANDBOX_BASE_BUILTINS)
            atributos_permitidos.setdefault("print", print)
            atributos_permitidos["__import__"] = _safe_import
            for prohibido in _FORBIDDEN_NAMES:
                atributos_permitidos.pop(prohibido, None)
            for clave, valor in atributos_permitidos.items():
                setattr(modulo_sanitizado, clave, valor)
            _SANITIZED_BUILTINS_MODULE = modulo_sanitizado
        return _SANITIZED_BUILTINS_MODULE

    modulo = _ORIGINAL_IMPORT(name, globals, locals, fromlist, level)
    if root == "urllib":  # Evita accesos a urllib.request y similares.
        raise ImportError(f"Módulo bloqueado en sandbox: {name}")
    return modulo


def _run_in_subprocess(
    codigo: str, timeout: float | None = None, memoria_mb: int | None = None
) -> str:
    """Ejecuta ``codigo`` en un subproceso de Python sin restricciones.

    ``timeout`` define el tiempo máximo de ejecución en segundos. ``memoria_mb``
    establece el límite superior de memoria (en megabytes) utilizando
    ``resource.RLIMIT_AS`` en sistemas POSIX. En Windows se lanza
    ``NotImplementedError`` cuando se solicita un límite de memoria y se emite
    ``ValueError`` si el parámetro no es positivo. Se lanza ``TimeoutError`` si
    el subproceso excede el tiempo y ``MemoryError`` si el proceso hijo supera
    el límite asignado.
    """

    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[3]
    src_root = repo_root / "src"
    pythonpath = env.get("PYTHONPATH", "")
    extra_paths = [str(repo_root), str(src_root)]
    current = pythonpath.split(os.pathsep) if pythonpath else []
    updated = current[:]
    for ruta in extra_paths:
        if ruta not in current:
            updated.insert(0, ruta)
    env["PYTHONPATH"] = os.pathsep.join(updated) if updated else ""

    preexec_fn: Callable[[], None] | None = None
    if memoria_mb is not None:
        if memoria_mb <= 0:
            raise ValueError("memoria_mb debe ser un entero positivo")
        if os.name == "nt":
            raise NotImplementedError(
                "El límite de memoria no está soportado en Windows"
            )

        def limitar_memoria() -> None:
            import resource

            limite = memoria_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limite, limite))

        preexec_fn = limitar_memoria

    try:
        completed = subprocess.run(
            [sys.executable, "-c", codigo],
            capture_output=True,
            text=True,
            check=True,
            env=env,
            timeout=timeout,
            preexec_fn=preexec_fn,
        )
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - comportamiento simple
        raise TimeoutError("Tiempo de ejecución agotado") from exc
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error simple
        salida = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        if "MemoryError" in salida:
            raise MemoryError("Límite de memoria excedido en sandbox") from exc
        raise RuntimeError(salida) from exc
    return completed.stdout


def _worker(
    code_bytes: bytes, queue: multiprocessing.Queue, memoria_mb: int | None
) -> None:
    """Ejecuta ``code_bytes`` en un proceso aislado y comunica el resultado."""
    try:
        if memoria_mb is not None and os.name != "nt":
            import resource

            limite = memoria_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limite, limite))

        builtins_dict = dict(_SANDBOX_BASE_BUILTINS)
        builtins_dict["__import__"] = _safe_import
        builtins_dict.setdefault("print", print)

        env = {
            "__builtins__": builtins_dict,
            "_print_": PrintCollector,
            "_getattr_": default_guarded_getattr,
            "_getitem_": default_guarded_getitem,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
        }

        byte_code = marshal.loads(code_bytes)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(byte_code, env, env)
        queue.put(stdout.getvalue())
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
    _verificar_codigo_prohibido(codigo)

    if not HAS_RESTRICTED_PYTHON:
        return _run_in_subprocess(codigo, timeout=timeout, memoria_mb=memoria_mb)

    try:
        byte_code = compile_restricted(codigo, "<string>", "exec")
    except SyntaxError as se:  # pragma: no cover - comportamiento simple
        return _run_in_subprocess(codigo, timeout=timeout, memoria_mb=memoria_mb)

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
