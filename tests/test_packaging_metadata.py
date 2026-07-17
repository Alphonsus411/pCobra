from __future__ import annotations

import subprocess
import sys
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path

from packaging.requirements import Requirement


REPO_ROOT = Path(__file__).resolve().parents[1]


def _is_optional(requirement: Requirement) -> bool:
    """Indica si un Requires-Dist pertenece a un extra del proyecto."""

    return requirement.marker is not None and "extra" in str(requirement.marker)


def test_wheel_preserva_dependencias_obligatorias_de_pyproject(tmp_path: Path) -> None:
    """Evita que el backend añada, elimine o modifique dependencias al publicar."""

    with (REPO_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        project = tomllib.load(pyproject_file)["project"]
    declared = {Requirement(value) for value in project["dependencies"]}

    dist_dir = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    wheels = list(dist_dir.glob("*.whl"))
    assert len(wheels) == 1, f"Se esperaba exactamente un wheel, encontrados: {wheels}"
    with zipfile.ZipFile(wheels[0]) as wheel:
        metadata_paths = [
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        ]
        assert len(metadata_paths) == 1, (
            "El wheel debe contener un único *.dist-info/METADATA: "
            f"{metadata_paths}"
        )
        metadata = BytesParser().parsebytes(wheel.read(metadata_paths[0]))

    published = {
        requirement
        for value in metadata.get_all("Requires-Dist", [])
        if not _is_optional(requirement := Requirement(value))
    }
    assert published == declared, (
        "Las dependencias obligatorias del wheel difieren de [project].dependencies. "
        f"Añadidas o modificadas: {sorted(map(str, published - declared))}; "
        f"eliminadas o modificadas: {sorted(map(str, declared - published))}"
    )
