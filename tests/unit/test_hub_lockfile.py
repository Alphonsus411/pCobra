import json

import pytest

from pcobra.cobra.hub.errors import PackageResolutionError
from pcobra.cobra.hub.lockfile import read_lockfile, write_lockfile
from pcobra.cobra.hub.models import LockedDependency


HASH = "a" * 64


@pytest.mark.parametrize(
    "contents",
    [
        '[{"name":"Demo_Pkg","version":"1.2.3","sha256":"' + HASH + '"}]',
        'version = 1\n[[packages]]\nname = "Demo_Pkg"\nversion = "1.2.3"\nsha256 = "'
        + HASH
        + '"\n',
        '[packages.demo_pkg]\nversion = "1.2.3"\nsha256 = "' + HASH + '"\n',
    ],
)
def test_snapshot_lectura_v1_json_toml_y_tabla(tmp_path, contents):
    path = tmp_path / "cobra.lock"
    path.write_text(contents, encoding="utf-8")

    assert read_lockfile(path) == {
        "demo_pkg": LockedDependency("demo_pkg", "1.2.3", HASH, None)
    }


def test_snapshot_v2_conserva_metadatos_y_lectura_offline(tmp_path):
    path = tmp_path / "cobra.lock"
    path.write_text(
        json.dumps(
            {
                "version": 2,
                "packages": [{
                    "name": "demo", "version": "1.0.0", "source": "cobrahub-cache",
                    "sha256": HASH, "package_type": "library", "artifact_type": "co",
                    "artifact": "demo.co", "exports": ["demo.api"],
                    "capabilities": ["net"], "extensions": [{"name": "plug"}],
                    "platforms": ["linux"], "architectures": ["x86_64"],
                    "dependencies": {"base": "2.0.0"},
                }],
            }
        ),
        encoding="utf-8",
    )

    entry = read_lockfile(path)["demo"]
    assert entry.source == "cobrahub-cache"
    assert entry.metadata == {
        "package_type": "library", "artifact_type": "co", "artifact": "demo.co",
        "exports": ["demo.api"], "capabilities": ["net"],
        "extensions": [{"name": "plug"}], "platforms": ["linux"],
        "architectures": ["x86_64"], "dependencies": {"base": "2.0.0"},
    }


def test_reserializacion_v2_es_determinista(tmp_path):
    path = tmp_path / "cobra.lock"
    entries = {
        "z": LockedDependency("z", "2.0.0", HASH, "cobrahub"),
        "a": LockedDependency("a", "1.0.0", HASH, "installer-cache"),
    }

    write_lockfile(path, entries)
    first = path.read_bytes()
    write_lockfile(path, dict(reversed(entries.items())))

    assert path.read_bytes() == first
    assert [item["name"] for item in json.loads(first)["packages"]] == ["a", "z"]


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"version": 3, "packages": []}, "no soportada"),
        ({"version": 2, "other": []}, "packages"),
        ({"version": 2, "packages": [{"name": "x", "version": "1.0.0", "sha256": "bad"}]}, "sha256"),
        ({"version": 2, "packages": [{"name": "x", "version": 1}]}, "version"),
        ({"version": 2, "packages": [{"version": "1.0.0"}]}, "name"),
    ],
)
def test_rechaza_esquema_futuro_estructura_y_campos_invalidos(tmp_path, payload, message):
    path = tmp_path / "cobra.lock"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PackageResolutionError, match=message):
        read_lockfile(path)


def test_rechaza_duplicados_despues_de_normalizar(tmp_path):
    path = tmp_path / "cobra.lock"
    path.write_text(json.dumps([
        {"name": "Demo_Pkg", "version": "1.0.0"},
        {"name": "demo_pkg", "version": "1.0.0"},
    ]), encoding="utf-8")

    with pytest.raises(PackageResolutionError, match="duplicado"):
        read_lockfile(path)
