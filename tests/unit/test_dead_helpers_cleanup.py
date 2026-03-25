from pathlib import Path


def test_asm_nodes_only_keeps_runtime_adapter_in_official_pipeline():
    asm_nodes = Path("src/pcobra/cobra/transpilers/transpiler/asm_nodes")
    py_files = sorted(path.name for path in asm_nodes.glob("*.py"))
    assert py_files == ["__init__.py", "runtime_holobit.py"]
