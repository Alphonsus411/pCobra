import pytest

from pcobra.cobra.cli.cli import CliApplication


def test_build_installer_target_is_hidden_from_public_help(capsys):
    app = CliApplication()
    app.initialize()

    with pytest.raises(SystemExit) as exc_info:
        app._parse_arguments(["build", "--help"])

    assert exc_info.value.code == 0
    help_output = capsys.readouterr().out
    assert "--target" not in help_output
    assert "--installer" in help_output


def test_build_installer_still_accepts_hidden_target_option():
    app = CliApplication()
    app.initialize()

    args = app._parse_arguments([
        "build",
        "--installer",
        ".",
        "--target",
        "current",
    ])

    assert args.command == "build"
    assert args.installer is True
    assert args.file == "."
    assert args.target == "current"
