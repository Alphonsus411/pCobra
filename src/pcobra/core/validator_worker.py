"""Aislamiento y protocolo cerrado para validadores adicionales.

Este módulo no importa el intérprete deliberadamente: el proceso hijo sólo
compila el archivo autorizado y devuelve descriptores de datos.
"""

from __future__ import annotations

import ast
import builtins
import math
import os
from typing import Any, Protocol, cast

MAX_SOURCE_BYTES = 1_000_000
MAX_DESCRIPTORS = 32
MAX_CONTAINER_ITEMS = 128


class _Connection(Protocol):
    def send(self, obj: object) -> None: ...
    def close(self) -> None: ...


def _apply_resource_limits() -> None:
    """Aplica límites POSIX; en otras plataformas el padre conserva el timeout."""

    try:
        import resource
    except ImportError:  # pragma: no cover - ruta explícita no POSIX
        return

    # ``resource`` expone atributos dependientes de plataforma.
    # El import anterior conserva la protección runtime; aquí aislamos
    # únicamente esa variación de typeshed/mypy.
    resource_api: Any = resource

    memory = 256 * 1024 * 1024
    resource_api.setrlimit(resource_api.RLIMIT_AS, (memory, memory))
    cpu_consumida = resource_api.getrusage(resource_api.RUSAGE_SELF)
    usada = cpu_consumida.ru_utime + cpu_consumida.ru_stime
    limite_blando = max(1, math.ceil(usada + 1.0))
    resource_api.setrlimit(
        resource_api.RLIMIT_CPU,
        (limite_blando, limite_blando + 1),
    )


def _check_policy(source: str, filename: str) -> ast.AST:
    tree = ast.parse(source, filename=filename)
    sensitive = {
        "__subclasses__",
        "__globals__",
        "__dict__",
        "__mro__",
        "__bases__",
        "__getattribute__",
        "__setattr__",
        "__delattr__",
        "__code__",
        "__closure__",
        "__func__",
        "__self__",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise PermissionError("import_no_permitido")
        if (
            isinstance(node, ast.Attribute)
            and node.attr.startswith("__")
            and node.attr != "__name__"
        ):
            raise PermissionError("atributo_magico_no_permitido")
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(token in node.value for token in sensitive):
                raise PermissionError("introspeccion_no_permitida")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "__import__":
                raise PermissionError("import_no_permitido")
            if node.func.id == "getattr":
                raise PermissionError("introspeccion_no_permitida")
    return tree


def _primitive(value: Any, *, depth: int = 0) -> Any:
    if depth > 4:
        raise TypeError("resultado_no_serializable")
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list) and len(value) <= MAX_CONTAINER_ITEMS:
        return [_primitive(item, depth=depth + 1) for item in value]
    if isinstance(value, dict) and len(value) <= MAX_CONTAINER_ITEMS:
        if not all(isinstance(key, str) for key in value):
            raise TypeError("resultado_no_serializable")
        return {key: _primitive(item, depth=depth + 1) for key, item in value.items()}
    raise TypeError("resultado_no_serializable")


def _normalize_descriptors(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_DESCRIPTORS:
        raise TypeError("resultado_no_serializable")
    result = _primitive(value)
    for descriptor in result:
        if not isinstance(descriptor, dict) or set(descriptor) != {
            "nombre",
            "parametros",
        }:
            raise TypeError("descriptor_invalido")
        if not isinstance(descriptor["nombre"], str) or not isinstance(
            descriptor["parametros"], dict
        ):
            raise TypeError("descriptor_invalido")
    return cast(list[dict[str, Any]], result)


def run_validator_worker(
    connection: _Connection,
    request: dict[str, Any],
) -> None:
    """Punto de entrada ``spawn``: siempre intenta responder datos primitivos."""

    try:
        if set(request) != {"source", "filename"}:
            raise TypeError("solicitud_invalida")
        source, filename = request["source"], request["filename"]
        if not isinstance(source, str) or not isinstance(filename, str):
            raise TypeError("solicitud_invalida")
        if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise MemoryError
        _check_policy(source, filename)

        from .sandbox import cargar_simbolos_restrictedpython

        symbols, available = cargar_simbolos_restrictedpython()
        if not available:
            connection.send(
                {"estado": "error", "codigo": "restrictedpython_no_disponible"}
            )
            return
        # La importación confiable puede consumir una parte apreciable del
        # presupuesto; los límites protegen exclusivamente el código externo.
        _apply_resource_limits()
        safe = symbols["safe_builtins"]
        allowed_builtins = {
            name: safe[name] for name in ("len", "range") if name in safe
        }
        namespace = {"__builtins__": allowed_builtins, "__name__": "validators"}
        byte_code = symbols["compile_restricted"](source, filename, "exec")
        exec(byte_code, namespace)
        descriptors = _normalize_descriptors(namespace.get("VALIDADORES_EXTRA", []))
        connection.send({"estado": "ok", "validadores": descriptors})
    except PermissionError as exc:
        connection.send({"estado": "error", "codigo": str(exc)})
    except SyntaxError:
        connection.send({"estado": "error", "codigo": "sintaxis_invalida"})
    except (MemoryError, OverflowError):
        connection.send({"estado": "error", "codigo": "memoria_excedida"})
    except TypeError as exc:
        codigo = (
            str(exc)
            if str(exc) in {"resultado_no_serializable", "descriptor_invalido"}
            else "protocolo_invalido"
        )
        connection.send({"estado": "error", "codigo": codigo})
    except BaseException:
        connection.send({"estado": "error", "codigo": "error_en_ejecucion"})
    finally:
        connection.close()
