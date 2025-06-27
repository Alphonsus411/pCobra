import json
import pytest
from src.cli.cli import main
from src.cobra.transpilers import module_map


@pytest.mark.timeout(20)
def test_benchmarks2_generates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    salida = tmp_path / "res.json"
    main(["benchmarks2", "--output", str(salida)])
    data = json.loads(salida.read_text())
    modos = {d["modo"] for d in data}
    assert {"cobra", "python", "js", "sandbox"}.issubset(modos)
    for d in data:
        assert isinstance(d["time"], float)
        assert isinstance(d["memory_kb"], int)
