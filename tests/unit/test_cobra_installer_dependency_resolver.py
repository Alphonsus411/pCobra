import json

import pytest

from pcobra.cobra.packaging import construir_paquete
from pcobra.cobra_installer.dependency_resolver import (
    CobraDependencyError,
    detect_cobra_imports,
    read_declared_dependencies,
    resolve_project_dependencies,
)
from pcobra.cobra_installer.hub_resolver import CobraHubResolver, CobraInstallerError


def _package(tmp_path, name="dep", version="1.2.3", dependencies=None):
    root = tmp_path / f"pkg-{name}"
    (root / "src").mkdir(parents=True)
    (root / "src" / "main.cobra").write_text("var x = 1\n", encoding="utf-8")
    manifest = {
        "format": "cobra-package-v1",
        "name": name,
        "version": version,
        "files": [],
        "checksums": {},
    }
    if dependencies:
        manifest["dependencies"] = dependencies
    (root / "cobra.pkg.json").write_text(json.dumps(manifest), encoding="utf-8")
    return construir_paquete(root)


def test_detecta_imports_cobra_estaticos(tmp_path):
    (tmp_path / "main.cobra").write_text(
        'usar dep.modulo\nimport "otra.sub"\nusar "./local.cobra"\n',
        encoding="utf-8",
    )

    assert detect_cobra_imports(tmp_path) == {"dep", "otra"}


def test_lee_dependencias_de_cobra_toml(tmp_path):
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\nDep = "1.2.3"\n[project]\ndependencies = ["otra==2.0.0"]\n',
        encoding="utf-8",
    )

    deps = read_declared_dependencies(tmp_path / "cobra.toml")

    assert deps["dep"].version == "1.2.3"
    assert deps["otra"].version == "2.0.0"


def test_resuelve_desde_cache_y_genera_lock(tmp_path):
    package = _package(tmp_path, name="dep", version="1.2.3")
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / "dep-1.2.3.co"
    cached.write_bytes(package.read_bytes())
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep = "1.2.3"\n', encoding="utf-8"
    )
    (tmp_path / "main.cobra").write_text("usar dep.modulo\n", encoding="utf-8")

    result = resolve_project_dependencies(
        tmp_path, resolver=CobraHubResolver(cache_dir=cache)
    )

    assert result.lockfile_created is True
    assert result.resolved["dep"].path == cached
    lock = json.loads((tmp_path / "cobra.lock").read_text(encoding="utf-8"))
    assert lock["packages"][0]["name"] == "dep"
    assert lock["packages"][0]["version"] == "1.2.3"
    assert len(lock["packages"][0]["sha256"]) == 64


class _FakeCobraHubRepository:
    def __init__(self, packages):
        self.packages = packages
        self.downloads = []

    def download(self, name, version=None):
        from pcobra.cobra.hub.repository import DownloadedPackage

        self.downloads.append((name, version))
        path = self.packages[(name, version)]
        sha256 = CobraHubResolver._sha256_file(path)
        return DownloadedPackage(path=path, name=name, version=version, checksum=sha256)


def test_resuelve_multiples_dependencias_desde_cache_y_cobrahub_sin_red(tmp_path):
    cached_package = _package(tmp_path, name="dep-cache", version="1.2.3")
    remote_package = _package(tmp_path, name="dep-remota", version="2.0.0")
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / "dep-cache-1.2.3.co"
    cached.write_bytes(cached_package.read_bytes())
    remote = tmp_path / "remote" / "dep-remota-2.0.0.co"
    remote.parent.mkdir()
    remote.write_bytes(remote_package.read_bytes())
    repo = _FakeCobraHubRepository({("dep-remota", "2.0.0"): remote})
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep-cache = "1.2.3"\ndep-remota = "2.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "main.cobra").write_text(
        "import 'dep-cache.modulo'\nimport 'dep-remota.api'\n", encoding="utf-8"
    )

    result = resolve_project_dependencies(
        tmp_path, resolver=CobraHubResolver(repository=repo, cache_dir=cache)
    )

    assert result.used_imports == {"dep-cache", "dep-remota"}
    assert set(result.declared) == {"dep-cache", "dep-remota"}
    assert set(result.resolved) == {"dep-cache", "dep-remota"}
    assert repo.downloads == [("dep-remota", "2.0.0")]
    assert result.resolved["dep-cache"].name == "dep-cache"
    assert result.resolved["dep-cache"].version == "1.2.3"
    assert result.resolved["dep-cache"].path == cached
    assert len(result.resolved["dep-cache"].sha256) == 64
    assert result.resolved["dep-cache"].source == "installer-cache"
    assert result.resolved["dep-remota"].name == "dep-remota"
    assert result.resolved["dep-remota"].version == "2.0.0"
    assert result.resolved["dep-remota"].path == remote
    assert len(result.resolved["dep-remota"].sha256) == 64
    assert result.resolved["dep-remota"].source == "cobrahub"
    lock = json.loads((tmp_path / "cobra.lock").read_text(encoding="utf-8"))
    assert [package["name"] for package in lock["packages"]] == [
        "dep-cache",
        "dep-remota",
    ]
    assert {package["source"] for package in lock["packages"]} == {
        "installer-cache",
        "cobrahub",
    }


def test_falla_si_import_no_esta_declarado(tmp_path):
    (tmp_path / "cobra.toml").write_text("", encoding="utf-8")
    (tmp_path / "main.cobra").write_text("usar dep.modulo\n", encoding="utf-8")

    with pytest.raises(CobraDependencyError, match="no declaradas"):
        resolve_project_dependencies(
            tmp_path, resolver=CobraHubResolver(cache_dir=tmp_path / "cache")
        )


def test_falla_hash_de_lock(tmp_path):
    package = _package(tmp_path, name="dep", version="1.2.3")
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "dep-1.2.3.co").write_bytes(package.read_bytes())
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep = "1.2.3"\n', encoding="utf-8"
    )
    (tmp_path / "main.cobra").write_text("usar dep.modulo\n", encoding="utf-8")
    (tmp_path / "cobra.lock").write_text(
        json.dumps(
            {
                "version": 1,
                "packages": [{"name": "dep", "version": "1.2.3", "sha256": "0" * 64}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CobraInstallerError, match="Hash inválido"):
        resolve_project_dependencies(
            tmp_path, resolver=CobraHubResolver(cache_dir=cache)
        )


def test_detecta_conflicto_transitivo(tmp_path):
    package = _package(
        tmp_path, name="dep", version="1.2.3", dependencies={"otra": "2.0.0"}
    )
    package2 = _package(tmp_path, name="otra", version="1.0.0")
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "dep-1.2.3.co").write_bytes(package.read_bytes())
    (cache / "otra-1.0.0.co").write_bytes(package2.read_bytes())
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep = "1.2.3"\notra = "1.0.0"\n', encoding="utf-8"
    )
    (tmp_path / "main.cobra").write_text(
        "usar dep.modulo\nusar otra.mod\n", encoding="utf-8"
    )

    with pytest.raises(CobraDependencyError, match="Conflicto de versiones"):
        resolve_project_dependencies(
            tmp_path, resolver=CobraHubResolver(cache_dir=cache)
        )
