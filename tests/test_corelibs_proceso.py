import subprocess
import sys

import pytest

from pcobra.corelibs import proceso


def test_superficie_publica_proceso() -> None:
    assert proceso.__all__ == [
        "ejecutar",
        "capturar",
        "codigo_salida",
        "salida",
        "errores",
    ]


def test_captura_salida_con_argumentos_explicitos() -> None:
    resultado = proceso.capturar(
        sys.executable,
        argumentos=["-c", "print('cobra')"],
    )

    assert proceso.codigo_salida(resultado) == 0
    assert proceso.salida(resultado) == "cobra\n"
    assert proceso.errores(resultado) == ""


def test_shell_false_no_expande_metacaracteres() -> None:
    resultado = proceso.ejecutar(
        sys.executable,
        argumentos=["-c", "import sys; print(sys.argv[1])", "$NO_EXPANDIR"],
    )

    assert resultado == {"codigo": 0, "salida": "$NO_EXPANDIR\n", "error": ""}


def test_comando_inexistente_devuelve_error_determinista() -> None:
    resultado = proceso.ejecutar("comando-pcobra-inexistente-para-prueba")

    assert proceso.codigo_salida(resultado) == 127
    assert proceso.salida(resultado) == ""
    assert proceso.errores(resultado).startswith("Comando no encontrado:")


def test_timeout_devuelve_error_determinista() -> None:
    resultado = proceso.ejecutar(
        sys.executable,
        argumentos=["-c", "import time; time.sleep(1)"],
        timeout=0.01,
    )

    assert resultado == {
        "codigo": 124,
        "salida": "",
        "error": "Tiempo de espera agotado",
    }


def test_rechaza_argumentos_texto_plano() -> None:
    with pytest.raises(TypeError, match="argumentos debe ser una secuencia explícita"):
        proceso.ejecutar(sys.executable, argumentos="--version")


def test_ejecutar_usa_shell_false_por_defecto_y_shell_true_explicito(monkeypatch) -> None:
    llamadas = []

    def fake_run(*args, **kwargs):
        llamadas.append(kwargs["shell"])
        return subprocess.CompletedProcess(args[0], 0, "", "")

    monkeypatch.setattr(proceso.subprocess, "run", fake_run)

    proceso.ejecutar("python")
    proceso.ejecutar("echo ok", shell=True)

    assert llamadas == [False, True]
