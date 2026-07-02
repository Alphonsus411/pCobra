import json

import pytest

from pcobra.cobra.hub.repository import DownloadedPackage
from pcobra.cobra.packaging import construir_paquete
from pcobra.cobra_installer.hub_resolver import CobraHubResolver


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


class FakeCobraHubRepository:
    def __init__(self, packages):
        self.packages = packages
        self.downloads = []

    def download(self, name, version=None):
        self.downloads.append((name, version))
        path = self.packages[(name, version)]
        checksum = CobraHubResolver._sha256_file(path)
        return DownloadedPackage(
            path=path, name=name, version=version, checksum=checksum
        )


def test_hub_resolver_devuelve_paquete_cacheado_con_hash_ruta_y_origen(tmp_path):
    package = _package(tmp_path, name="dep-cache", version="1.2.3")
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / "dep-cache-1.2.3.co"
    cached.write_bytes(package.read_bytes())
    expected_hash = CobraHubResolver._sha256_file(cached)

    result = CobraHubResolver(cache_dir=cache).resolve(
        "dep-cache", "1.2.3", expected_sha256=expected_hash
    )

    assert result.name == "dep-cache"
    assert result.version == "1.2.3"
    assert result.sha256 == expected_hash
    assert result.path == cached
    assert result.source == "installer-cache"


def test_hub_resolver_descarga_desde_repositorio_mock_sin_red(tmp_path):
    remote = _package(
        tmp_path,
        name="dep-remota",
        version="2.0.0",
        dependencies={"dep-cache": "1.2.3"},
    )
    remote_target = tmp_path / "remote" / "dep-remota-2.0.0.co"
    remote_target.parent.mkdir()
    remote_target.write_bytes(remote.read_bytes())
    repo = FakeCobraHubRepository({("dep-remota", "2.0.0"): remote_target})
    expected_hash = CobraHubResolver._sha256_file(remote_target)

    result = CobraHubResolver(repository=repo, cache_dir=tmp_path / "cache").resolve(
        "dep-remota", "2.0.0", expected_sha256=expected_hash
    )

    assert repo.downloads == [("dep-remota", "2.0.0")]
    assert result.name == "dep-remota"
    assert result.version == "2.0.0"
    assert result.sha256 == expected_hash
    assert result.path == remote_target
    assert result.source == "cobrahub"
    assert result.dependencies == {"dep-cache": "1.2.3"}


class MultiPackageCobraHubFixture:
    def __init__(self, tmp_path):
        self.cache_dir = tmp_path / "cache"
        self.cache_dir.mkdir()
        self.remote_dir = tmp_path / "remote"
        self.remote_dir.mkdir()

        cache_package = _package(tmp_path, name="dep-cache", version="1.2.3")
        remote_package = _package(
            tmp_path,
            name="dep-remota",
            version="2.0.0",
            dependencies={"dep-cache": "1.2.3"},
        )
        self.cached_path = self.cache_dir / "dep-cache-1.2.3.co"
        self.cached_path.write_bytes(cache_package.read_bytes())
        self.remote_path = self.remote_dir / "dep-remota-2.0.0.co"
        self.remote_path.write_bytes(remote_package.read_bytes())
        self.hashes = {
            "dep-cache": CobraHubResolver._sha256_file(self.cached_path),
            "dep-remota": CobraHubResolver._sha256_file(self.remote_path),
        }
        self.repository = FakeCobraHubRepository(
            {("dep-remota", "2.0.0"): self.remote_path}
        )


@pytest.fixture
def multi_package_hub_fixture(tmp_path):
    return MultiPackageCobraHubFixture(tmp_path)


def test_hub_resolver_resuelve_multiples_paquetes_cache_y_remoto_sin_red(
    multi_package_hub_fixture,
):
    fixture = multi_package_hub_fixture
    resolver = CobraHubResolver(
        repository=fixture.repository,
        cache_dir=fixture.cache_dir,
    )

    cached_result = resolver.resolve(
        "dep-cache", "1.2.3", expected_sha256=fixture.hashes["dep-cache"]
    )
    remote_result = resolver.resolve(
        "dep-remota", "2.0.0", expected_sha256=fixture.hashes["dep-remota"]
    )

    assert fixture.repository.downloads == [("dep-remota", "2.0.0")]
    assert {
        cached_result.name: {
            "version": cached_result.version,
            "hash": cached_result.sha256,
            "path": cached_result.path,
            "source": cached_result.source,
        },
        remote_result.name: {
            "version": remote_result.version,
            "hash": remote_result.sha256,
            "path": remote_result.path,
            "source": remote_result.source,
        },
    } == {
        "dep-cache": {
            "version": "1.2.3",
            "hash": fixture.hashes["dep-cache"],
            "path": fixture.cached_path,
            "source": "installer-cache",
        },
        "dep-remota": {
            "version": "2.0.0",
            "hash": fixture.hashes["dep-remota"],
            "path": fixture.remote_path,
            "source": "cobrahub",
        },
    }
    assert remote_result.dependencies == {"dep-cache": "1.2.3"}
