import subprocess
import shutil
import pytest

from src.core.ast_nodes import NodoAsignacion, NodoValor
from src.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from src.cobra.transpilers.transpiler.to_go import TranspiladorGo


def test_transpile_and_compile_rust_go(tmp_path):
    ast = [NodoAsignacion("x", NodoValor(1))]

    rust_code = TranspiladorRust().generate_code(ast)
    go_code = TranspiladorGo().generate_code(ast)

    rustc = shutil.which("rustc")
    go_cmd = shutil.which("go")
    if not rustc or not go_cmd:
        pytest.skip("rustc o go no disponibles")

    rust_src = tmp_path / "prog.rs"
    rust_src.write_text(
        "fn main() {\n    "
        + rust_code.replace("\n", "\n    ")
        + "\n    let _ = x;\n}\n"
    )
    subprocess.run([rustc, str(rust_src), "-o", str(tmp_path / "prog_rust")], check=True)

    go_src = tmp_path / "prog.go"
    go_src.write_text(
        "package main\n\nfunc main() {\n    "
        + go_code.replace("\n", "\n    ")
        + "\n    _ = x\n}\n"
    )
    subprocess.run([go_cmd, "build", "-o", str(tmp_path / "prog_go"), str(go_src)], check=True)
