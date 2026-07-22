from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from pcobra.cobra.cli.services.run_service import RunService


def test_factorial_recursivo_oficial_ejecuta_sin_falso_ciclo_runtime():
    ruta = Path("examples/avanzados/funciones/factorial_recursivo.cobra")
    codigo = ruta.read_text(encoding="utf-8")
    servicio = RunService()
    stdout = StringIO()
    stderr = StringIO()

    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = servicio.ejecutar_normal(
            codigo,
            seguro=False,
            extra_validators=None,
            main_file=ruta,
        )

    assert rc == 0
    assert stdout.getvalue().strip().endswith("120")
    assert "Recursive evaluation detected" not in stderr.getvalue()
