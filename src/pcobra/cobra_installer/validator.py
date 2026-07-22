"""Validación de proyectos para el instalador Cobra."""

from __future__ import annotations

import json
import re
import tomllib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from pcobra.cobra.packaging import es_paquete_cobra

from .project import BuildOptions, CobraInstallerError, CobraProject
from .targets import validate_target

COBRA_EXTENSIONS = (".cobra",)
_EXECUTABLE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_RESERVED_EXECUTABLE_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}
_ICON_SUFFIXES = {".ico", ".icns", ".png", ".svg"}
_CONFIG_PATH_KEYS = ("icon", "icon_path")
_EXECUTABLE_NAME_KEYS = ("name", "executable_name", "executable", "app_name")
_REQUIRED_TOML_TOP_LEVEL = ("project", "package", "build", "app", "cobra")
_LOCK_REQUIRED_KEYS = {"version", "package", "packages", "dependencies", "metadata"}


@dataclass(frozen=True, slots=True)
class ValidationErrorDetail:
    """Detalle serializable de un problema detectado al validar un proyecto."""

    code: str
    message: str
    path: Path | None = None
    field: str | None = None
    hint: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Resultado acumulado para que el IDLE muestre todos los errores juntos."""

    project: CobraProject
    errors: tuple[ValidationErrorDetail, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        """Indica si el proyecto no tiene errores de validación."""

        return not self.errors

    def raise_for_errors(self) -> None:
        """Convierte el resultado acumulado en una excepción clásica si hace falta."""

        if self.is_valid:
            return
        formatted = "\n".join(f"- {error.message}" for error in self.errors)
        raise CobraInstallerError(f"El proyecto Cobra no es válido:\n{formatted}")


# La API pública nueva valida CobraProject y acumula errores. La validación de
# BuildOptions se conserva abajo para compatibilidad interna del builder.
def validate_project(project: CobraProject) -> ValidationResult:
    """Valida un proyecto Cobra sin detenerse en el primer error."""

    normalized = project.normalized()
    root = Path(normalized.project_root)
    errors: list[ValidationErrorDetail] = []

    if not root.exists() or not root.is_dir():
        errors.append(
            ValidationErrorDetail(
                code="project_root_missing",
                message=f"La raíz del proyecto no existe o no es una carpeta: {root}",
                path=root,
            )
        )
        return ValidationResult(project=normalized, errors=tuple(errors))

    _validate_entrypoint(normalized, root, errors)
    _validate_cobra_toml(normalized, root, errors)
    _validate_cobra_lock(normalized, root, errors)
    _validate_resource_paths(normalized.assets, root, "assets", errors)
    _validate_resource_paths(normalized.config_dirs, root, "config_dirs", errors)
    _validate_resource_paths(normalized.documentation, root, "documentation", errors)
    _validate_resource_paths(
        normalized.auxiliary_resources, root, "auxiliary_resources", errors
    )
    _validate_resource_paths(normalized.co_packages, root, "co_packages", errors)
    _validate_configured_executable_names(normalized.config, errors)
    _validate_configured_icon(normalized.config, root, errors)
    _validate_co_package_distinction(normalized, errors)

    return ValidationResult(project=normalized, errors=tuple(errors))


def validate_build_options(options: BuildOptions) -> BuildOptions:
    """Valida opciones de build y devuelve una versión normalizada.

    Mantiene el comportamiento previo para el orquestador de empaquetado, que
    debe seguir recibiendo ``BuildOptions`` normalizadas o lanzar
    ``CobraInstallerError``.
    """

    try:
        normalized = options.normalized()
    except (RuntimeError, ValueError) as exc:
        raise CobraInstallerError(str(exc)) from exc
    entrypoint = normalized.entrypoint or discover_entrypoint(
        Path(normalized.project_root)
    )
    project = CobraProject(
        project_root=normalized.project_root,
        entrypoint=entrypoint,
        assets=normalized.assets,
        config=normalized.config,
    )
    result = validate_project(project)
    extra_errors = list(result.errors)
    try:
        validate_target(normalized.target)
    except (RuntimeError, ValueError) as exc:
        extra_errors.append(
            ValidationErrorDetail(
                code="target_invalid",
                message=str(exc),
                field="target",
                hint="Usa windows, linux, macos o current.",
            )
        )
    if normalized.icon is not None:
        _validate_icon_path(
            normalized.icon,
            Path(normalized.project_root),
            extra_errors,
            field_name="icon",
        )
    if normalized.name is not None:
        _validate_executable_name(normalized.name, extra_errors, field_name="name")
    if extra_errors:
        ValidationResult(
            project=result.project, errors=tuple(extra_errors)
        ).raise_for_errors()
    return normalized


def discover_entrypoint(project_root: Path) -> Path | None:
    """Busca un punto de entrada Cobra común dentro del proyecto."""

    for name in ("main.cobra", "app.cobra"):
        candidate = project_root / name
        if candidate.exists() and candidate.is_file():
            return candidate
    for extension in COBRA_EXTENSIONS:
        matches = sorted(project_root.glob(f"*{extension}"))
        if matches:
            return matches[0]
    return None


def _validate_entrypoint(
    project: CobraProject, root: Path, errors: list[ValidationErrorDetail]
) -> None:
    entrypoint = project.entrypoint
    if entrypoint is None:
        errors.append(
            ValidationErrorDetail(
                code="entrypoint_missing",
                message="El proyecto no declara un entrypoint Cobra.",
                path=root,
                field="entrypoint",
                hint="Crea main.cobra o configura entrypoint/main/source/script en cobra.toml.",
            )
        )
        return
    if not entrypoint.is_file():
        errors.append(
            ValidationErrorDetail(
                "entrypoint_not_found",
                f"El punto de entrada no existe: {entrypoint}",
                entrypoint,
                "entrypoint",
            )
        )
        return
    if not _is_inside_project(entrypoint, root):
        errors.append(
            ValidationErrorDetail(
                "entrypoint_outside_project",
                f"El entrypoint está fuera del proyecto: {entrypoint}",
                entrypoint,
                "entrypoint",
            )
        )
    if entrypoint.suffix.lower() != ".cobra":
        errors.append(
            ValidationErrorDetail(
                code="entrypoint_extension_invalid",
                message=f"El entrypoint principal debe usar extensión .cobra: {entrypoint}",
                path=entrypoint,
                field="entrypoint",
            )
        )


def _validate_cobra_toml(
    project: CobraProject, root: Path, errors: list[ValidationErrorDetail]
) -> None:
    path = project.cobra_toml
    if path is None:
        return
    if path.name != "cobra.toml":
        errors.append(
            ValidationErrorDetail(
                "cobra_toml_name_invalid",
                f"El manifiesto debe llamarse cobra.toml: {path}",
                path,
                "cobra_toml",
            )
        )
    if not _is_inside_project(path, root):
        errors.append(
            ValidationErrorDetail(
                "cobra_toml_outside_project",
                f"cobra.toml está fuera del proyecto: {path}",
                path,
                "cobra_toml",
            )
        )
    if not path.exists():
        if path == root / "cobra.toml":
            return
        errors.append(
            ValidationErrorDetail(
                "cobra_toml_not_found",
                f"cobra.toml no existe: {path}",
                path,
                "cobra_toml",
            )
        )
        return
    if not path.is_file():
        errors.append(
            ValidationErrorDetail(
                "cobra_toml_not_file",
                f"cobra.toml no es un archivo: {path}",
                path,
                "cobra_toml",
            )
        )
        return
    data = _read_toml_mapping(path, errors, "cobra_toml")
    if data is not None and not any(key in data for key in _REQUIRED_TOML_TOP_LEVEL):
        errors.append(
            ValidationErrorDetail(
                "cobra_toml_format_invalid",
                "cobra.toml debe declarar al menos una sección reconocida: [project], [package], [build], [app] o [cobra].",
                path,
                "cobra_toml",
            )
        )


def _validate_cobra_lock(
    project: CobraProject, root: Path, errors: list[ValidationErrorDetail]
) -> None:
    path = project.cobra_lock
    if path is None or not path.exists():
        return
    if path.name != "cobra.lock":
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_name_invalid",
                f"El lockfile debe llamarse cobra.lock: {path}",
                path,
                "cobra_lock",
            )
        )
    if not _is_inside_project(path, root):
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_outside_project",
                f"cobra.lock está fuera del proyecto: {path}",
                path,
                "cobra_lock",
            )
        )
    if not path.is_file():
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_not_file",
                f"cobra.lock no es un archivo: {path}",
                path,
                "cobra_lock",
            )
        )
        return
    parsed = _read_lock_mapping(path, errors)
    if (
        parsed is not None
        and parsed
        and not any(key in parsed for key in _LOCK_REQUIRED_KEYS)
    ):
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_format_invalid",
                "cobra.lock no contiene claves reconocibles de lockfile.",
                path,
                "cobra_lock",
            )
        )


def _validate_resource_paths(
    paths: Sequence[Path | str],
    root: Path,
    field_name: str,
    errors: list[ValidationErrorDetail],
) -> None:
    for raw_path in paths:
        path = Path(raw_path)
        if not _is_inside_project(path, root):
            errors.append(
                ValidationErrorDetail(
                    f"{field_name}_outside_project",
                    f"La ruta de {field_name} está fuera del proyecto: {path}",
                    path,
                    field_name,
                )
            )
        if not path.exists():
            errors.append(
                ValidationErrorDetail(
                    f"{field_name}_not_found",
                    f"La ruta de {field_name} no existe: {path}",
                    path,
                    field_name,
                )
            )


def _validate_configured_executable_names(
    config: Mapping[str, object], errors: list[ValidationErrorDetail]
) -> None:
    for field_name, value in _iter_config_values(config, _EXECUTABLE_NAME_KEYS):
        if isinstance(value, str):
            _validate_executable_name(value, errors, field_name=field_name)
        elif value is not None:
            errors.append(
                ValidationErrorDetail(
                    "executable_name_type_invalid",
                    f"El nombre de ejecutable en {field_name} debe ser texto.",
                    field=field_name,
                )
            )


def _validate_executable_name(
    name: str, errors: list[ValidationErrorDetail], *, field_name: str
) -> None:
    if (
        not name
        or not _EXECUTABLE_NAME_RE.fullmatch(name)
        or name.endswith(".")
        or name.endswith(" ")
    ):
        errors.append(
            ValidationErrorDetail(
                "executable_name_invalid",
                f"Nombre de ejecutable inválido: {name!r}",
                field=field_name,
                hint="Usa letras, números, guion, guion bajo o punto, empezando por un carácter alfanumérico.",
            )
        )
        return
    if name.split(".", 1)[0].upper() in _RESERVED_EXECUTABLE_NAMES:
        errors.append(
            ValidationErrorDetail(
                "executable_name_reserved",
                f"Nombre de ejecutable reservado por Windows: {name!r}",
                field=field_name,
            )
        )


def _validate_configured_icon(
    config: Mapping[str, object], root: Path, errors: list[ValidationErrorDetail]
) -> None:
    for field_name, value in _iter_config_values(config, _CONFIG_PATH_KEYS):
        if isinstance(value, str) and value:
            _validate_icon_path(
                Path(value) if Path(value).is_absolute() else root / value,
                root,
                errors,
                field_name=field_name,
            )
        elif value is not None:
            errors.append(
                ValidationErrorDetail(
                    "icon_type_invalid",
                    f"El icono opcional en {field_name} debe ser una ruta de texto.",
                    field=field_name,
                )
            )


def _validate_icon_path(
    path: Path, root: Path, errors: list[ValidationErrorDetail], *, field_name: str
) -> None:
    path = path.expanduser().resolve()
    if not _is_inside_project(path, root):
        errors.append(
            ValidationErrorDetail(
                "icon_outside_project",
                f"El icono está fuera del proyecto: {path}",
                path,
                field_name,
            )
        )
    if not path.is_file():
        errors.append(
            ValidationErrorDetail(
                "icon_not_found",
                f"El icono configurado no existe: {path}",
                path,
                field_name,
            )
        )
    if path.suffix.lower() not in _ICON_SUFFIXES:
        errors.append(
            ValidationErrorDetail(
                "icon_extension_invalid",
                f"El icono debe usar una extensión compatible ({', '.join(sorted(_ICON_SUFFIXES))}): {path}",
                path,
                field_name,
            )
        )


def _validate_co_package_distinction(
    project: CobraProject, errors: list[ValidationErrorDetail]
) -> None:
    entrypoint = project.entrypoint
    if (
        entrypoint is not None
        and entrypoint.suffix.lower() == ".co"
        and entrypoint.exists()
        and es_paquete_cobra(entrypoint)
    ):
        errors.append(
            ValidationErrorDetail(
                "entrypoint_co_is_package",
                f"El entrypoint .co parece ser un paquete binario Cobra, no una fuente editable: {entrypoint}",
                entrypoint,
                "entrypoint",
            )
        )
    for raw_path in project.co_packages:
        path = Path(raw_path)
        if (
            path.suffix.lower() == ".co"
            and path.exists()
            and not es_paquete_cobra(path)
            and not zipfile.is_zipfile(path)
        ):
            errors.append(
                ValidationErrorDetail(
                    "co_package_is_text_source",
                    f"El paquete .co declarado parece una fuente de texto; muévelo a fuentes o conviértelo en paquete Cobra: {path}",
                    path,
                    "co_packages",
                )
            )


def _read_toml_mapping(
    path: Path, errors: list[ValidationErrorDetail], field_name: str
) -> dict[str, object] | None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # type: ignore[union-attr]
        errors.append(
            ValidationErrorDetail(
                f"{field_name}_syntax_invalid",
                f"{path.name} no es TOML válido: {exc}",
                path,
                field_name,
            )
        )
        return None
    except UnicodeDecodeError as exc:
        errors.append(
            ValidationErrorDetail(
                f"{field_name}_encoding_invalid",
                f"{path.name} debe poder leerse como UTF-8: {exc}",
                path,
                field_name,
            )
        )
        return None
    if not isinstance(data, dict):
        errors.append(
            ValidationErrorDetail(
                f"{field_name}_format_invalid",
                f"{path.name} debe contener un documento TOML de tablas/clave-valor.",
                path,
                field_name,
            )
        )
        return None
    return data


def _read_lock_mapping(
    path: Path, errors: list[ValidationErrorDetail]
) -> Mapping[str, object] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_encoding_invalid",
                f"cobra.lock debe poder leerse como UTF-8: {exc}",
                path,
                "cobra_lock",
            )
        )
        return None
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith(("{", "[")):
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(
                ValidationErrorDetail(
                    "cobra_lock_syntax_invalid",
                    f"cobra.lock no es JSON válido: {exc}",
                    path,
                    "cobra_lock",
                )
            )
            return None
        if isinstance(data, Mapping):
            return data
        if isinstance(data, list):
            return {"packages": data}
        errors.append(
            ValidationErrorDetail(
                "cobra_lock_format_invalid",
                "cobra.lock JSON debe ser un objeto o lista.",
                path,
                "cobra_lock",
            )
        )
        return None
    return _read_toml_mapping(path, errors, "cobra_lock")


def _iter_config_values(
    config: Mapping[str, object], keys: Sequence[str]
) -> list[tuple[str, object]]:
    values: list[tuple[str, object]] = []
    for key, value in config.items():
        if key in keys:
            values.append((key, value))
        if isinstance(value, Mapping):
            for nested_key, nested_value in _iter_config_values(value, keys):
                values.append((f"{key}.{nested_key}", nested_value))
    return values


def _is_inside_project(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


__all__ = [
    "COBRA_EXTENSIONS",
    "ValidationErrorDetail",
    "ValidationResult",
    "discover_entrypoint",
    "validate_build_options",
    "validate_project",
]
