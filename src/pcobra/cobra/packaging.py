"""Herramientas independientes para paquetes Cobra ``.co``.

Este módulo no participa en Lexer ni Parser: opera sobre archivos y metadatos.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_NAME = "cobra.pkg.json"
LEGACY_MANIFEST_NAME = "cobra.pkg"
PACKAGE_FORMAT = "cobra-package-v1"
DEFAULT_CACHE_DIR = Path.home() / ".cobra" / "hub" / "cache"
DEFAULT_INSTALL_DIR = Path.home() / ".cobra" / "packages"
ALLOWED_TEXT_SUFFIXES = {".cobra", ".co", ".md", ".markdown", ".txt", ".json", ".toml", ".yaml", ".yml"}
MAX_PACKAGE_SIZE = 50 * 1024 * 1024


@dataclass(frozen=True)
class PackageSearchResult:
    """Metadatos normalizados para resultados remotos de CobraHub."""

    name: str
    version: str | None = None
    filename: str | None = None
    checksum: str | None = None
    download_url: str | None = None
    remote_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        """Devuelve solo los campos disponibles para mantener compatibilidad JSON."""
        values = {
            "name": self.name,
            "version": self.version,
            "filename": self.filename,
            "checksum": self.checksum,
            "download_url": self.download_url,
            "remote_id": self.remote_id,
        }
        return {key: value for key, value in values.items() if value is not None}


@dataclass(frozen=True)
class PackageInspection:
    path: Path
    manifest: dict[str, Any]
    files: list[str]
    checksum: str


def _safe_name(name: str) -> str:
    normalized = name.strip().replace(" ", "-")
    if not normalized or any(part in {"..", ""} for part in normalized.split("/")):
        raise ValueError("Nombre de paquete inválido")
    return normalized


def _sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _iter_package_files(source: Path) -> list[Path]:
    ignored = {".git", "__pycache__", ".pytest_cache"}
    files: list[Path] = []
    for path in source.rglob("*"):
        if any(part in ignored for part in path.relative_to(source).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(source).as_posix())


def crear_paquete(source: str | Path, *, nombre: str, version: str = "0.1.0") -> Path:
    """Crea una estructura base de paquete Cobra en ``source``."""
    root = Path(source)
    root.mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    manifest = {
        "format": PACKAGE_FORMAT,
        "name": _safe_name(nombre),
        "version": version,
        "files": [],
        "checksums": {},
    }
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(f"# {nombre}\n\nPaquete Cobra.\n", encoding="utf-8")
    return manifest_path


def construir_paquete(source: str | Path, output: str | Path | None = None, *, nombre: str | None = None, version: str | None = None) -> Path:
    """Construye un archivo ``.co`` ZIP con manifiesto e integridad."""
    root = Path(source).resolve()
    if not root.is_dir():
        raise ValueError("La fuente del paquete debe ser un directorio")
    manifest_path = root / MANIFEST_NAME
    manifest: dict[str, Any]
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"format": PACKAGE_FORMAT, "name": nombre or root.name, "version": version or "0.1.0"}
    manifest["format"] = PACKAGE_FORMAT
    manifest["name"] = _safe_name(str(nombre or manifest.get("name") or root.name))
    manifest["version"] = str(version or manifest.get("version") or "0.1.0")

    files = [p for p in _iter_package_files(root) if p.relative_to(root).as_posix() != MANIFEST_NAME]
    checksums = {p.relative_to(root).as_posix(): _sha256_file(p) for p in files}
    manifest["files"] = list(checksums)
    manifest["checksums"] = checksums
    dest = Path(output) if output else root.parent / f"{manifest['name']}-{manifest['version']}.co"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        for file in files:
            zf.write(file, file.relative_to(root).as_posix())
    return dest


def es_paquete_cobra(path: str | Path) -> bool:
    """Indica si ``path`` es un paquete Cobra ``.co`` ZIP con manifiesto.

    La detección es deliberadamente estructural y barata: no usa Lexer ni Parser,
    solo comprueba que el archivo sea un ZIP legible y que contenga
    ``cobra.pkg.json`` en la raíz del archivo.
    """
    candidate = Path(path)
    if not candidate.is_file() or not zipfile.is_zipfile(candidate):
        return False
    try:
        with zipfile.ZipFile(candidate) as zf:
            return MANIFEST_NAME in zf.namelist()
    except (OSError, zipfile.BadZipFile):
        return False


def inspeccionar_paquete(package: str | Path) -> PackageInspection:
    pkg = Path(package)
    if not pkg.exists():
        raise FileNotFoundError(f"Paquete no encontrado: {pkg}")
    if pkg.stat().st_size > MAX_PACKAGE_SIZE:
        raise ValueError("El paquete excede el tamaño máximo permitido")
    if not es_paquete_cobra(pkg):
        raise ValueError("El paquete no es un paquete Cobra válido: debe ser ZIP y contener cobra.pkg.json")
    with zipfile.ZipFile(pkg) as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
    return PackageInspection(pkg, manifest, names, _sha256_file(pkg))


def _normalizar_ruta_paquete(name: str) -> str:
    normalized = Path(str(name).replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"Ruta insegura en paquete: {name}")
    normalized_name = normalized.as_posix()
    if not normalized_name or normalized_name == ".":
        raise ValueError(f"Ruta inválida en paquete: {name}")
    return normalized_name


def _normalizar_lista_archivos(values: Any, *, field: str) -> set[str]:
    if not isinstance(values, list):
        raise ValueError(f"El manifiesto debe declarar {field} como lista")
    return {_normalizar_ruta_paquete(str(value)) for value in values}


def _normalizar_checksums(values: Any) -> dict[str, Any]:
    if not isinstance(values, dict):
        raise ValueError("El manifiesto debe declarar checksums como objeto")
    return {_normalizar_ruta_paquete(str(name)): checksum for name, checksum in values.items()}


def validar_paquete(package: str | Path) -> PackageInspection:
    inspection = inspeccionar_paquete(package)
    manifest = inspection.manifest
    package_format = manifest.get("format")
    if package_format is None:
        raise ValueError("El manifiesto no declara format")
    if package_format != PACKAGE_FORMAT:
        raise ValueError(f"Formato de paquete no soportado: {package_format}")
    if not manifest.get("name"):
        raise ValueError("El manifiesto no declara name")
    if not manifest.get("version"):
        raise ValueError("El manifiesto no declara version")

    declared_files = _normalizar_lista_archivos(manifest.get("files"), field="files")
    checksums = _normalizar_checksums(manifest.get("checksums"))

    with zipfile.ZipFile(inspection.path) as zf:
        real_files = {
            _normalizar_ruta_paquete(info.filename)
            for info in zf.infolist()
            if not info.is_dir() and info.filename != MANIFEST_NAME
        }
        extra_files = real_files - declared_files
        if extra_files:
            raise ValueError(f"Archivos no declarados en paquete: {', '.join(sorted(extra_files))}")

        missing_files = declared_files - real_files
        if missing_files:
            raise ValueError(f"Archivos declarados ausentes: {', '.join(sorted(missing_files))}")

        checksum_files = set(checksums)
        undeclared_checksums = checksum_files - declared_files
        if undeclared_checksums:
            raise ValueError(f"Checksums para archivos no declarados: {', '.join(sorted(undeclared_checksums))}")

        missing_checksums = declared_files - checksum_files
        if missing_checksums:
            raise ValueError(f"Faltan checksums para archivos declarados: {', '.join(sorted(missing_checksums))}")

        for name in sorted(declared_files):
            actual = _sha256_bytes(zf.read(name))
            if actual != checksums[name]:
                raise ValueError(f"Integridad fallida para {name}")
    return inspection


def extraer_paquete(package: str | Path, destination: str | Path) -> Path:
    inspection = validar_paquete(package)
    dest = Path(destination).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(inspection.path) as zf:
        for name in inspection.files:
            target = (dest / name).resolve()
            target.relative_to(dest)
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src, target.open("wb") as out:
                    shutil.copyfileobj(src, out)
    return dest


def verificar_integridad(package: str | Path) -> bool:
    validar_paquete(package)
    return True
