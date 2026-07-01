"""Herramientas independientes para paquetes Cobra ``.co``.

Este módulo no participa en Lexer ni Parser: opera sobre archivos y metadatos.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_NAME = "cobra.pkg.json"
LEGACY_MANIFEST_NAME = "cobra.pkg"
PACKAGE_FORMAT = "cobra-package-v1"
DEFAULT_CACHE_DIR = Path.home() / ".cobra" / "hub" / "cache"
DEFAULT_INSTALL_DIR = Path.home() / ".cobra" / "packages"
MAX_PACKAGE_SIZE = 50 * 1024 * 1024
_PACKAGE_NAME_RE = re.compile(r"^[a-z0-9_.-]+$")
_SIMPLE_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)

__all__ = [
    "crear_paquete",
    "validar_paquete",
    "construir_paquete",
    "extraer_paquete",
    "inspeccionar_paquete",
    "verificar_integridad",
    "es_paquete_cobra",
]


@dataclass(frozen=True)
class PackageManifest:
    """Modelo explícito del manifiesto de un paquete Cobra."""

    format: str
    name: str
    version: str
    files: list[str]
    checksums: dict[str, str]
    description: str | None = None
    authors: list[str] | None = None
    license: str | None = None
    homepage: str | None = None
    dependencies: dict[str, str] | None = None


def manifest_from_dict(data: dict[str, Any]) -> PackageManifest:
    """Convierte un diccionario JSON en un manifiesto Cobra validado.

    Mantiene compatibilidad con manifiestos históricos que solo declaran
    ``format``, ``name``, ``version``, ``files`` y ``checksums``.
    """
    package_format = data.get("format")
    if package_format is None:
        raise ValueError("El manifiesto no declara format")
    if package_format != PACKAGE_FORMAT:
        raise ValueError(f"Formato de paquete no soportado: {package_format}")

    name = data.get("name")
    if not name:
        raise ValueError("El manifiesto no declara name")

    version = data.get("version")
    if not version:
        raise ValueError("El manifiesto no declara version")

    files = data.get("files", [])
    checksums = data.get("checksums", {})
    if not isinstance(files, list):
        raise ValueError("El manifiesto debe declarar files como lista")
    if not isinstance(checksums, dict):
        raise ValueError("El manifiesto debe declarar checksums como objeto")

    authors = data.get("authors")
    if authors is not None and not isinstance(authors, list):
        raise ValueError("El manifiesto debe declarar authors como lista")

    dependencies = data.get("dependencies")
    if dependencies is not None and not isinstance(dependencies, dict):
        raise ValueError("El manifiesto debe declarar dependencies como objeto")

    return PackageManifest(
        format=str(package_format),
        name=normalizar_nombre_paquete(str(name)),
        version=validar_version_paquete(str(version)),
        files=[str(file) for file in files],
        checksums={str(name): checksum for name, checksum in checksums.items()},
        description=(
            None if data.get("description") is None else str(data.get("description"))
        ),
        authors=None if authors is None else [str(author) for author in authors],
        license=None if data.get("license") is None else str(data.get("license")),
        homepage=None if data.get("homepage") is None else str(data.get("homepage")),
        dependencies=(
            None
            if dependencies is None
            else {str(name): str(value) for name, value in dependencies.items()}
        ),
    )


def manifest_to_dict(manifest: PackageManifest) -> dict[str, Any]:
    """Convierte un ``PackageManifest`` en un diccionario JSON-compatible."""
    data: dict[str, Any] = {
        "format": manifest.format,
        "name": manifest.name,
        "version": manifest.version,
        "files": list(manifest.files),
        "checksums": dict(manifest.checksums),
    }
    optional_fields = {
        "description": manifest.description,
        "authors": manifest.authors,
        "license": manifest.license,
        "homepage": manifest.homepage,
        "dependencies": manifest.dependencies,
    }
    for key, value in optional_fields.items():
        if value is not None:
            data[key] = (
                list(value)
                if isinstance(value, list)
                else dict(value) if isinstance(value, dict) else value
            )
    return data


@dataclass(frozen=True)
class PackageSearchResult:
    """Metadatos normalizados para resultados remotos de CobraHub."""

    name: str
    version: str | None = None
    filename: str | None = None
    checksum: str | None = None
    download_url: str | None = None
    remote_id: str | None = None
    description: str | None = None
    authors: list[str] | None = None
    license: str | None = None
    homepage: str | None = None
    dependencies: dict[str, str] | None = None

    def as_dict(self) -> dict[str, Any]:
        """Devuelve solo los campos disponibles para mantener compatibilidad JSON."""
        values = {
            "name": self.name,
            "version": self.version,
            "filename": self.filename,
            "checksum": self.checksum,
            "download_url": self.download_url,
            "remote_id": self.remote_id,
            "description": self.description,
            "authors": self.authors,
            "license": self.license,
            "homepage": self.homepage,
            "dependencies": self.dependencies,
        }
        return {key: value for key, value in values.items() if value is not None}


@dataclass(frozen=True)
class PackageInspection:
    path: Path
    manifest: dict[str, Any]
    files: list[str]
    checksum: str


def normalizar_nombre_paquete(nombre: str) -> str:
    """Normaliza y valida la identidad pública de un paquete Cobra.

    Política de nombres:
    - se recortan espacios externos y se convierten espacios internos a ``-``;
    - el resultado siempre se guarda en minúsculas;
    - solo se admiten letras ASCII, números, ``_``, ``-`` y ``.``;
    - no se admiten separadores de ruta, segmentos vacíos separados por ``.`` ni
      segmentos ``..`` para evitar ambigüedad o traversal en cachés/instalación.
    """
    normalized = str(nombre).strip().lower().replace(" ", "-")
    if not normalized:
        raise ValueError("Nombre de paquete inválido")
    if "/" in normalized or "\\" in normalized:
        raise ValueError("Nombre de paquete inválido")
    if not _PACKAGE_NAME_RE.fullmatch(normalized):
        raise ValueError("Nombre de paquete inválido")
    if any(part in {"", ".."} for part in normalized.split(".")):
        raise ValueError("Nombre de paquete inválido")
    return normalized


def validar_version_paquete(version: str) -> str:
    """Valida y devuelve una versión SemVer simple para paquetes Cobra.

    La versión debe seguir ``MAJOR.MINOR.PATCH`` con enteros no negativos sin
    ceros a la izquierda, y puede incluir sufijo prerelease ``-...`` y metadatos
    de build ``+...`` compatibles con SemVer.
    """
    normalized = str(version).strip()
    if not normalized or not _SIMPLE_SEMVER_RE.fullmatch(normalized):
        raise ValueError("Versión de paquete inválida")
    return normalized


def _safe_name(name: str) -> str:
    return normalizar_nombre_paquete(name)


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
    """API pública: crea una estructura base de paquete Cobra en ``source``.

    Genera el directorio raíz, ``src/`` y un manifiesto ``cobra.pkg.json``
    mínimo cuando todavía no existe. CLI, IDLE e integraciones externas deben
    usar esta función como único punto de entrada para inicializar paquetes
    ``.co``.
    """
    root = Path(source)
    root.mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    manifest = manifest_to_dict(
        PackageManifest(
            format=PACKAGE_FORMAT,
            name=normalizar_nombre_paquete(nombre),
            version=validar_version_paquete(version),
            files=[],
            checksums={},
        )
    )
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(f"# {nombre}\n\nPaquete Cobra.\n", encoding="utf-8")
    return manifest_path


def construir_paquete(
    source: str | Path,
    output: str | Path | None = None,
    *,
    nombre: str | None = None,
    version: str | None = None,
) -> Path:
    """API pública: construye un archivo ``.co`` ZIP con manifiesto e integridad.

    Recorre el directorio fuente, regenera ``files`` y ``checksums`` en el
    manifiesto y escribe un contenedor publicable. Esta función es la fuente de
    verdad para crear artefactos ``.co`` desde CLI, IDLE y CobraHub.
    """
    root = Path(source).resolve()
    if not root.is_dir():
        raise ValueError("La fuente del paquete debe ser un directorio")
    manifest_path = root / MANIFEST_NAME
    if manifest_path.exists():
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = manifest_from_dict(manifest_data)
    else:
        manifest = PackageManifest(
            format=PACKAGE_FORMAT,
            name=str(nombre or root.name),
            version=validar_version_paquete(str(version or "0.1.0")),
            files=[],
            checksums={},
        )

    files = [
        p
        for p in _iter_package_files(root)
        if p.relative_to(root).as_posix() != MANIFEST_NAME
    ]
    checksums = {p.relative_to(root).as_posix(): _sha256_file(p) for p in files}
    manifest = PackageManifest(
        format=PACKAGE_FORMAT,
        name=normalizar_nombre_paquete(str(nombre or manifest.name or root.name)),
        version=validar_version_paquete(str(version or manifest.version or "0.1.0")),
        files=list(checksums),
        checksums=checksums,
        description=manifest.description,
        authors=manifest.authors,
        license=manifest.license,
        homepage=manifest.homepage,
        dependencies=manifest.dependencies,
    )
    manifest_data = manifest_to_dict(manifest)
    dest = (
        Path(output)
        if output
        else root.parent / f"{manifest.name}-{manifest.version}.co"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            MANIFEST_NAME,
            json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n",
        )
        for file in files:
            zf.write(file, file.relative_to(root).as_posix())
    return dest


def es_paquete_cobra(path: str | Path) -> bool:
    """API pública: indica si ``path`` es un paquete Cobra ``.co`` ZIP con manifiesto.

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
    """API pública: devuelve manifiesto, entradas y SHA-256 del paquete ``.co``.

    Realiza la comprobación estructural básica del contenedor antes de leer sus
    metadatos, sin extraer archivos ni invocar Lexer/Parser.
    """
    pkg = Path(package)
    if not pkg.exists():
        raise FileNotFoundError(f"Paquete no encontrado: {pkg}")
    if pkg.stat().st_size > MAX_PACKAGE_SIZE:
        raise ValueError("El paquete excede el tamaño máximo permitido")
    if not es_paquete_cobra(pkg):
        raise ValueError(
            "El paquete no es un paquete Cobra válido: debe ser ZIP y contener cobra.pkg.json"
        )
    with zipfile.ZipFile(pkg) as zf:
        names = zf.namelist()
        manifest = manifest_from_dict(
            json.loads(zf.read(MANIFEST_NAME).decode("utf-8"))
        )
    return PackageInspection(pkg, manifest_to_dict(manifest), names, _sha256_file(pkg))


def _normalizar_ruta_paquete(name: str) -> str:
    raw_name = str(name)
    if not raw_name:
        raise ValueError(f"Ruta inválida en paquete: {name}")
    if "\\" in raw_name:
        raise ValueError(f"Ruta insegura en paquete: {name}")
    if raw_name.startswith("/") or re.match(r"^[A-Za-z]:", raw_name):
        raise ValueError(f"Ruta insegura en paquete: {name}")

    parts = raw_name.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Ruta insegura en paquete: {name}")
    return "/".join(parts)


def _zipinfo_es_symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_ISLNK((info.external_attr >> 16) & 0o170000)


def _validar_entrada_zip(info: zipfile.ZipInfo) -> str:
    if _zipinfo_es_symlink(info):
        raise ValueError(f"Symlink no permitido en paquete: {info.filename}")
    filename = info.filename.rstrip("/") if info.is_dir() else info.filename
    return _normalizar_ruta_paquete(filename)


def _validar_entradas_zip(zf: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    entries: dict[str, zipfile.ZipInfo] = {}
    for info in zf.infolist():
        normalized_name = _validar_entrada_zip(info)
        if normalized_name in entries:
            raise ValueError(f"Entrada duplicada en paquete: {normalized_name}")
        entries[normalized_name] = info
    return entries


def _normalizar_lista_archivos(values: Any, *, field: str) -> set[str]:
    if not isinstance(values, list):
        raise ValueError(f"El manifiesto debe declarar {field} como lista")
    return {_normalizar_ruta_paquete(str(value)) for value in values}


def _validar_checksum_sha256(name: str, checksum: Any) -> str:
    if not isinstance(checksum, str):
        raise ValueError(f"Checksum inválido para {name}: debe ser una cadena")
    if len(checksum) != 64:
        raise ValueError(f"Checksum inválido para {name}: debe tener 64 caracteres")
    if not all(char in "0123456789abcdefABCDEF" for char in checksum):
        raise ValueError(
            f"Checksum inválido para {name}: debe contener solo caracteres hexadecimales"
        )
    return checksum


def _normalizar_checksums(values: Any) -> dict[str, str]:
    if not isinstance(values, dict):
        raise ValueError("El manifiesto debe declarar checksums como objeto")
    return {
        normalized_name: _validar_checksum_sha256(normalized_name, checksum)
        for name, checksum in values.items()
        for normalized_name in [_normalizar_ruta_paquete(str(name))]
    }


def validar_paquete(package: str | Path) -> PackageInspection:
    """API pública: valida manifiesto, rutas declaradas y checksums del ``.co``.

    Es el contrato canónico que deben usar CLI, IDLE y CobraHub antes de
    publicar, instalar o confiar en un paquete Cobra.
    """
    inspection = inspeccionar_paquete(package)
    manifest = manifest_from_dict(inspection.manifest)

    declared_files = _normalizar_lista_archivos(manifest.files, field="files")
    checksums = _normalizar_checksums(manifest.checksums)

    with zipfile.ZipFile(inspection.path) as zf:
        entries = _validar_entradas_zip(zf)
        real_files = {
            name
            for name, info in entries.items()
            if not info.is_dir() and name != MANIFEST_NAME
        }
        extra_files = real_files - declared_files
        if extra_files:
            raise ValueError(
                f"Archivos no declarados en paquete: {', '.join(sorted(extra_files))}"
            )

        missing_files = declared_files - real_files
        if missing_files:
            raise ValueError(
                f"Archivos declarados ausentes: {', '.join(sorted(missing_files))}"
            )

        checksum_files = set(checksums)
        undeclared_checksums = checksum_files - declared_files
        if undeclared_checksums:
            raise ValueError(
                f"Checksums para archivos no declarados: {', '.join(sorted(undeclared_checksums))}"
            )

        missing_checksums = declared_files - checksum_files
        if missing_checksums:
            raise ValueError(
                f"Faltan checksums para archivos declarados: {', '.join(sorted(missing_checksums))}"
            )

        for name in sorted(declared_files):
            actual = _sha256_bytes(zf.read(entries[name]))
            if actual != checksums[name]:
                raise ValueError(f"Integridad fallida para {name}")
    return inspection


def extraer_paquete(package: str | Path, destination: str | Path) -> Path:
    """API pública: valida y extrae un paquete ``.co`` en ``destination``.

    Todas las rutas internas se normalizan y se comprueba que permanezcan bajo
    el destino para evitar traversal durante la instalación o apertura desde
    herramientas de usuario.
    """
    inspection = validar_paquete(package)
    dest = Path(destination).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(inspection.path) as zf:
        entries = _validar_entradas_zip(zf)
        for name, info in entries.items():
            target = (dest / name).resolve()
            target.relative_to(dest)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, target.open("wb") as out:
                    shutil.copyfileobj(src, out)
    return dest


def verificar_integridad(package: str | Path) -> bool:
    """API pública: confirma que la integridad SHA-256 del ``.co`` es válida.

    Devuelve ``True`` cuando ``validar_paquete`` finaliza sin errores; propaga
    la excepción de validación cuando el artefacto está corrupto o incompleto.
    """
    validar_paquete(package)
    return True
