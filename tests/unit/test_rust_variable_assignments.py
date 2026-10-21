import shutil
import subprocess
from pathlib import Path

import pytest

from pcobra.cobra.build import backend_pipeline


def test_rust_pipeline_reasigna_variable_declarada_en_vez_de_sombrearla(
    tmp_path: Path,
):
    source = tmp_path / "reasignacion.cobra"
    source.write_text("var x = 0\nx = x + 1\nimprimir(x)\n", encoding="utf-8")

    result = backend_pipeline.build(
        str(source),
        {"preferred_backend": "rust", "source_file": str(source)},
    )

    assert result["backend"] == "rust"
    assert "let mut x = 0;" in result["code"]
    assert "x = x + 1;" in result["code"]
    assert "let x = x + 1;" not in result["code"]


def test_rust_pipeline_reasignacion_compila_con_rustc(tmp_path: Path):
    rustc = shutil.which("rustc")
    if rustc is None:
        pytest.skip("rustc no está disponible")

    source = tmp_path / "reasignacion.cobra"
    source.write_text("var x = 0\nx = x + 1\nimprimir(x)\n", encoding="utf-8")
    result = backend_pipeline.build(
        str(source),
        {"preferred_backend": "rust", "source_file": str(source)},
    )
    body = "\n".join(
        line
        for line in str(result["code"]).splitlines()
        if line.strip()
        not in {"use crate::corelibs::*;", "use crate::standard_library::*;"}
    )
    program = (
        "fn main() {\n"
        + "\n".join(f"    {line}" for line in body.splitlines())
        + "\n}\n"
    )
    rust_source = tmp_path / "reasignacion.rs"
    rust_source.write_text(program, encoding="utf-8")

    subprocess.run(
        [rustc, "--edition=2021", str(rust_source), "-o", str(tmp_path / "program")],
        check=True,
        capture_output=True,
        text=True,
    )
