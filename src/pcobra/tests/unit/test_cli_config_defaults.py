import importlib
import logging
import sys
import types


def stub_cli_dependencies() -> None:
    """Crea módulos y clases mínimos para evitar dependencias pesadas al importar la CLI."""
    def create_command(name: str):
        return type(name, (), {"name": name, "register_subparser": lambda self, sp: None})

    command_modules = {
        "cobra.cli.commands.base": "BaseCommand",
        "cobra.cli.commands.bench_cmd": "BenchCommand",
        "cobra.cli.commands.bench_transpilers_cmd": "BenchTranspilersCommand",
        "cobra.cli.commands.benchmarks_cmd": "BenchmarksCommand",
        "cobra.cli.commands.benchthreads_cmd": "BenchThreadsCommand",
        "cobra.cli.commands.cache_cmd": "CacheCommand",
        "cobra.cli.commands.compile_cmd": "CompileCommand",
        "cobra.cli.commands.container_cmd": "ContainerCommand",
        "cobra.cli.commands.crear_cmd": "CrearCommand",
        "cobra.cli.commands.dependencias_cmd": "DependenciasCommand",
        "cobra.cli.commands.docs_cmd": "DocsCommand",
        "cobra.cli.commands.empaquetar_cmd": "EmpaquetarCommand",
        "cobra.cli.commands.execute_cmd": "ExecuteCommand",
        "cobra.cli.commands.flet_cmd": "FletCommand",
        "cobra.cli.commands.init_cmd": "InitCommand",
        "cobra.cli.commands.jupyter_cmd": "JupyterCommand",
        "cobra.cli.commands.modules_cmd": "ModulesCommand",
        "cobra.cli.commands.package_cmd": "PaqueteCommand",
        "cobra.cli.commands.plugins_cmd": "PluginsCommand",
        "cobra.cli.commands.profile_cmd": "ProfileCommand",
        "cobra.cli.commands.qualia_cmd": "QualiaCommand",
        "cobra.cli.commands.transpilar_inverso_cmd": "TranspilarInversoCommand",
        "cobra.cli.commands.verify_cmd": "VerifyCommand",
    }

    for module_name, class_name in command_modules.items():
        module = types.ModuleType(module_name)
        setattr(module, class_name, create_command(class_name))
        sys.modules[module_name] = module

    sys.modules["cobra.cli.commands.compile_cmd"].LANG_CHOICES = []
    sys.modules["cobra.cli.commands.transpilar_inverso_cmd"].ORIGIN_CHOICES = []

    core_mod = types.ModuleType("core.interpreter")
    core_mod.InterpretadorCobra = type("InterpretadorCobra", (), {})
    sys.modules["core.interpreter"] = core_mod

    i18n_mod = types.ModuleType("cobra.cli.i18n")
    i18n_mod._ = lambda x: x
    i18n_mod.format_traceback = lambda x: x
    i18n_mod.setup_gettext = lambda *args, **kwargs: None
    sys.modules["cobra.cli.i18n"] = i18n_mod

    plugin_mod = types.ModuleType("cobra.cli.plugin")
    plugin_mod.descubrir_plugins = lambda: []
    sys.modules["cobra.cli.plugin"] = plugin_mod


def test_cli_starts_with_defaults_when_config_absent(tmp_path, monkeypatch):
    """La CLI debe iniciar con valores por defecto si no existe archivo de configuración."""
    # Aseguramos que no existan variables de entorno que puedan modificar los valores
    monkeypatch.delenv("COBRA_LANG", raising=False)
    monkeypatch.delenv("COBRA_DEFAULT_COMMAND", raising=False)
    monkeypatch.delenv("COBRA_LOG_FORMAT", raising=False)
    monkeypatch.delenv("COBRA_PROGRAM_NAME", raising=False)
    monkeypatch.chdir(tmp_path)

    stub_cli_dependencies()
    sys.modules.pop("cobra.cli.cli", None)
    cli_mod = importlib.import_module("cobra.cli.cli")

    assert cli_mod.AppConfig.DEFAULT_LANGUAGE == "es"
    assert cli_mod.AppConfig.DEFAULT_COMMAND == "interactive"


def test_cli_uses_defaults_when_config_load_fails(monkeypatch, caplog):
    """La CLI debe registrar un error y continuar con valores por defecto si la carga falla."""
    import cobra.cli.utils.config as config_mod

    def bad_load():
        raise RuntimeError("boom")

    monkeypatch.setattr(config_mod, "load_config", bad_load)
    stub_cli_dependencies()
    sys.modules.pop("cobra.cli.cli", None)

    with caplog.at_level(logging.ERROR):
        cli_mod = importlib.import_module("cobra.cli.cli")

    assert "boom" in caplog.text
    assert cli_mod.AppConfig.config_data == {}
    assert cli_mod.AppConfig.DEFAULT_LANGUAGE == "es"
    assert cli_mod.AppConfig.DEFAULT_COMMAND == "interactive"
