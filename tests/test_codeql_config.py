"""Contratos mínimos para la configuración de CodeQL."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEQL_CONFIG = ROOT / ".github" / "codeql" / "custom" / "codeql-config.yml"


def _codeql_config_text() -> str:
    return CODEQL_CONFIG.read_text(encoding="utf-8")


def test_codeql_paths_exist_in_repository() -> None:
    """Evita inicializar CodeQL con rutas inexistentes."""
    config = _codeql_config_text()

    for path in ("src",):
        assert f"  - {path}" in config
        assert (ROOT / path).exists(), path


def test_codeql_custom_queries_resolve_from_repository_root() -> None:
    """Evita referencias locales que no resuelven durante CodeQL init."""
    config = _codeql_config_text()
    query_paths = (
        "./.github/codeql/custom/ast-no-type-validation.ql",
        "./.github/codeql/custom/missing-codegen-exception.ql",
        "./.github/codeql/custom/unsafe-eval-exec.ql",
    )

    for query_path in query_paths:
        assert f"  - uses: {query_path}" in config
        assert (ROOT / query_path).is_file(), query_path
