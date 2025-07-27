from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import standard_library.fecha as fecha


def test_fecha():
    ahora = fecha.hoy()
    assert isinstance(ahora, datetime)
    form = fecha.formatear(datetime(2020, 1, 1), "%Y")
    assert form == "2020"
    futuro = fecha.sumar_dias(datetime(2020, 1, 1), 5)
    assert futuro == datetime(2020, 1, 6)

