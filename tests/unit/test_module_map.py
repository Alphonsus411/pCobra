from cobra.transpilers import module_map


def test_module_map_resuelve_target_tier2_en_cobra_toml(tmp_path, monkeypatch):
    mod = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "go = 'biblioteca.go'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(mod, "go") == "biblioteca.go"


def test_module_map_ignora_cobra_mod_para_resolucion(tmp_path, monkeypatch):
    mod = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text("[modulos]\n", encoding="utf-8")
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "go = 'biblioteca.go'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    monkeypatch.setenv("COBRA_MODULE_MAP", str(mod_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map.MODULE_MAP_PATH = str(mod_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(mod, "go") == mod
