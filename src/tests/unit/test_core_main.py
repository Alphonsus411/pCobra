import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))

from core.main import main


def test_main_saludo(capsys=None):
    """Verifica que se imprima el saludo correcto."""
    with patch("sys.stdout", new_callable=StringIO) as out:
        main()
    assert out.getvalue().strip() == "¡Hola desde Cobra!"
