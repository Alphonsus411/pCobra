import json
import shutil

import pytest

from pcobra.cobra.hub.errors import PackageIntegrityError, PackageResolutionError
from pcobra.cobra.hub.providers.local import LocalArtifactProvider
from pcobra.cobra_installer.dependency_resolver import (
    read_declared_dependencies,
    read_lockfile,
    resolve_project_dependencies,
)
from pcobra.cobra.packaging import construir_paquete


def _package(root, name="dep", version="1.2.3", dependencies=None):
    project = root / f"src-{name}-{version}"
    (project / "src").mkdir(parents=True)
    (project / "src" / "main.cobra").write_text("var x = 1\n", encoding="utf-8")
    manifest = {
        "format": "cobra-package-v1",
        "name": name,
        "version": version,
        "files": [],
        "checksums": {},
    }
    if dependencies is not None:
        manifest["dependencies"] = dependencies
    (project / "cobra.pkg.json").write_text(json.dumps(manifest), encoding="utf-8")
    return construir_paquete(project, root / f"{name}-{version}.co")


def test_proveedor_local_admite_ruta_directa_y_reutiliza_cache(tmp_path):
    package = _package(tmp_path)
    provider = LocalArtifactProvider(package, cache_dir=tmp_path / "cache")

    first = provider.acquire("dep", "1.2.3")
    first_mtime = first.path.stat().st_mtime_ns
    second = provider.acquire("dep", "1.2.3")

    assert first.path == second.path
    assert first.path.name == f"dep-1.2.3-{first.checksum}.co"
    assert second.path.stat().st_mtime_ns == first_mtime
    assert not list((tmp_path / "cache").glob("*.partial"))


def test_proveedor_local_busca_directorio_y_rechaza_ambiguedad(tmp_path):
    package = _package(tmp_path)
    provider = LocalArtifactProvider(tmp_path, cache_dir=tmp_path / "cache")
    assert provider.acquire("dep", "1.2.3").name == "dep"

    shutil.copy2(package, tmp_path / "copia.co")
    with pytest.raises(PackageResolutionError, match="ambiguo"):
        provider.acquire("dep", "1.2.3")


def test_proveedor_local_rechaza_hash_e_identidad_discordante(tmp_path):
    package = _package(tmp_path, name="otro", version="2.0.0")
    provider = LocalArtifactProvider(package, cache_dir=tmp_path / "cache")

    with pytest.raises(PackageResolutionError, match="discordante"):
        provider.acquire("dep", "1.2.3")
    with pytest.raises(PackageIntegrityError, match="Hash inválido"):
        provider.acquire("otro", "2.0.0", expected_sha256="0" * 64)


def test_toml_y_lock_resuelven_sources_relativos_a_su_archivo(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    (project / "cobra.toml").write_text(
        '[dependencies]\ndep = { version = "1.2.3", source = "../artifacts" }\n',
        encoding="utf-8",
    )
    (project / "cobra.lock").write_text(
        json.dumps(
            {
                "version": 2,
                "packages": {"dep": {"version": "1.2.3", "source": "../artifacts"}},
            }
        ),
        encoding="utf-8",
    )

    assert read_declared_dependencies(project / "cobra.toml")["dep"].source == str(
        artifacts
    )
    assert read_lockfile(project / "cobra.lock")["dep"].source == str(artifacts)


def test_resolucion_offline_local_incluye_dependencia_transitiva(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    _package(artifacts, name="child", version="2.0.0")
    _package(artifacts, name="dep", version="1.2.3", dependencies={"child": "2.0.0"})
    project = tmp_path / "project"
    project.mkdir()
    (project / "cobra.toml").write_text(
        '[dependencies]\ndep = { version = "1.2.3", source = "../artifacts" }\n',
        encoding="utf-8",
    )
    (project / "main.cobra").write_text("usar dep.modulo\n", encoding="utf-8")

    result = resolve_project_dependencies(project)

    assert set(result.resolved) == {"child", "dep"}
    assert all(item.path.is_file() for item in result.resolved.values())


def test_lock_v1_local_relativo_se_usa_offline(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    package = _package(artifacts)
    project = tmp_path / "project"
    project.mkdir()
    (project / "cobra.toml").write_text(
        '[dependencies]\ndep = "1.2.3"\n', encoding="utf-8"
    )
    (project / "main.cobra").write_text("usar dep.modulo\n", encoding="utf-8")
    from pcobra.cobra.hub.integrity import sha256_file

    (project / "cobra.lock").write_text(
        json.dumps(
            {
                "version": 1,
                "packages": [
                    {
                        "name": "dep",
                        "version": "1.2.3",
                        "sha256": sha256_file(package),
                        "source": "../artifacts",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    assert resolve_project_dependencies(project).resolved["dep"].source == str(
        artifacts
    )
