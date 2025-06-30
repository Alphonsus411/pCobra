import pytest
from io import StringIO
from unittest.mock import patch
import backend  # ensure backend aliases are initialized
from src.cli.cli import main


def test_cli_help():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
    assert "uso" in out.getvalue().lower() or "usage" in out.getvalue().lower()
