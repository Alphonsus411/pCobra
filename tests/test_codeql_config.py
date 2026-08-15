"""Contratos mínimos para la configuración de CodeQL."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEQL_CONFIG = ROOT / ".github" / "codeql" / "custom" / "codeql-config.yml"
CODEQL_WORKFLOW = ROOT / ".github" / "workflows" / "codeql.yml"
MISSING_CODEGEN_EXCEPTION_QUERY = (
    ROOT / ".github" / "codeql" / "custom" / "missing-codegen-exception.ql"
)
UNSAFE_EVAL_EXEC_QUERY = ROOT / ".github" / "codeql" / "custom" / "unsafe-eval-exec.ql"
AST_NO_EXPORT_VALIDATION_QUERY = (
    ROOT / ".github" / "codeql" / "custom" / "ast-no-export-validation.ql"
)
AST_NO_TYPE_VALIDATION_QUERY = (
    ROOT / ".github" / "codeql" / "custom" / "ast-no-type-validation.ql"
)


def _codeql_config_text() -> str:
    return CODEQL_CONFIG.read_text(encoding="utf-8")


def test_codeql_workflow_runs_both_custom_query_harnesses() -> None:
    """Ejecuta ambos harnesses con el binario publicado por CodeQL init."""
    workflow = CODEQL_WORKFLOW.read_text(encoding="utf-8")

    assert '"${{ steps.codeql-init.outputs.codeql-path }}" test run' in workflow
    assert ".github/codeql/custom/test/ast_no_export_validation" in workflow
    assert ".github/codeql/custom/test/ast_no_type_validation" in workflow


def test_codeql_production_config_keeps_fixtures_isolated() -> None:
    """Excluye ambos árboles de fixtures sin retirar la consulta productiva."""
    config = _codeql_config_text()

    assert "  - '.github/codeql/custom/test/ast_no_export_validation/**'" in config
    assert "  - '.github/codeql/custom/test/ast_no_type_validation/**'" in config
    assert "  - uses: ./.github/codeql/custom/ast-no-type-validation.ql" in config


def test_codeql_paths_exist_in_repository() -> None:
    """Evita limitar el análisis de producción a un subárbol."""
    config = _codeql_config_text()

    assert "paths:" not in config
    assert "  - 'tests/**'" not in config
    assert "  - 'src/**'" not in config


def test_codeql_custom_queries_resolve_from_repository_root() -> None:
    """Evita referencias locales que no resuelven durante CodeQL init."""
    config = _codeql_config_text()
    query_paths = (
        "./.github/codeql/custom/ast-no-export-validation.ql",
        "./.github/codeql/custom/ast-no-type-validation.ql",
        "./.github/codeql/custom/missing-codegen-exception.ql",
        "./.github/codeql/custom/unsafe-eval-exec.ql",
    )

    for query_path in query_paths:
        assert f"  - uses: {query_path}" in config
        assert (ROOT / query_path).is_file(), query_path


def test_configured_validation_queries_declare_a_non_empty_kind() -> None:
    """Exige que las tres queries de validación declaren su tipo de resultado."""
    queries = (
        AST_NO_EXPORT_VALIDATION_QUERY,
        AST_NO_TYPE_VALIDATION_QUERY,
        MISSING_CODEGEN_EXCEPTION_QUERY,
    )

    for query_path in queries:
        query = query_path.read_text(encoding="utf-8")
        header = query.split("*/", maxsplit=1)[0]

        assert re.search(r"^\s*\*\s+@kind\s+\S+\s*$", header, re.MULTILINE), query_path


def test_ast_export_query_uses_formal_isolated_fixtures() -> None:
    """Mantiene los casos deliberados fuera del árbol analizado en producción."""
    config = _codeql_config_text()
    fixture_dir = (
        ROOT / ".github" / "codeql" / "custom" / "test" / "ast_no_export_validation"
    )

    assert "  - '.github/codeql/custom/test/ast_no_export_validation/**'" in config
    assert "  - 'tests/**'" not in config
    assert "  - 'src/**'" not in config
    assert (fixture_dir / "insecure" / "ast-no-export-validation.qlref").read_text(
        encoding="utf-8"
    ).strip() == "ast-no-export-validation.ql"
    assert "return parse_source(source)" in (
        fixture_dir / "insecure" / "insecure_alias_indirection.py"
    ).read_text(encoding="utf-8")
    assert "validate_ast(tree)" in (
        fixture_dir / "safe" / "safe_validated_export.py"
    ).read_text(encoding="utf-8")
    assert AST_NO_EXPORT_VALIDATION_QUERY.is_file()


def test_ast_type_query_uses_supported_api_and_isolated_fixtures() -> None:
    """Valida la API de llamadas y aísla los casos inseguros deliberados."""
    config = _codeql_config_text()
    fixture_dir = (
        ROOT / ".github" / "codeql" / "custom" / "test" / "ast_no_type_validation"
    )
    query = AST_NO_TYPE_VALIDATION_QUERY.read_text(encoding="utf-8")

    assert "  - '.github/codeql/custom/test/ast_no_type_validation/**'" in config
    assert "exists(Call call, Name callee |" in query
    assert "call.getFunc() = callee" in query
    assert 'callee.getId() = "isinstance"' in query
    assert "FunctionCall" not in query
    assert "not exists(Function m |" in query
    assert 'c.getName().regexpMatch("^Nodo.*")' in query
    assert (fixture_dir / "insecure" / "ast-no-type-validation.qlref").is_file()
    assert (fixture_dir / "safe" / "ast-no-type-validation.qlref").is_file()


def test_missing_codegen_exception_uses_supported_try_api() -> None:
    """Evita reintroducir tipos o relaciones inexistentes para ``Try``."""
    query = MISSING_CODEGEN_EXCEPTION_QUERY.read_text(encoding="utf-8")

    assert "from Function m, File f" in query
    assert "m.getLocation().getFile() = f" in query
    assert 'regexpMatch("^src/cobra/transpilers/transpiler/.*")' in query
    assert "exists(Try t |" in query
    assert "t.getScope() = m" in query
    assert "from Method" not in query
    assert "TryStmt" not in query
    assert "getEnclosingCallable" not in query


def test_unsafe_eval_exec_preserves_positive_and_negative_fixtures() -> None:
    """La query conserva una violación y excluye únicamente el sandbox."""
    query = UNSAFE_EVAL_EXEC_QUERY.read_text(encoding="utf-8")
    fixtures = ROOT / "tests" / "unit" / "codeql_fixtures" / "unsafe_eval_exec"

    assert 'regexpMatch("^src/.*")' in query
    assert 'not f.getRelativePath().regexpMatch("^src/core/sandbox.py$")' in query
    assert 'builtin.getId() in ["eval", "exec"]' in query
    assert "f = c.getLocation().getFile()" in query
    assert 'select c, "Uso potencialmente inseguro de eval/exec"' in query
    assert "eval(expression)" in (fixtures / "src" / "violation.py").read_text(
        encoding="utf-8"
    )
    assert "eval(expression)" in (fixtures / "src" / "core" / "sandbox.py").read_text(
        encoding="utf-8"
    )
