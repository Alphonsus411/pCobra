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


def test_resuelve_dependencia_cacheada_sin_cliente_remoto_y_lock_indica_cache(tmp_path):
    package = _package(tmp_path, name="dep-cache", version="1.2.3")
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / "dep-cache-1.2.3.co"
    cached.write_bytes(package.read_bytes())
    repo = _FakeCobraHubRepository({})
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep-cache = "1.2.3"\n', encoding="utf-8"
    )
    (tmp_path / "main.cobra").write_text(
        "usar dep-cache.modulo\n", encoding="utf-8"
    )

    result = resolve_project_dependencies(
        tmp_path, resolver=CobraHubResolver(repository=repo, cache_dir=cache)
    )

    assert repo.downloads == []
    assert result.resolved["dep-cache"].path == cached
    assert result.resolved["dep-cache"].version == "1.2.3"
    assert result.resolved["dep-cache"].source == "installer-cache"
    lock = json.loads((tmp_path / "cobra.lock").read_text(encoding="utf-8"))
    assert lock["packages"] == [
        {
            "architectures": [],
            "artifact": str(cached),
            "capabilities": [],
            "dependencies": {},
            "exports": [],
            "extensions": [],
            "name": "dep-cache",
            "platforms": [],
            "version": "1.2.3",
            "sha256": result.resolved["dep-cache"].sha256,
            "source": "installer-cache",
        }
    ]


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


class MultiDependencyProjectFixture:
    def __init__(self, tmp_path):
        self.project_root = tmp_path / "project"
        self.project_root.mkdir()
        self.cache_dir = tmp_path / "cache"
        self.cache_dir.mkdir()
        self.remote_dir = tmp_path / "remote"
        self.remote_dir.mkdir()

        cached_package = _package(tmp_path, name="dep-cache", version="1.2.3")
        remote_package = _package(tmp_path, name="dep-remota", version="2.0.0")
        self.cached_path = self.cache_dir / "dep-cache-1.2.3.co"
        self.cached_path.write_bytes(cached_package.read_bytes())
        self.remote_path = self.remote_dir / "dep-remota-2.0.0.co"
        self.remote_path.write_bytes(remote_package.read_bytes())
        self.hashes = {
            "dep-cache": CobraHubResolver._sha256_file(self.cached_path),
            "dep-remota": CobraHubResolver._sha256_file(self.remote_path),
        }
        self.repository = _FakeCobraHubRepository(
            {("dep-remota", "2.0.0"): self.remote_path}
        )
        (self.project_root / "cobra.toml").write_text(
            '[dependencies]\ndep-cache = "1.2.3"\n\n'
            '[cobra.dependencies]\ndep-remota = "2.0.0"\n',
            encoding="utf-8",
        )
        (self.project_root / "main.cobra").write_text(
            "import 'dep-cache.modulo'\nimport 'dep-remota.api'\n",
            encoding="utf-8",
        )

    @property
    def resolver(self):
        return CobraHubResolver(repository=self.repository, cache_dir=self.cache_dir)


@pytest.fixture
def multi_dependency_project(tmp_path):
    return MultiDependencyProjectFixture(tmp_path)


def test_resuelve_proyecto_con_multiples_dependencias_hash_ruta_y_origen(
    multi_dependency_project,
):
    fixture = multi_dependency_project

    result = resolve_project_dependencies(
        fixture.project_root, resolver=fixture.resolver
    )

    assert result.lockfile_created is True
    assert result.used_imports == {"dep-cache", "dep-remota"}
    assert set(result.declared) == {"dep-cache", "dep-remota"}
    assert fixture.repository.downloads == [("dep-remota", "2.0.0")]
    assert {
        name: {
            "name": resolution.name,
            "version": resolution.version,
            "hash": resolution.sha256,
            "path": resolution.path,
            "source": resolution.source,
        }
        for name, resolution in result.resolved.items()
    } == {
        "dep-cache": {
            "name": "dep-cache",
            "version": "1.2.3",
            "hash": fixture.hashes["dep-cache"],
            "path": fixture.cached_path,
            "source": "installer-cache",
        },
        "dep-remota": {
            "name": "dep-remota",
            "version": "2.0.0",
            "hash": fixture.hashes["dep-remota"],
            "path": fixture.remote_path,
            "source": "cobrahub",
        },
    }

    lock = json.loads((fixture.project_root / "cobra.lock").read_text(encoding="utf-8"))
    assert lock == {
        "version": 2,
        "packages": [
            {
                "architectures": [],
                "artifact": str(fixture.cached_path),
                "capabilities": [],
                "dependencies": {},
                "exports": [],
                "extensions": [],
                "name": "dep-cache",
                "platforms": [],
                "sha256": fixture.hashes["dep-cache"],
                "source": "installer-cache",
                "version": "1.2.3",
            },
            {
                "architectures": [],
                "artifact": str(fixture.remote_path),
                "capabilities": [],
                "dependencies": {},
                "exports": [],
                "extensions": [],
                "name": "dep-remota",
                "platforms": [],
                "sha256": fixture.hashes["dep-remota"],
                "source": "cobrahub",
                "version": "2.0.0",
            },
        ],
    }


class _MissingCobraHubRepository:
    def __init__(self):
        self.downloads = []

    def download(self, name, version=None):
        self.downloads.append((name, version))
        raise FileNotFoundError(f"paquete no publicado: {name}=={version}")


def test_dependencia_declarada_inexistente_en_cobrahub_falla_controlado(tmp_path):
    repo = _MissingCobraHubRepository()
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep-fantasma = "9.9.9"\n', encoding="utf-8"
    )
    (tmp_path / "main.cobra").write_text("usar dep-fantasma.modulo\n", encoding="utf-8")

    with pytest.raises(CobraInstallerError) as exc_info:
        resolve_project_dependencies(
            tmp_path,
            resolver=CobraHubResolver(repository=repo, cache_dir=tmp_path / "cache"),
        )

    assert isinstance(exc_info.value, CobraInstallerError)
    message = str(exc_info.value)
    assert "dep-fantasma" in message
    assert "9.9.9" in message
    assert "CobraHub" in message
    assert repo.downloads == [("dep-fantasma", "9.9.9")]


def test_detecta_conflicto_entre_dependencias_transitivas_y_explica_cadenas(tmp_path):
    dep_a = _package(
        tmp_path,
        name="dep-a",
        version="1.0.0",
        dependencies={"compartida": "1.0.0"},
    )
    dep_b = _package(
        tmp_path,
        name="dep-b",
        version="1.0.0",
        dependencies={"compartida": "2.0.0"},
    )
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "dep-a-1.0.0.co").write_bytes(dep_a.read_bytes())
    (cache / "dep-b-1.0.0.co").write_bytes(dep_b.read_bytes())
    (tmp_path / "cobra.toml").write_text(
        '[dependencies]\ndep-a = "1.0.0"\ndep-b = "1.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "main.cobra").write_text(
        "usar dep-a.api\nusar dep-b.api\n", encoding="utf-8"
    )

    with pytest.raises(CobraDependencyError) as exc_info:
        resolve_project_dependencies(
            tmp_path, resolver=CobraHubResolver(cache_dir=cache)
        )

    message = str(exc_info.value)
    assert "Conflicto de versiones para compartida" in message
    assert "versiones incompatibles 1.0.0 y 2.0.0" in message
    assert (
        "Cadena existente: proyecto -> dep-a==1.0.0 -> compartida==1.0.0"
        in message
    )
    assert (
        "Cadena nueva: proyecto -> dep-b==1.0.0 -> compartida==2.0.0"
        in message
    )
    assert not (tmp_path / "cobra.lock").exists()
