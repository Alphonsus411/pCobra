import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from pcobra.cobra.hub.models import (
    DISTRIBUTION_TYPES,
    PackageManifestV2,
    manifest_v2_from_dict,
)
from pcobra.cobra.packaging import (
    extraer_paquete,
    inspeccionar_paquete,
    manifest_from_dict,
    validar_paquete,
)


def _manifest() -> dict:
    digest = hashlib.sha256(b"wheel").hexdigest()
    return {
        "format": "cobra-package-v2",
        "name": "demo.extension",
        "version": "1.2.3-beta.1",
        "package_type": "extension",
        "requires_cobra": ">=10.1,<11",
        "exports": ["cobra.demo", "cobra.demo.api"],
        "capabilities": ["transpiler.python"],
        "platforms": ["linux", "windows"],
        "architectures": ["x86_64", "arm64"],
        "dependencies": {"cobra.std": "2.0.0"},
        "distributions": [
            {
                "type": "python-wheel",
                "path": "dist/demo.whl",
                "platforms": ["any"],
                "architectures": ["any"],
            }
        ],
        "extensions": [
            {
                "namespace": "cobra.transpilers",
                "provider": "demo-provider",
                "capabilities": ["transpiler.python"],
                "entrypoint": "demo.plugin:Provider.create",
            }
        ],
        "files": ["dist/demo.whl"],
        "checksums": {"dist/demo.whl": digest},
    }


def test_manifest_v2_modela_todos_los_campos_y_distribuciones_permitidas():
    data = _manifest()
    data["distributions"] = [
        {"type": kind, "path": "dist/demo.whl"} for kind in DISTRIBUTION_TYPES
    ]

    manifest = manifest_v2_from_dict(data)

    assert isinstance(manifest, PackageManifestV2)
    assert {item.type for item in manifest.distributions} == DISTRIBUTION_TYPES
    assert manifest.extensions[0].entrypoint == "demo.plugin:Provider.create"
    assert manifest.as_dict() == data | {
        "distributions": [
            {
                "type": kind,
                "path": "dist/demo.whl",
                "platforms": ["any"],
                "architectures": ["any"],
            }
            for kind in DISTRIBUTION_TYPES
        ]
    }


@pytest.mark.parametrize(
    "constraint",
    ["10", "10.1", "10.1.0", ">=10.1,<11", ">=10.1.0,!=10.2.0,<11.0.0"],
)
def test_manifest_v2_acepta_restricciones_cobra_estaticas(constraint):
    data = _manifest()
    data["requires_cobra"] = constraint

    assert manifest_v2_from_dict(data).requires_cobra == constraint


@pytest.mark.parametrize(
    "constraint",
    ["", "v10.1", ">=10.1,", ">=10.1, <11", ">=10.*", "__import__('os')"],
)
def test_manifest_v2_rechaza_restricciones_cobra_invalidas(constraint):
    data = _manifest()
    data["requires_cobra"] = constraint

    with pytest.raises(ValueError, match="restricción de versiones"):
        manifest_v2_from_dict(data)


@pytest.mark.parametrize("architecture", ["arm64", "aarch64"])
def test_manifest_v2_normaliza_arm64_como_representacion_canonica(architecture):
    data = _manifest()
    data["architectures"] = [architecture]
    data["distributions"][0]["architectures"] = [architecture]

    manifest = manifest_v2_from_dict(data)

    assert manifest.architectures == ("arm64",)
    assert manifest.distributions[0].architectures == ("arm64",)
    assert manifest.as_dict()["architectures"] == ["arm64"]
    assert manifest.as_dict()["distributions"][0]["architectures"] == ["arm64"]


def test_manifest_v2_exports_son_namespaces_y_no_rutas_de_files():
    data = _manifest()
    data["exports"] = ["cobra.demo.api", "cobra_demo.utilidades"]

    manifest = manifest_v2_from_dict(data)

    assert manifest.exports == ("cobra.demo.api", "cobra_demo.utilidades")


@pytest.mark.parametrize(
    "export", ["dist/demo.whl", ".cobra", "cobra..demo", "cobra-demo"]
)
def test_manifest_v2_rechaza_exports_que_no_son_namespaces(export):
    data = _manifest()
    data["exports"] = [export]

    with pytest.raises(ValueError, match="namespace"):
        manifest_v2_from_dict(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("files", ["../demo.whl"]),
        ("files", ["/dist/demo.whl"]),
        ("checksums", {"../dist/demo.whl": "0" * 64}),
    ],
)
def test_manifest_v2_rechaza_rutas_inseguras_de_archivos(field, value):
    data = _manifest()
    data[field] = value

    with pytest.raises(ValueError, match="ruta insegura"):
        manifest_v2_from_dict(data)


def test_manifest_v2_rechaza_ruta_insegura_de_distribucion():
    data = _manifest()
    data["distributions"][0]["path"] = "../demo.whl"

    with pytest.raises(ValueError, match="ruta insegura"):
        manifest_v2_from_dict(data)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("version", "v1.2.3", "SemVer"),
        ("platforms", ["plan9"], "no soportados"),
        ("architectures", ["mips"], "no soportados"),
        ("checksums", {"dist/demo.whl": "not-a-hash"}, "SHA-256"),
        ("extensions", [{}], "namespace"),
    ],
)
def test_manifest_v2_rechaza_valores_invalidos(field, value, match):
    data = _manifest()
    data[field] = value
    with pytest.raises(ValueError, match=match):
        manifest_v2_from_dict(data)


@pytest.mark.parametrize(
    "entrypoint",
    [
        "demo.plugin",
        "demo.plugin:",
        "demo-plugin:factory",
        "demo:factory()",
        " demo:factory",
    ],
)
def test_manifest_v2_rechaza_entrypoints_no_estaticos(entrypoint):
    data = _manifest()
    data["extensions"][0]["entrypoint"] = entrypoint
    with pytest.raises(ValueError, match="entrypoint"):
        manifest_v2_from_dict(data)


def test_fachadas_packaging_validan_y_extraen_v2_sin_importar_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    imported: list[str] = []
    original_import = __import__
    monkeypatch.setattr(
        "builtins.__import__",
        lambda name, *args, **kwargs: (
            imported.append(name) or original_import(name, *args, **kwargs)
        ),
    )
    package = tmp_path / "demo.co"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("cobra.pkg.json", json.dumps(_manifest()))
        archive.writestr("dist/demo.whl", b"wheel")

    assert isinstance(manifest_from_dict(_manifest()), PackageManifestV2)
    assert inspeccionar_paquete(package).manifest["format"] == "cobra-package-v2"
    assert validar_paquete(package).manifest["name"] == "demo.extension"
    destination = extraer_paquete(package, tmp_path / "out")

    assert (destination / "dist/demo.whl").read_bytes() == b"wheel"
    assert "demo.plugin" not in imported
