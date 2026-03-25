from pathlib import Path

TRANSPILER_FILES = (
    "src/pcobra/cobra/transpilers/transpiler/to_python.py",
    "src/pcobra/cobra/transpilers/transpiler/to_js.py",
    "src/pcobra/cobra/transpilers/transpiler/to_rust.py",
    "src/pcobra/cobra/transpilers/transpiler/to_go.py",
    "src/pcobra/cobra/transpilers/transpiler/to_cpp.py",
    "src/pcobra/cobra/transpilers/transpiler/to_java.py",
    "src/pcobra/cobra/transpilers/transpiler/to_wasm.py",
    "src/pcobra/cobra/transpilers/transpiler/to_asm.py",
)


def test_transpilers_oficiales_consumen_contrato_runtime_centralizado():
    for rel in TRANSPILER_FILES:
        content = Path(rel).read_text(encoding="utf-8")
        assert "get_standard_imports" in content
        assert "get_runtime_hooks" in content
