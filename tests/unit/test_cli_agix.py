from argparse import Namespace
from unittest.mock import MagicMock, patch

from cobra.cli.cli import main
from cobra.cli.commands.agix_cmd import AgixCommand


def test_cli_agix_generates_suggestion(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    cmd = AgixCommand()
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )
    instancia = MagicMock()
    instancia.select_best_model.return_value = {"reason": "Usar nombres descriptivos"}
    with patch("ia.analizador_agix.Reasoner", return_value=instancia):
        cmd.run(args)
    salida = capsys.readouterr().out.strip()
    assert "Usar nombres descriptivos" in salida


def test_cli_agix_pad_values(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    instancia = MagicMock()
    instancia.select_best_model.return_value = {"reason": "Usar nombres descriptivos"}
    with patch("ia.analizador_agix.Reasoner", return_value=instancia):
        with patch("ia.analizador_agix.PADState") as pad_mock:
            with patch("cobra.cli.cli.setup_gettext", return_value=lambda s: s):
                with patch(
                    "cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES",
                    new=[AgixCommand],
                ):
                    main(
                        [
                            "agix",
                            str(archivo),
                            "--placer",
                            "0.1",
                            "--activacion",
                            "0.2",
                            "--dominancia",
                            "-0.3",
                        ]
                    )
    salida = capsys.readouterr().out.strip()
    assert "Usar nombres descriptivos" in salida
    pad_mock.assert_called_once_with(0.1, 0.2, -0.3)
    instancia.modular_por_emocion.assert_called_once_with(pad_mock.return_value)
