import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import standard_library.util as util


def test_util():
    assert util.es_nulo(None) is True
    assert util.es_nulo(0) is False
    assert util.es_vacio([]) is True
    assert util.es_vacio("a") is False
    assert util.repetir("a", 3) == "aaa"

