from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.cli.cli import main


def test_cli_gui_invokes_flet_app():
    mock_app = MagicMock()
    fake_flet = SimpleNamespace(
        app=mock_app,
        TextField=MagicMock(),
        Text=MagicMock(),
        ElevatedButton=MagicMock(),
        Page=MagicMock(),
    )
    with patch.dict('sys.modules', {'flet': fake_flet}):
        main(['gui'])
    mock_app.assert_called_once()
