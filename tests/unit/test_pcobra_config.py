import importlib
import sys


def _reload_module():
    if 'core.pcobra_config' in sys.modules:
        importlib.reload(sys.modules['core.pcobra_config'])
    return sys.modules.get('core.pcobra_config')


def test_cargar_configuracion_python_js(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    py_out = tmp_path / "m.py"
    js_out = tmp_path / "m.js"

    config = f"\n['{mod}']\npython = '{py_out}'\njs = '{js_out}'\n"
    cfg_file = tmp_path / "pcobra.toml"
    cfg_file.write_text(config)

    monkeypatch.setenv('PCOBRA_CONFIG', str(cfg_file))
    _reload_module()
    from core.pcobra_config import cargar_configuracion

    data = cargar_configuracion()
    ruta = str(mod)
    assert data[ruta]['python'] == str(py_out)
    assert data[ruta]['js'] == str(js_out)


def test_cargar_configuracion_cache(tmp_path, monkeypatch):
    cfg_file = tmp_path / 'pcobra.toml'
    cfg_file.write_text("")
    monkeypatch.setenv('PCOBRA_CONFIG', str(cfg_file))
    _reload_module()
    from core.pcobra_config import cargar_configuracion, _cache

    cargar_configuracion()
    before = dict(_cache)

    cfg_file.write_text("['x']\npython='a.py'\n")
    data = cargar_configuracion()

    assert _cache == before
    assert data == before[str(cfg_file)]
