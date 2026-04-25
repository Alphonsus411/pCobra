from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class RunRequest:
    archivo: str
    debug: bool = False
    sandbox: bool = False
    contenedor: str | None = None
    formatear: bool = False
    modo: str = "mixto"
    backend_reason: str | None = None
    seguro: bool = True
    verbose: int = 0
    depurar: bool = False
    extra_validators: str | list[str] | None = None
    allow_insecure_fallback: bool = False


@dataclass(frozen=True, slots=True)
class TestRequest:
    archivo: str
    lenguajes: list[str]
    modo: str = "mixto"
    backend_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ModRequest:
    accion: str
    ruta: str | None = None
    nombre: str | None = None


def _to_mapping(raw: Any) -> Mapping[str, Any]:
    if isinstance(raw, Mapping):
        return raw
    if hasattr(raw, "__dict__"):
        return vars(raw)
    raise TypeError(f"No se puede normalizar request desde tipo: {type(raw)!r}")


def normalize_run_request(raw: RunRequest | Mapping[str, Any] | Any) -> RunRequest:
    if isinstance(raw, RunRequest):
        if not raw.archivo:
            raise ValueError("El campo 'archivo' es obligatorio")
        return raw

    payload = _to_mapping(raw)
    archivo = str(payload.get("archivo") or payload.get("file") or "").strip()
    if not archivo:
        raise ValueError("El campo 'archivo' es obligatorio")

    extra = payload.get("extra_validators")
    if isinstance(extra, (str, Path)):
        extra = str(extra)
    elif isinstance(extra, list):
        extra = [str(item) for item in extra]

    return RunRequest(
        archivo=archivo,
        debug=bool(payload.get("debug", False)),
        sandbox=bool(payload.get("sandbox", False)),
        contenedor=payload.get("contenedor") or payload.get("container"),
        formatear=bool(payload.get("formatear", False)),
        modo=str(payload.get("modo", "mixto") or "mixto"),
        backend_reason=payload.get("backend_reason"),
        seguro=bool(payload.get("seguro", True)),
        verbose=int(payload.get("verbose", 0) or 0),
        depurar=bool(payload.get("depurar", False)),
        extra_validators=extra,
        allow_insecure_fallback=bool(payload.get("allow_insecure_fallback", False)),
    )


def normalize_test_request(raw: TestRequest | Mapping[str, Any] | Any) -> TestRequest:
    if isinstance(raw, TestRequest):
        archivo = str(raw.archivo or "").strip()
        if not archivo:
            raise ValueError("El campo 'archivo' es obligatorio")
        if isinstance(raw.lenguajes, str):
            lenguajes = [lang.strip() for lang in raw.lenguajes.split(",") if lang.strip()]
        else:
            lenguajes = [str(lang).strip() for lang in raw.lenguajes if str(lang).strip()]
        if not lenguajes:
            raise ValueError("El campo 'lenguajes' es obligatorio")
        return TestRequest(
            archivo=archivo,
            lenguajes=lenguajes,
            modo=str(raw.modo or "mixto"),
            backend_reason=raw.backend_reason,
        )

    payload = _to_mapping(raw)
    archivo = str(payload.get("archivo") or payload.get("file") or "").strip()
    if not archivo:
        raise ValueError("El campo 'archivo' es obligatorio")

    raw_langs = payload.get("lenguajes")
    if raw_langs is None:
        raw_langs = payload.get("langs")
    if isinstance(raw_langs, str):
        lenguajes = [lang.strip() for lang in raw_langs.split(",") if lang.strip()]
    else:
        lenguajes = [str(lang).strip() for lang in (raw_langs or []) if str(lang).strip()]

    if not lenguajes:
        raise ValueError("El campo 'lenguajes' es obligatorio")

    return TestRequest(
        archivo=archivo,
        lenguajes=lenguajes,
        modo=str(payload.get("modo", "mixto") or "mixto"),
        backend_reason=payload.get("backend_reason"),
    )


def normalize_mod_request(raw: ModRequest | Mapping[str, Any] | Any) -> ModRequest:
    if isinstance(raw, ModRequest):
        request = raw
    else:
        payload = _to_mapping(raw)
        request = ModRequest(
            accion=str(payload.get("accion") or payload.get("action") or "").strip(),
            ruta=payload.get("ruta") or payload.get("path"),
            nombre=payload.get("nombre") or payload.get("name"),
        )

    action_aliases = {
        "list": "listar",
        "install": "instalar",
        "remove": "remover",
        "publish": "publicar",
        "search": "buscar",
    }
    request = ModRequest(
        accion=action_aliases.get(request.accion, request.accion),
        ruta=request.ruta,
        nombre=request.nombre,
    )

    if not request.accion:
        raise ValueError("El campo 'accion' es obligatorio")

    requires_ruta = {"instalar", "publicar"}
    requires_nombre = {"remover", "buscar"}
    if request.accion in requires_ruta and not request.ruta:
        raise ValueError(f"La acción '{request.accion}' requiere el campo 'ruta'")
    if request.accion in requires_nombre and not request.nombre:
        raise ValueError(f"La acción '{request.accion}' requiere el campo 'nombre'")

    return request
