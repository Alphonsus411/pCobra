import subprocess

from core.cobra_config import tiempo_max_transpilacion


def test_cli_import_help():
    """Verifica que la CLI responde y que `tiempo_max_transpilacion` se importa."""
    # Llamar a la función para garantizar que el módulo se carga sin errores
    tiempo_max_transpilacion()
    try:
        subprocess.run(
            ["cobra", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print("STDOUT:", exc.stdout)
        print("STDERR:", exc.stderr)
        raise
