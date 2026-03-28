from pathlib import Path

from scripts.generate_target_policy_docs import (
    POLICY_RUNTIME_SPLIT_END,
    POLICY_RUNTIME_SPLIT_START,
    POLICY_STATUS_TABLE_END,
    POLICY_STATUS_TABLE_START,
    POLICY_TIERS_END,
    POLICY_TIERS_START,
    _policy_runtime_split_md,
    _policy_status_table_md,
    _policy_tiers_md,
)
from scripts.generar_matriz_transpiladores import _build_markdown
from pcobra.cobra.cli.target_policies import build_cli_compile_examples


def _extract_block(text: str, *, start: str, end: str) -> str:
    assert start in text, f"Falta marcador start: {start}"
    assert end in text, f"Falta marcador end: {end}"
    _, remainder = text.split(start, 1)
    block, _ = remainder.split(end, 1)
    return block.strip()


def test_targets_policy_bloques_criticos_siguen_snapshot_generado():
    content = Path("docs/targets_policy.md").read_text(encoding="utf-8")

    tiers_block = _extract_block(content, start=POLICY_TIERS_START, end=POLICY_TIERS_END)
    status_block = _extract_block(
        content,
        start=POLICY_STATUS_TABLE_START,
        end=POLICY_STATUS_TABLE_END,
    )
    runtime_split_block = _extract_block(
        content,
        start=POLICY_RUNTIME_SPLIT_START,
        end=POLICY_RUNTIME_SPLIT_END,
    )

    assert tiers_block == _policy_tiers_md().strip()
    assert status_block == _policy_status_table_md().strip()
    assert runtime_split_block == _policy_runtime_split_md().strip()


def test_matriz_transpiladores_conserva_bloques_generados_obligatorios():
    content = Path("docs/matriz_transpiladores.md").read_text(encoding="utf-8")
    assert "<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->" in content
    assert "<!-- END GENERATED MATRIZ POLICY SUMMARY -->" in content
    assert "<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->" in content
    assert "<!-- END GENERATED MATRIZ STATUS TABLE -->" in content


def test_matriz_transpiladores_bloques_criticos_siguen_snapshot_generado():
    content = Path("docs/matriz_transpiladores.md").read_text(encoding="utf-8")
    generated_content = _build_markdown()

    summary_block = _extract_block(
        content,
        start="<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->",
        end="<!-- END GENERATED MATRIZ POLICY SUMMARY -->",
    )
    expected_summary_block = _extract_block(
        generated_content,
        start="<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->",
        end="<!-- END GENERATED MATRIZ POLICY SUMMARY -->",
    )

    status_block = _extract_block(
        content,
        start="<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->",
        end="<!-- END GENERATED MATRIZ STATUS TABLE -->",
    )
    expected_status_block = _extract_block(
        generated_content,
        start="<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->",
        end="<!-- END GENERATED MATRIZ STATUS TABLE -->",
    )

    assert summary_block == expected_summary_block
    assert status_block == expected_status_block


def test_ejemplos_cli_generados_derivan_de_target_policies():
    rst = Path("docs/_generated/cli_backend_examples.rst").read_text(encoding="utf-8")
    for command in build_cli_compile_examples():
        assert f"   {command}" in rst
