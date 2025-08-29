import pytest
from io import StringIO
from unittest.mock import patch

from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils import messages


def test_custom_argument_parser_error(monkeypatch):
    captured = {}

    def fake_error(msg: str) -> None:
        captured['msg'] = msg

    monkeypatch.setattr(messages, 'mostrar_error', fake_error)
    parser = CustomArgumentParser(prog='cobra')
    parser.add_argument('--ok')
    with patch('sys.stdout', new_callable=StringIO) as out, pytest.raises(SystemExit) as exc:
        parser.parse_args(['--bad'])
    assert 'unrecognized arguments' in captured['msg']
    assert 'usage:' in out.getvalue()
    assert exc.value.code == 2
