import json
from pathlib import Path

import pytest

from pcobra.cobra.hub.errors import PackageResolutionError
from pcobra.cobra.hub.lockfile import read_lockfile, write_lockfile
from pcobra.cobra.hub.models import CobraHubResolution, LockedDependency

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
                "packages": [
                    {
                        "name": "demo",
                        "version": "1.0.0",
                        "source": "cobrahub-cache",
                        "sha256": HASH,
                        "package_type": "library",
                        "artifact_type": "cobra-package",
                        "artifact": "demo.co",
                        "exports": ["demo.api"],
                        "capabilities": ["net"],
                        "extensions": [
                            {
                                "namespace": "demo.plugins",
                                "provider": "plug",
                                "capabilities": ["net"],
                                "entrypoint": "demo.plugin:Plugin",
                            }
                        ],
                        "platforms": ["linux"],
                        "architectures": ["x86_64"],
                        "dependencies": {"base": "2.0.0"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    entry = read_lockfile(path)["demo"]
    assert entry.source == "cobrahub-cache"
    assert entry.metadata == {
        "package_type": "library",
        "artifact_type": "cobra-package",
        "artifact": "demo.co",
        "exports": ["demo.api"],
        "capabilities": ["net"],
        "extensions": [
            {
                "namespace": "demo.plugins",
                "provider": "plug",
                "capabilities": ["net"],
                "entrypoint": "demo.plugin:Plugin",
            }
        ],
        "platforms": ["linux"],
        "architectures": ["x86_64"],
        "dependencies": {"base": "2.0.0"},
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


def test_lockfile_v2_serializa_solo_metadata_normalizada_y_permite_lectura_offline(
    tmp_path,
):
    path = tmp_path / "cobra.lock"
    entry = LockedDependency(
        "demo",
        "1.0.0",
        HASH,
        "cobrahub",
        metadata={
            "package_type": "library",
            "requires_cobra": ">=10,<11",
            "artifact_type": "cobra-package",
            "artifact": "dist/demo.co",
            "exports": ["demo.api"],
            "capabilities": ["net"],
            "extensions": [],
            "platforms": ["linux"],
            "architectures": ["x86_64"],
            "distributions": [
                {
                    "type": "cobra-package",
                    "path": "dist/demo.co",
                    "platforms": ["linux"],
                    "architectures": ["x86_64"],
                }
            ],
            "dependencies": {"base": "2.0.0"},
            "campo_interno": "no serializar",
        },
    )
    write_lockfile(path, {"demo": entry})

    payload = json.loads(path.read_text())
    assert "campo_interno" not in payload["packages"][0]
    offline = read_lockfile(path)["demo"]
    assert offline.metadata["artifact"] == "dist/demo.co"
    assert offline.metadata["requires_cobra"] == ">=10,<11"
    assert offline.metadata["distributions"][0]["type"] == "cobra-package"


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"version": 3, "packages": []}, "no soportada"),
        ({"version": 2, "other": []}, "packages"),
        (
            {
                "version": 2,
                "packages": [{"name": "x", "version": "1.0.0", "sha256": "bad"}],
            },
            "sha256",
        ),
        ({"version": 2, "packages": [{"name": "x", "version": 1}]}, "version"),
        ({"version": 2, "packages": [{"version": "1.0.0"}]}, "name"),
    ],
)
def test_rechaza_esquema_futuro_estructura_y_campos_invalidos(
    tmp_path, payload, message
):
    path = tmp_path / "cobra.lock"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PackageResolutionError, match=message):
        read_lockfile(path)


def test_rechaza_duplicados_despues_de_normalizar(tmp_path):
    path = tmp_path / "cobra.lock"
    path.write_text(
        json.dumps(
            [
                {"name": "Demo_Pkg", "version": "1.0.0"},
                {"name": "demo_pkg", "version": "1.0.0"},
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(PackageResolutionError, match="duplicado"):
        read_lockfile(path)


def _v2_entry(**changes):
    entry = {
        "name": "demo",
        "version": "1.0.0",
        "artifact_type": "cobra-package",
        "artifact": "dist/demo.co",
        "exports": ["demo.api"],
        "capabilities": ["net"],
        "extensions": [],
        "platforms": ["linux"],
        "architectures": ["x86_64"],
    }
    entry.update(changes)
    return {"version": 2, "packages": [entry]}


@pytest.mark.parametrize(
    "artifact",
    ["../demo.co", "/tmp/demo.co", "C:\\temp\\demo.co", "dist\\demo.co", ""],
)
def test_v2_rechaza_rutas_de_artefacto_inseguras(tmp_path, artifact):
    path = tmp_path / "cobra.lock"
    path.write_text(json.dumps(_v2_entry(artifact=artifact)), encoding="utf-8")

    with pytest.raises(PackageResolutionError, match="artifact|ruta insegura"):
        read_lockfile(path)


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"artifact_type": "desconocido"}, "artifact_type"),
        ({"platforms": ["plan9"]}, "platforms"),
        ({"architectures": ["mips"]}, "architectures"),
        ({"exports": ["demo", "demo"]}, "duplicados"),
        ({"capabilities": ["net", "net"]}, "duplicados"),
        ({"platforms": ["linux", "linux"]}, "duplicados"),
        ({"architectures": ["arm64", "arm64"]}, "duplicados"),
        ({"campo_nuevo": True}, "desconocidas"),
        (
            {
                "extensions": [
                    {
                        "namespace": "demo.plugins",
                        "provider": "plug",
                        "capabilities": ["net"],
                        "entrypoint": "no-es-un-entrypoint",
                    }
                ]
            },
            "entrypoint",
        ),
    ],
)
def test_v2_rechaza_campos_fuera_de_los_contratos(tmp_path, changes, message):
    path = tmp_path / "cobra.lock"
    path.write_text(json.dumps(_v2_entry(**changes)), encoding="utf-8")

    with pytest.raises(PackageResolutionError, match=message):
        read_lockfile(path)


def test_v1_mantiene_tolerancia_a_claves_historicas(tmp_path):
    path = tmp_path / "cobra.lock"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "packages": [
                    {"name": "demo", "version": "1.0.0", "campo_antiguo": True}
                ],
            }
        ),
        encoding="utf-8",
    )

    assert read_lockfile(path)["demo"].version == "1.0.0"


def test_escritura_no_depende_del_directorio_de_trabajo(tmp_path, monkeypatch):
    artifact = tmp_path / "cache" / "demo.co"
    artifact.parent.mkdir()
    artifact.touch()
    resolution = CobraHubResolution("demo", "1.0.0", artifact, HASH, "cobrahub-cache")
    first = tmp_path / "first.lock"
    second = tmp_path / "second.lock"

    write_lockfile(first, {"demo": resolution})
    other_cwd = tmp_path / "other"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)
    write_lockfile(second, {"demo": resolution})

    assert first.read_bytes() == second.read_bytes()
    assert json.loads(first.read_text())["packages"][0]["artifact"] == "demo.co"
    assert str(Path(artifact).parent) not in first.read_text()
