import json

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
        return DownloadedPackage(path=path, name=name, version=version, checksum=checksum)


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
