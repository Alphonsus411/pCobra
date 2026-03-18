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
    """Debe fallar si falta un backend requerido (python o javascript/js)."""
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


def test_validador_js_legacy_normaliza_y_advierte(tmp_path, caplog, monkeypatch):
    js = tmp_path / "m.js"
    js.write_text("console.log('ok')")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "js": str(js)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", None)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["javascript"]}},
    )

    with caplog.at_level("WARNING"):
        validar_mod(str(tmp_path / "cobra.mod"))

    assert "está deprecada; usa 'javascript'" in caplog.text


def test_validador_javascript_canonico(tmp_path, monkeypatch):
    js = tmp_path / "m.js"
    js.write_text("console.log('ok')")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "javascript": str(js)}}
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


def test_validador_omite_requisitos_estaticos_de_schema_para_usar_politica(monkeypatch):
    schema = {
        "patternProperties": {
            ".*\\.co$": {
                "type": "object",
                "anyOf": [
                    {"required": ["python"]},
                    {"required": ["javascript"]},
                ],
            },
        },
    }

    captured = {}

    def fake_validate(*, instance, schema):
        captured["instance"] = instance
        captured["schema"] = schema

    monkeypatch.setattr("cobra.semantico.mod_validator.SCHEMA", schema)
    monkeypatch.setattr("cobra.semantico.mod_validator.validate", fake_validate)
    monkeypatch.setattr("cobra.semantico.mod_validator.ValidationError", Exception)
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.cargar_mod",
        lambda _path=None: {"mod.co": {"version": "0.1.0", "rust": "mod.rs"}},
    )
    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["rust"]}},
    )
    monkeypatch.setattr("cobra.semantico.mod_validator.os.path.exists", lambda _path: True)

    validar_mod("cobra.mod")

    assert captured["instance"] == {"mod.co": {"version": "0.1.0", "rust": "mod.rs"}}
    module_schema = next(iter(captured["schema"]["patternProperties"].values()))
    assert "anyOf" not in module_schema


def test_validador_permite_modulo_rust_only_cuando_politica_lo_requiere(tmp_path, monkeypatch):
    rust = tmp_path / "m.rs"
    rust.write_text("fn main() {}")
    mod = tmp_path / "m.co"
    data = {str(mod): {"version": "0.1.0", "rust": str(rust)}}
    _write_yaml(tmp_path / "cobra.mod", data)

    monkeypatch.setattr(
        "cobra.semantico.mod_validator.module_map.get_toml_map",
        lambda: {"project": {"required_targets": ["rust"]}},
    )
    monkeypatch.setattr("cobra.semantico.mod_validator.validate", lambda **_kwargs: None)

    validar_mod(str(tmp_path / "cobra.mod"))
