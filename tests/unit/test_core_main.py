from io import StringIO
from unittest.mock import patch

from pcobra.core.main import main


def test_main_saludo_demo() -> None:
    """Verifica que el módulo demo conserve su salida esperada."""
    with patch("sys.stdout", new_callable=StringIO) as out:
        main()
    assert out.getvalue().strip() == "¡Hola desde Cobra!"
