import pytest
from argcomplete.completers import FilesCompleter

from cobra.cli.cli import CliApplication
from cobra.cli.utils.argument_parser import CustomArgumentParser


def test_configure_autocomplete_with_list_choices():
    app = CliApplication()
    parser = CustomArgumentParser(prog="cobra")
    parser.add_argument("archivo", choices=["uno", "dos"])

    try:
        app._configure_autocomplete(parser)
    except Exception as exc:  # pragma: no cover
        pytest.fail(f"_configure_autocomplete raised {exc}")

    action = next(a for a in parser._actions if a.dest == "archivo")
    assert isinstance(getattr(action, "completer", None), FilesCompleter)
