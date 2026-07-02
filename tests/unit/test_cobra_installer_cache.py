import hashlib

from pcobra.cobra_installer.cache import CobraInstallerCache, installer_cache_dir


def _write(path, content=b"artifact"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def test_installer_cache_dir_usa_subdirectorio_de_cobrahub(tmp_path):
    hub_cache = tmp_path / "hub-cache"

    assert installer_cache_dir(hub_cache_dir=hub_cache) == hub_cache / "cobra-installer"


def test_get_prefiere_cache_cobrahub_cuando_no_hay_configuracion_explicita(tmp_path):
    hub_cache = tmp_path / "hub"
    installer_cache = hub_cache / "cobra-installer"
    hub_hash = _write(hub_cache / "dep-1.2.3.co", b"hub")
    _write(installer_cache / "dep-1.2.3.co", b"installer")

    cache = CobraInstallerCache(hub_cache_dir=hub_cache)
    entry = cache.get("dep", "1.2.3", expected_sha256=hub_hash)

    assert entry is not None
    assert entry.path == hub_cache / "dep-1.2.3.co"
    assert entry.source == "cobrahub-cache"


def test_put_escribe_en_cache_propia_y_clear_no_borra_cobrahub(tmp_path):
    hub_cache = tmp_path / "hub"
    source_hash = _write(tmp_path / "source.co", b"installer")
    _write(hub_cache / "dep-1.2.3.co", b"hub")
    cache = CobraInstallerCache(hub_cache_dir=hub_cache)

    entry = cache.put("dep", "1.2.3", tmp_path / "source.co", expected_sha256=source_hash)
    deleted = cache.clear("dep", "1.2.3")

    assert entry.path == hub_cache / "cobra-installer" / "dep-1.2.3.co"
    assert deleted == 1
    assert (hub_cache / "dep-1.2.3.co").exists()
    assert not entry.path.exists()


def test_hash_invalida_artefacto_de_cache_propia(tmp_path):
    hub_cache = tmp_path / "hub"
    cache = CobraInstallerCache(hub_cache_dir=hub_cache)
    artifact = cache.cache_dir / "dep-1.2.3.co"
    _write(artifact, b"old")

    entry = cache.get("dep", "1.2.3", expected_sha256="0" * 64)

    assert entry is None
    assert not artifact.exists()


def test_variable_entorno_dirige_cache_instalador(monkeypatch, tmp_path):
    configured = tmp_path / "configured-cache"
    hub_cache = tmp_path / "hub"
    hub_hash = _write(hub_cache / "dep-1.2.3.co", b"hub")
    configured_hash = _write(configured / "dep-1.2.3.co", b"configured")
    monkeypatch.setenv("COBRA_INSTALLER_CACHE_DIR", str(configured))

    cache = CobraInstallerCache(hub_cache_dir=hub_cache)
    entry = cache.get("dep", "1.2.3", expected_sha256=configured_hash)

    assert entry is not None
    assert entry.path == configured / "dep-1.2.3.co"
    assert cache.get("dep", "1.2.3", expected_sha256=hub_hash) is None


def test_get_reutiliza_paquete_cacheado_si_version_y_hash_coinciden(tmp_path):
    hub_cache = tmp_path / "hub"
    cache = CobraInstallerCache(hub_cache_dir=hub_cache)
    artifact_hash = _write(cache.cache_dir / "dep-1.2.3.co", b"cached-package")

    entry = cache.get("dep", "1.2.3", expected_sha256=f"sha256:{artifact_hash}")

    assert entry is not None
    assert entry.name == "dep"
    assert entry.version == "1.2.3"
    assert entry.sha256 == artifact_hash
    assert entry.path == cache.cache_dir / "dep-1.2.3.co"
    assert entry.source == "installer-cache"
    assert cache.get("dep", "1.2.4", expected_sha256=artifact_hash) is None
