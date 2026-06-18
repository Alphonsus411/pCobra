from pathlib import Path

from scripts.ci.audit_public_backend_exposure_terms import find_violations


def test_auditor_rechaza_exposiciones_en_registro_choices_y_docs_publicas(tmp_path):
    (tmp_path / "src/pcobra/cobra/transpilers").mkdir(parents=True)
    (tmp_path / "src/pcobra/cobra/cli/commands").mkdir(parents=True)
    (tmp_path / "src/pcobra/gui").mkdir(parents=True)
    (tmp_path / "docs").mkdir(parents=True)

    (tmp_path / "src/pcobra/cobra/transpilers/registry.py").write_text(
        "TRANSPILER_CLASS_PATHS = {'go': object}\n",
        encoding="utf-8",
    )
    (tmp_path / "src/pcobra/cobra/cli/commands/compile_cmd.py").write_text(
        "parser.add_argument('--tipo', choices=('python', 'js'))\n",
        encoding="utf-8",
    )
    (tmp_path / "src/pcobra/gui/runtime.py").write_text(
        "Dropdown(options=[Option('java')])\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/guia.md").write_text(
        "Lenguajes destino disponibles: python, javascript, wasm, rust.\n",
        encoding="utf-8",
    )

    violations = find_violations(tmp_path)

    assert {violation.scope for violation in violations} == {
        "registro público de transpiladores",
        "choices públicos CLI/GUI",
        "documentación pública",
    }
    assert {violation.term.lower() for violation in violations} >= {"go", "js", "java", "wasm"}


def test_auditor_permite_docs_historicos_pruebas_de_rechazo_y_shims_legacy(tmp_path):
    (tmp_path / "docs/historico").mkdir(parents=True)
    (tmp_path / "tests/unit").mkdir(parents=True)
    (tmp_path / "src/cobra/cli").mkdir(parents=True)

    (tmp_path / "docs/historico/targets.md").write_text(
        "Registro histórico: `go`, `cpp`, `java`, `wasm`, `asm`.\n",
        encoding="utf-8",
    )
    (tmp_path / "tests/unit/test_rechazo_aliases.py").write_text(
        "def test_rechaza_aliases():\n    assert 'node'\n",
        encoding="utf-8",
    )
    (tmp_path / "src/cobra/cli/target_policies.py").write_text(
        "from pcobra.cobra.cli.target_policies import *  # shim legacy py/js\n",
        encoding="utf-8",
    )

    assert find_violations(tmp_path) == []
