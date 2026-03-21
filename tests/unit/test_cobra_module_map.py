from cobra.transpilers import module_map


def test_cobra_toml_mapping_requires_tabla_modulos(tmp_path, monkeypatch):
    mod = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "python = 'biblioteca.py'\n"
        "javascript = 'biblioteca.js'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(mod, "python") == "biblioteca.py"
    assert module_map.get_mapped_path(mod, "javascript") == "biblioteca.js"


def test_cobra_toml_mapping_no_usa_estructura_antigua_en_raiz(tmp_path, monkeypatch):
    mod = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "['biblioteca.co']\n"
        "python = 'biblioteca.py'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(mod, "python") == mod
