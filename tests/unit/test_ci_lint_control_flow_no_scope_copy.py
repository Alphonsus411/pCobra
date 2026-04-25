from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.ci.lint_control_flow_no_scope_copy import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _interpreter_stub(
    *,
    condicional_body: str = "        return None\n",
    mientras_body: str = "        return None\n",
) -> str:
    return (
        "class InterpretadorCobra:\n"
        "    def ejecutar_condicional(self, nodo):\n"
        f"{condicional_body}"
        "    def ejecutar_mientras(self, nodo):\n"
        f"{mientras_body}"
    )


def test_lint_detecta_env_copy_en_mientras(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "core" / "interpreter.py",
        _interpreter_stub(mientras_body="        cache = env.copy()\n        return cache\n"),
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "patrón prohibido `env.copy(`" in violations[0]
    assert "ejecutar_mientras" in violations[0]


def test_lint_detecta_dict_env_values_en_condicional(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "core" / "interpreter.py",
        _interpreter_stub(
            condicional_body="        snapshot = dict(env.values)\n        return snapshot\n"
        ),
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "patrón prohibido `dict(env.values)`" in violations[0]
    assert "ejecutar_condicional" in violations[0]


def test_lint_detecta_scope_nuevo_en_cada_iteracion_de_mientras(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "core" / "interpreter.py",
        _interpreter_stub(
            mientras_body=(
                "        while True:\n"
                "            self.contextos.append({})\n"
                "        return None\n"
            )
        ),
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "no debe crear scopes por iteración" in violations[0]


def test_lint_pasa_con_control_flow_sin_patrones_prohibidos(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "core" / "interpreter.py",
        _interpreter_stub(
            condicional_body="        return self._evaluar_condicion_control(nodo.condicion)\n",
            mientras_body=(
                "        while self._evaluar_condicion_control(nodo.condicion):\n"
                "            for instruccion in nodo.cuerpo:\n"
                "                self.ejecutar_nodo(instruccion)\n"
                "        return None\n"
            ),
        ),
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_script_lint_control_flow_no_scope_copy_pasa_en_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/ci/lint_control_flow_no_scope_copy.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
