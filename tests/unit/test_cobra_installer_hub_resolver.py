import json
import hashlib
import zipfile

import pytest

from pcobra.cobra.hub.errors import PackageCompatibilityError
from pcobra.cobra.hub.models import PackageDistribution
from pcobra.cobra.hub.repository import DownloadedPackage
from pcobra.cobra.packaging import construir_paquete
from pcobra.cobra_installer.hub_resolver import CobraHubResolver
from pcobra.cobra_installer.project import CobraInstallerError


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


def _package_v2(
    tmp_path, distribution_type="cobra-package", requires_cobra=">=10.0,<11"
):
    package = tmp_path / f"dep-v2-{distribution_type}.co"
    artifact = b"contenido estatico"
    artifact_path = "dist/dep.co"
    manifest = {
        "format": "cobra-package-v2",
        "name": "dep-v2",
        "version": "2.1.0",
        "package_type": "library",
        "requires_cobra": requires_cobra,
        "exports": ["dep.api"],
        "capabilities": ["net"],
        "platforms": ["linux"],
        "architectures": ["x86_64"],
        "dependencies": {"base": "1.0.0"},
        "distributions": [
            {
                "type": distribution_type,
                "path": artifact_path,
                "platforms": ["linux"],
                "architectures": ["x86_64"],
            }
        ],
        "extensions": [
            {
                "namespace": "cobra.extensions",
                "provider": "dep-provider",
                "capabilities": ["net"],
                "entrypoint": "malicious.module:run",
            }
        ],
        "files": [artifact_path],
        "checksums": {artifact_path: hashlib.sha256(artifact).hexdigest()},
    }
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("cobra.pkg.json", json.dumps(manifest))
        archive.writestr(artifact_path, artifact)
    return package


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


def test_hub_resolver_v2_selecciona_cobra_package_y_normaliza_metadata(
    tmp_path, monkeypatch
):
    imported = []
    original_import = __import__
    monkeypatch.setattr(
        "builtins.__import__",
        lambda name, *args, **kwargs: (
            imported.append(name) or original_import(name, *args, **kwargs)
        ),
    )
    package = _package_v2(tmp_path)

    result = CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
        "dep-v2",
        "2.1.0",
        source=str(package),
        platform="linux",
        architecture="x86_64",
    )

    assert result.dependencies == {"base": "1.0.0"}
    assert result.metadata == {
        "package_type": "library",
        "requires_cobra": ">=10.0,<11",
        "exports": ["dep.api"],
        "capabilities": ["net"],
        "extensions": [
            {
                "namespace": "cobra.extensions",
                "provider": "dep-provider",
                "capabilities": ["net"],
                "entrypoint": "malicious.module:run",
            }
        ],
        "platforms": ["linux"],
        "architectures": ["x86_64"],
        "distributions": [
            {
                "type": "cobra-package",
                "path": "dist/dep.co",
                "platforms": ["linux"],
                "architectures": ["x86_64"],
            }
        ],
        "artifact_type": "cobra-package",
        "artifact": "dist/dep.co",
    }
    assert "malicious.module" not in imported


def test_hub_resolver_v2_acepta_version_cobra_compatible(tmp_path, monkeypatch):
    package = _package_v2(tmp_path, requires_cobra=">=10.1,!=10.2")
    monkeypatch.setattr(
        "pcobra.cobra.hub.installation.installed_cobra_version", lambda: "10.1.1"
    )

    result = CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
        "dep-v2", "2.1.0", source=str(package), platform="linux", architecture="x86_64"
    )

    assert result.name == "dep-v2"


def test_hub_resolver_v2_rechaza_version_cobra_incompatible(tmp_path, monkeypatch):
    package = _package_v2(tmp_path, requires_cobra=">=11,<12")
    monkeypatch.setattr(
        "pcobra.cobra.hub.installation.installed_cobra_version", lambda: "10.1.1"
    )

    with pytest.raises(CobraInstallerError) as exc_info:
        CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
            "dep-v2", "2.1.0", source=str(package), platform="linux", architecture="x86_64"
        )

    message = str(exc_info.value)
    assert "dep-v2" in message
    assert "10.1.1" in message
    assert ">=11,<12" in message
    assert isinstance(exc_info.value.__cause__, PackageCompatibilityError)


def test_hub_resolver_v2_rechaza_restriccion_cobra_invalida(tmp_path):
    package = _package_v2(tmp_path, requires_cobra=">=10 || <11")

    with pytest.raises(CobraInstallerError, match="requires_cobra.*restricción"):
        CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
            "dep-v2", "2.1.0", source=str(package), platform="linux", architecture="x86_64"
        )


@pytest.mark.parametrize(
    "distribution_type",
    [
        "python-wheel",
        "python-sdist",
        "javascript-package",
        "rust-binary",
        "wasm",
        "native-binary",
    ],
)
def test_hub_resolver_rechaza_distribuciones_aun_no_instalables(
    tmp_path, distribution_type
):
    package = _package_v2(tmp_path, distribution_type)
    with pytest.raises(
        CobraInstallerError, match=f"{distribution_type!r}.*no es instalable"
    ):
        CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
            "dep-v2",
            "2.1.0",
            source=str(package),
            platform="linux",
            architecture="x86_64",
        )


def test_select_distribution_prioriza_cobra_package_compatible():
    distributions = (
        PackageDistribution(
            type="python-wheel",
            path="dist/dep.whl",
            platforms=("linux",),
            architectures=("x86_64",),
        ),
        PackageDistribution(
            type="cobra-package",
            path="dist/dep.co",
            platforms=("linux",),
            architectures=("x86_64",),
        ),
    )

    selected = CobraHubResolver._select_distribution(distributions, "linux", "x86_64")

    assert selected == distributions[1]


def test_select_distribution_informa_tipos_compatibles_no_instalables():
    distributions = (
        PackageDistribution(type="python-wheel", path="dist/dep.whl"),
        PackageDistribution(type="wasm", path="dist/dep.wasm"),
    )

    with pytest.raises(PackageCompatibilityError) as exc_info:
        CobraHubResolver._select_distribution(distributions, "linux", "x86_64")

    message = str(exc_info.value)
    assert "'python-wheel'" in message
    assert "'wasm'" in message
    assert "no son instalables" in message


def test_select_distribution_conserva_error_sin_coincidencia_de_entorno():
    distributions = (
        PackageDistribution(
            type="cobra-package",
            path="dist/windows.co",
            platforms=("windows",),
            architectures=("x86_64",),
        ),
        PackageDistribution(
            type="cobra-package",
            path="dist/arm.co",
            platforms=("linux",),
            architectures=("arm64",),
        ),
    )

    with pytest.raises(
        PackageCompatibilityError,
        match=(
            "No hay una distribución compatible con la plataforma 'linux' "
            "y la arquitectura 'x86_64'\\."
        ),
    ):
        CobraHubResolver._select_distribution(distributions, "linux", "x86_64")


def test_hub_resolver_v1_conserva_resultado_historico_sin_metadata(tmp_path):
    package = _package(tmp_path)
    result = CobraHubResolver(cache_dir=tmp_path / "cache").resolve(
        "dep", "1.2.3", source=str(package)
    )
    assert result.metadata == {}
    assert result.dependencies == {}


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


def test_hub_resolver_reutiliza_cache_con_repo_configurado_sin_descargar(tmp_path):
    package = _package(tmp_path, name="dep-cache", version="1.2.3")
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / "dep-cache-1.2.3.co"
    cached.write_bytes(package.read_bytes())
    expected_hash = CobraHubResolver._sha256_file(cached)
    repo = FakeCobraHubRepository({})

    result = CobraHubResolver(repository=repo, cache_dir=cache).resolve(
        "dep-cache", "1.2.3", expected_sha256=f"sha256:{expected_hash}"
    )

    assert repo.downloads == []
    assert result.name == "dep-cache"
    assert result.version == "1.2.3"
    assert result.sha256 == expected_hash
    assert result.path == cached
    assert result.source == "installer-cache"


def test_adaptador_historico_traduce_error_hub_a_error_installer(tmp_path):
    resolver = CobraHubResolver(cache_dir=tmp_path / "cache")

    with pytest.raises(CobraInstallerError, match="no encontrada") as exc_info:
        resolver.resolve("inexistente", "1.0.0")

    assert exc_info.value.__cause__.__class__.__name__ == "PackageNotFoundError"
