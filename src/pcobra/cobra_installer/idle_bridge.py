"""Puente delgado para que el IDLE delegue el empaquetado.

No debe contener lógica de construcción: el IDLE y este módulo solo llaman a
``package_current_project``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .project import BuildOptions, CobraInstallerError
from .runtime_builder import build_project

ProgressCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class IdlePackageResult:
    """Resultado mínimo que necesita mostrar el IDLE tras empaquetar."""

    executable_path: Path | None
    dist_dir: Path
    artifact_path: Path | None = None
    output_dir: Path | None = None


def package_current_project(
    project_path: str | Path,
    ui_options: Mapping[str, Any] | object | None = None,
    progress_callback: ProgressCallback | None = None,
    error_callback: ErrorCallback | None = None,
    **kwargs: object,
) -> IdlePackageResult:
    """Empaqueta el proyecto actual desde IDLE usando la API del instalador.

    El IDLE entrega opciones propias de la interfaz (normalmente un ``dict`` o
    un objeto simple) y este puente las convierte a :class:`BuildOptions`,
    conecta el callback de progreso al ``log_callback`` del builder y traduce
    errores controlados del instalador a mensajes orientados a usuario.

    También acepta las palabras clave históricas del diálogo IDLE
    (``name``, ``target``, ``mode``, ``icon`` y ``log_callback``) para mantener
    compatibilidad con llamadas directas existentes.
    """

    merged_options = _merge_ui_options(ui_options, kwargs)
    callback = progress_callback or _pop_callback(merged_options, "log_callback")
    options = _build_options_from_idle(project_path, merged_options, callback)
    try:
        if callback is not None:
            callback("Iniciando empaquetado del proyecto Cobra...")
        result = build_project(project_path, options)
        dist_dir = Path(result.dist_dir or result.output_dir or result.artifact_path)
        executable_path = _resolve_executable_path(result.executable_name, dist_dir)
        artifact_path = result.artifact_path or executable_path
        output_dir = result.output_dir or dist_dir
        if callback is not None:
            callback(f"Empaquetado completado en {dist_dir}.")
        return IdlePackageResult(
            executable_path=executable_path,
            dist_dir=dist_dir,
            artifact_path=artifact_path,
            output_dir=output_dir,
        )
    except CobraInstallerError as exc:
        message = _user_message_from_installer_error(exc)
        if error_callback is not None:
            error_callback(message)
        raise RuntimeError(message) from exc


def package_from_idle(
    project_root: str | Path,
    ui_options: Mapping[str, Any] | object | None = None,
    progress_callback: ProgressCallback | None = None,
    error_callback: ErrorCallback | None = None,
    **kwargs: object,
) -> IdlePackageResult:
    """Alias explícito para código existente del IDLE."""

    merged_options = _merge_ui_options(ui_options, kwargs)
    return package_current_project(
        project_root, merged_options, progress_callback, error_callback
    )


def _build_options_from_idle(
    project_path: str | Path,
    ui_options: Mapping[str, Any] | object | None,
    progress_callback: ProgressCallback | None,
) -> BuildOptions:
    values = _ui_options_to_dict(ui_options)
    translated = {
        option_name: values[ui_name]
        for ui_name, option_name in _UI_OPTION_ALIASES.items()
        if ui_name in values and values[ui_name] is not None
    }
    extra_args = translated.get("extra_args")
    if isinstance(extra_args, str):
        translated["extra_args"] = tuple(extra_args.split())
    return BuildOptions(
        project_root=project_path,
        log_callback=progress_callback,
        **translated,
    )


def _ui_options_to_dict(
    ui_options: Mapping[str, Any] | object | None,
) -> dict[str, Any]:
    if ui_options is None:
        return {}
    if isinstance(ui_options, Mapping):
        return dict(ui_options)
    return {
        name: getattr(ui_options, name)
        for name in _UI_OPTION_ALIASES
        if hasattr(ui_options, name)
    }


def _merge_ui_options(
    ui_options: Mapping[str, Any] | object | None, kwargs: Mapping[str, object]
) -> dict[str, Any]:
    merged = _ui_options_to_dict(ui_options)
    merged.update(kwargs)
    return merged


def _pop_callback(options: dict[str, Any], name: str) -> ProgressCallback | None:
    callback = options.pop(name, None)
    if callback is None:
        return None
    if not callable(callback):
        raise TypeError(f"{name} debe ser callable")
    return callback


def _resolve_executable_path(
    executable_name: str | None, dist_dir: Path
) -> Path | None:
    if not executable_name:
        return None
    direct = dist_dir / executable_name
    if direct.exists():
        return direct
    windows = dist_dir / f"{executable_name}.exe"
    if windows.exists():
        return windows
    nested = dist_dir / executable_name / executable_name
    if nested.exists():
        return nested
    nested_windows = dist_dir / executable_name / f"{executable_name}.exe"
    if nested_windows.exists():
        return nested_windows
    return direct


def _user_message_from_installer_error(exc: CobraInstallerError) -> str:
    detail = str(exc).strip()
    if not detail:
        detail = "fallo desconocido del instalador"
    return f"No se pudo empaquetar el proyecto Cobra: {detail}"


_UI_OPTION_ALIASES = {
    "entrypoint": "entrypoint",
    "output_dir": "output_dir",
    "dist_dir": "dist_dir",
    "name": "name",
    "target": "target",
    "architecture": "architecture",
    "builder": "builder",
    "builder_config": "builder_config",
    "mode": "mode",
    "temp_dir": "temp_dir",
    "icon": "icon",
    "assets": "assets",
    "config": "config",
    "clean": "clean",
    "include_dependencies": "include_dependencies",
    "extra_args": "extra_args",
    "install_pyinstaller": "install_pyinstaller",
    # Nombres frecuentes de controles del IDLE.
    "nombre": "name",
    "salida": "output_dir",
    "directorio_salida": "output_dir",
    "objetivo": "target",
    "arquitectura": "architecture",
    "modo": "mode",
    "limpiar": "clean",
    "incluir_dependencias": "include_dependencies",
    "instalar_pyinstaller": "install_pyinstaller",
}
