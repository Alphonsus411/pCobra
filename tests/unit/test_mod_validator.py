import yaml
import pytest

from cobra.semantico.mod_validator import validar_mod


def _write_yaml(path, data):
    path.write_text(yaml.safe_dump(data))


def test_validador_archivo_faltante(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(tmp_path / "m.py")}}
    _write_yaml(tmp_path / "cobra.mod", data)
    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    with pytest.raises(ValueError):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_campos_faltantes(tmp_path):
    """Debe fallar si falta un backend requerido por la política."""
    mod = tmp_path / "x.co"
    data = {str(mod): {"version": "0.1.0"}}
    _write_yaml(tmp_path / "cobra.mod", data)
    with pytest.raises(ValueError):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_version_incorrecta(tmp_path):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "bad", "python": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)
    with pytest.raises(
        ValueError,
        match="^Archivo cobra.mod inválido: ",
    ):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_duplicados(tmp_path):
    py = tmp_path / "dup.py"
    py.write_text("x = 1")
    data = {
        str(tmp_path / "a.co"): {"version": "0.1.0", "python": str(py)},
        str(tmp_path / "b.co"): {"version": "0.1.0", "python": str(py)},
    }
    _write_yaml(tmp_path / "cobra.mod", data)
    with pytest.raises(ValueError):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_javascript_canonico(tmp_path, monkeypatch):
    javascript_output = tmp_path / "m.js"
    javascript_output.write_text("console.log('ok')")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "javascript": str(javascript_output)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["javascript"]}},
    )
    validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_respeta_required_targets_desde_politica(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python"]}},
    )

    validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_reporta_targets_faltantes_con_mensaje_claro(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python", "javascript"]}},
    )

    with pytest.raises(ValueError, match="Faltan rutas para targets requeridos por política"):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_por_defecto_exige_tier1_completo(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {},
    )

    with pytest.raises(ValueError, match="rust, javascript, wasm"):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_permite_targets_tier2_opcionales_en_mapeo(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    rs = tmp_path / "m.rs"
    rs.write_text("fn main() {}")
    javascript_output = tmp_path / "m.js"
    javascript_output.write_text("let x = 1;")
    wasm = tmp_path / "m.wasm"
    wasm.write_text("00")
    go = tmp_path / "m.go"
    go.write_text("package main")

    mod = tmp_path / "m.co"
    data = {
        str(mod): {
            "version": "0.1.0",
            "python": str(py),
            "rust": str(rs),
            "javascript": str(javascript_output),
            "wasm": str(wasm),
            "go": str(go),
        },
    }
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {},
    )

    validar_mod(str(tmp_path / "cobra.mod"))



def test_validador_rechaza_backend_fuera_de_los_8_oficiales(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py), "fantasy": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python"]}},
    )

    with pytest.raises(ValueError, match="Backends no canónicos"):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_v1_no_evalua_required_targets_v2_si_no_hay_modulos_v2(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    wasm = tmp_path / "m.wasm"
    wasm.write_text("00")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py), "wasm": str(wasm)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA_V1", None)
    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA_V2", None)
    monkeypatch.setattr("cobra.semantico.mod_validator.OFFICIAL_TARGETS", ("python", "javascript", "rust", "wasm"))
    monkeypatch.setattr("cobra.semantico.mod_validator.PUBLIC_BACKENDS", ("python", "javascript", "rust"))
    monkeypatch.setattr("cobra.semantico.mod_validator.DEFAULT_REQUIRED_TARGETS", ("python", "javascript", "rust", "wasm"))
    monkeypatch.setattr("cobra.semantico.mod_validator.DEFAULT_REQUIRED_TARGETS_V2", ("python", "javascript", "rust"))
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python", "wasm"]}},
    )

    validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_v2_por_version_restringe_backends_publicos(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    wasm = tmp_path / "m.wasm"
    wasm.write_text("00")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "2.0.0", "python": str(py), "wasm": str(wasm)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python"]}},
    )

    with pytest.raises(ValueError, match="Backends no canónicos"):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_v2_por_metadata_restringe_backends_publicos(tmp_path, monkeypatch):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    wasm = tmp_path / "m.wasm"
    wasm.write_text("00")
    mod = tmp_path / "m.co"
    data = {
        "metadata": {"schema_version": 2},
        str(mod): {"version": "0.1.0", "python": str(py), "wasm": str(wasm)},
    }
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python"]}},
    )

    with pytest.raises(ValueError, match="Backends no canónicos"):
        validar_mod(str(tmp_path / "cobra.mod"))


def test_validador_v1_emite_warning_migracion(tmp_path, monkeypatch, caplog):
    py = tmp_path / "m.py"
    py.write_text("x = 1")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "python": str(py)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["python"]}},
    )

    validar_mod(str(tmp_path / "cobra.mod"))
    assert "esquema v1 está deprecado" in caplog.text
