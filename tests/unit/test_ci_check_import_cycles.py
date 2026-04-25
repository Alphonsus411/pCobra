from __future__ import annotations

from pathlib import Path

from scripts.ci.check_import_cycles import (
    build_import_graph,
    find_scope_cycle_components,
    find_layer_violations,
    format_cycle_report,
    main,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_ciclo_en_grafo(tmp_path: Path) -> None:
    src = tmp_path / "src"
    _write(src / "pcobra" / "cobra" / "cli" / "a.py", "import pcobra.cobra.cli.b\n")
    _write(src / "pcobra" / "cobra" / "cli" / "b.py", "import pcobra.cobra.cli.c\n")
    _write(src / "pcobra" / "cobra" / "cli" / "c.py", "import pcobra.cobra.cli.a\n")

    graph = build_import_graph(src)
    _, _, cycle_components = find_scope_cycle_components(graph, "pcobra.cobra.cli")

    assert cycle_components
    cycle = sorted(cycle_components[0])
    cycle.append(cycle[0])
    report = format_cycle_report(cycle, src_dir=src, root=tmp_path)
    assert "Cadena:" in report
    assert "pcobra.cobra.cli.a" in report
    assert "pcobra.cobra.cli.b" in report
    assert "pcobra.cobra.cli.c" in report


def test_detecta_violaciones_de_capas(tmp_path: Path) -> None:
    src = tmp_path / "src"
    _write(
        src / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "from pcobra.cobra.cli.commands.compile_cmd import CompileCommand\n",
    )
    _write(
        src / "pcobra" / "cobra" / "cli" / "commands" / "compile_cmd.py",
        "class CompileCommand:\n    pass\n",
    )
    _write(
        src / "pcobra" / "cobra" / "core" / "runtime.py",
        "from pcobra.cobra.cli.public_command_policy import PUBLIC_COMMANDS\n",
    )
    _write(
        src / "pcobra" / "cobra" / "cli" / "public_command_policy.py",
        "PUBLIC_COMMANDS = ()\n",
    )

    graph = build_import_graph(src)
    violations = find_layer_violations(graph)

    kinds = {item.kind for item in violations}
    assert "cross_command" in kinds
    assert "core_depends_on_cli" in kinds


def test_detecta_dependencia_de_pcobra_core_hacia_cli(tmp_path: Path) -> None:
    src = tmp_path / "src"
    _write(
        src / "pcobra" / "core" / "runtime_guard.py",
        "from pcobra.cobra.cli.public_command_policy import PUBLIC_COMMANDS\n",
    )
    _write(
        src / "pcobra" / "cobra" / "cli" / "public_command_policy.py",
        "PUBLIC_COMMANDS = ()\n",
    )

    graph = build_import_graph(src)
    violations = find_layer_violations(graph)

    assert any(item.kind == "core_depends_on_cli" for item in violations)


def test_main_pasa_en_repositorio_actual() -> None:
    code = main()
    assert code == 0


def test_permite_import_base_entre_comandos(tmp_path: Path) -> None:
    src = tmp_path / "src"
    _write(
        src / "pcobra" / "cobra" / "cli" / "commands_v2" / "ok.py",
        "from pcobra.cobra.cli.commands.base import BaseCommand\n",
    )
    _write(
        src / "pcobra" / "cobra" / "cli" / "commands" / "base.py",
        "class BaseCommand:\n    pass\n",
    )

    graph = build_import_graph(src)
    violations = find_layer_violations(graph)

    assert not violations
