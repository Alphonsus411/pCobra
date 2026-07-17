import ast
import tomllib
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from types import SimpleNamespace
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "src" / "pcobra" / "cli.py"


def _load_version_helpers(tmp_path: Path, env: dict[str, str], package_version):
    source = CLI_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    wanted = {
        "_resolve_pyproject_version",
        "_resolve_cli_version",
        "_resolve_cli_commit",
        "_format_cli_version",
    }
    helper_source = "\n\n".join(
        ast.get_source_segment(source, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    )
    fake_cli = tmp_path / "src" / "pcobra" / "cli.py"
    fake_cli.parent.mkdir(parents=True)
    fake_cli.write_text("", encoding="utf-8")
    namespace = {
        "__file__": str(fake_cli),
        "environ": env,
        "importlib": SimpleNamespace(
            metadata=SimpleNamespace(
                version=package_version,
                PackageNotFoundError=PackageNotFoundError,
            )
        ),
        "os": type("FakeOs", (), {"environ": env}),
        "Path": Path,
        "tomllib": tomllib,
        "Optional": Optional,
    }
    exec(helper_source, namespace)
    return namespace


def test_pyproject_declara_version_10_1_1():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert metadata["project"]["version"] == "10.1.1"


def test_resolve_cli_version_prioriza_variable_de_entorno(tmp_path):
    def fail_if_called(_name: str) -> str:  # pragma: no cover - should not run
        raise AssertionError("package metadata should not be consulted")

    helpers = _load_version_helpers(
        tmp_path,
        {"COBRA_CLI_VERSION": "env-1"},
        fail_if_called,
    )

    assert helpers["_resolve_cli_version"]() == "env-1"


def test_resolve_cli_version_usa_metadata_antes_de_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "10.1.1"\n', encoding="utf-8")

    helpers = _load_version_helpers(tmp_path, {}, lambda _name: "dist-2")

    assert helpers["_resolve_cli_version"]() == "dist-2"


def test_resolve_cli_version_usa_pyproject_sin_metadata_de_distribucion(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "10.1.1"\n', encoding="utf-8")

    def missing_distribution(_name: str) -> str:
        raise PackageNotFoundError

    helpers = _load_version_helpers(tmp_path, {}, missing_distribution)

    assert helpers["_resolve_cli_version"]() == "10.1.1"


def test_resolve_cli_version_fallback_dev_si_no_hay_metadata_ni_pyproject(tmp_path):
    def missing_distribution(_name: str) -> str:
        raise PackageNotFoundError

    helpers = _load_version_helpers(tmp_path, {}, missing_distribution)

    assert helpers["_resolve_cli_version"]() == "dev"


def test_resolve_cli_version_fallback_dev_si_project_no_es_tabla(tmp_path):
    (tmp_path / "pyproject.toml").write_text('project = "invalid"\n', encoding="utf-8")

    def missing_distribution(_name: str) -> str:
        raise PackageNotFoundError

    helpers = _load_version_helpers(tmp_path, {}, missing_distribution)

    assert helpers["_resolve_cli_version"]() == "dev"


def test_format_cli_version_oculta_commit_unknown(tmp_path):
    helpers = _load_version_helpers(
        tmp_path,
        {"COBRA_CLI_COMMIT": "unknown"},
        lambda _name: "dist-2",
    )
    helpers["CLI_VERSION"] = "10.1.1"

    assert helpers["_format_cli_version"]() == "%(prog)s 10.1.1"


def test_format_cli_version_muestra_commit_informativo(tmp_path):
    helpers = _load_version_helpers(
        tmp_path,
        {"COBRA_CLI_COMMIT": "abc123"},
        lambda _name: "dist-2",
    )
    helpers["CLI_VERSION"] = "10.1.1"

    assert helpers["_format_cli_version"]() == "%(prog)s 10.1.1 (commit abc123)"
