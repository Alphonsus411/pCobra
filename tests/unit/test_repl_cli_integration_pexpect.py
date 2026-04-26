from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

import pytest

pexpect = pytest.importorskip("pexpect")


@pytest.fixture()
def cli_env() -> dict[str, str]:
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [src_path, env.get("PYTHONPATH", "")]))
    env["SQLITE_DB_KEY"] = env.get("SQLITE_DB_KEY", "test-key")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.pop("PYTEST_CURRENT_TEST", None)
    return env


def _spawn_repl(env: dict[str, str], timeout: int = 20):
    return pexpect.spawn(
        sys.executable,
        ["-m", "pcobra", "repl"],
        env=env,
        encoding="utf-8",
        timeout=timeout,
    )


@pytest.mark.integration
@pytest.mark.timeout(40)
@pytest.mark.parametrize("comando_salida", ["salir", "exit"])
def test_repl_arranca_y_sale_por_comandos_de_salida(cli_env: dict[str, str], comando_salida: str) -> None:
    child = _spawn_repl(cli_env)
    child.expect(">>> ")
    child.sendline(comando_salida)
    child.expect("Saliendo")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


@pytest.mark.integration
@pytest.mark.timeout(40)
def test_repl_ejecuta_bloque_simple_cerrado_con_fin(cli_env: dict[str, str]) -> None:
    child = _spawn_repl(cli_env)
    child.expect(">>> ")

    child.sendline("si verdadero:")
    child.expect("... ")
    child.sendline("    imprimir(11)")
    child.expect("... ")
    child.sendline("fin")

    child.expect("11")
    child.expect(">>> ")
    child.sendline("salir")
    child.expect("Saliendo")
    child.expect(pexpect.EOF)


@pytest.mark.integration
@pytest.mark.timeout(40)
def test_repl_ejecuta_bloque_anidado_con_multiples_fin(cli_env: dict[str, str]) -> None:
    child = _spawn_repl(cli_env)
    child.expect(">>> ")

    child.sendline("si verdadero:")
    child.expect("... ")
    child.sendline("    mientras falso:")
    child.expect("... ")
    child.sendline("        imprimir(0)")
    child.expect("... ")
    child.sendline("    fin")
    child.expect("... ")
    child.sendline("    imprimir(42)")
    child.expect("... ")
    child.sendline("fin")

    child.expect("42")
    child.expect(">>> ")
    child.sendline("salir")
    child.expect("Saliendo")
    child.expect(pexpect.EOF)


@pytest.mark.integration
@pytest.mark.timeout(40)
def test_repl_persiste_variables_entre_envios(cli_env: dict[str, str]) -> None:
    child = _spawn_repl(cli_env)
    child.expect(">>> ")

    child.sendline("var contador = 7")
    child.expect(">>> ")
    child.sendline("imprimir(contador)")
    child.expect("7")
    child.expect(">>> ")

    child.sendline("salir")
    child.expect("Saliendo")
    child.expect(pexpect.EOF)


@pytest.mark.integration
@pytest.mark.timeout(40)
def test_repl_se_recupera_tras_error_y_continua_sin_crash(cli_env: dict[str, str]) -> None:
    child = _spawn_repl(cli_env)
    child.expect(">>> ")

    child.sendline("fin")
    child.expect("Se encontró 'fin' inesperado")
    child.expect(">>> ")

    child.sendline("imprimir(7)")
    child.expect("7")
    child.expect(">>> ")

    child.sendline("salir")
    child.expect("Saliendo")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


@pytest.mark.integration
@pytest.mark.timeout(40)
def test_paridad_representativa_repl_vs_run_en_salida_observable(
    cli_env: dict[str, str], tmp_path: Path
) -> None:
    script = tmp_path / "estado_salida.co"
    script.write_text("imprimir(variable_inexistente)", encoding="utf-8")

    run_result = subprocess.run(
        [sys.executable, "-m", "pcobra", "run", str(script)],
        env=cli_env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run_result.returncode == 1
    assert "Variable no declarada" in run_result.stdout

    child = _spawn_repl(cli_env)
    child.expect(">>> ")
    child.sendline("imprimir(variable_inexistente)")
    child.expect("Variable no declarada")
    child.expect(">>> ")

    child.sendline("salir")
    child.expect("Saliendo")
    child.expect(pexpect.EOF)
    child.wait()

    assert child.exitstatus == 0
