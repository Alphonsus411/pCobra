from argparse import Namespace
from unittest.mock import create_autospec, patch

import pytest

from pcobra.ia import analizador_agix
from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands.agix_cmd import AgixCommand
from pcobra.ia.analizador_agix import FalloMotorAGIXError


def _doble_reasoner():
    clase = create_autospec(analizador_agix.Reasoner, spec_set=True)
    return clase, clase.return_value


def test_cli_agix_generates_suggestion(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.cobra"
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
    reasoner_cls, instancia = _doble_reasoner()
    instancia.select_best_model.return_value = {
        "name": "nombres descriptivos",
        "accuracy": 0.9,
        "reason": "Usar nombres descriptivos",
    }
    with patch("pcobra.ia.analizador_agix.Reasoner", reasoner_cls):
        resultado = cmd.run(args)
    salida = capsys.readouterr().out.strip()
    assert "Usar nombres descriptivos" in salida
    assert resultado == 0
    reasoner_cls.assert_called_once_with()
    instancia.select_best_model.assert_called_once()


def test_cli_agix_pad_values(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.cobra"
    archivo.write_text("var x = 5")
    reasoner_cls, instancia = _doble_reasoner()
    pad_mock = create_autospec(analizador_agix.PADState, spec_set=True)
    instancia.select_best_model.return_value = {
        "name": "nombres descriptivos",
        "accuracy": 0.9,
        "reason": "Usar nombres descriptivos",
    }
    with patch("pcobra.ia.analizador_agix.Reasoner", reasoner_cls):
        with patch("pcobra.ia.analizador_agix.PADState", pad_mock):
            with patch.object(cli_module, "setup_gettext", return_value=lambda s: s):
                with (
                    patch.object(
                        cli_module,
                        "resolve_command_profile",
                        return_value="development",
                    ),
                    patch.object(
                        cli_module.AppConfig,
                        "BASE_COMMAND_CLASSES",
                        [AgixCommand],
                    ),
                ):
                    cli_module.main(
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


def test_cli_agix_pasa_argumentos_de_seleccion_y_muestra_error_concreto(
    tmp_path, capsys
):
    archivo = tmp_path / "ejemplo.cobra"
    archivo.write_text("var x = 5")
    args = Namespace(
        archivo=str(archivo),
        peso_precision=0.75,
        peso_interpretabilidad=1.25,
        placer=None,
        activacion=None,
        dominancia=None,
    )
    reasoner_cls, instancia = _doble_reasoner()
    instancia.select_best_model.side_effect = ValueError(
        "evaluaciones rechazadas por AGIX"
    )

    with patch("pcobra.ia.analizador_agix.Reasoner", reasoner_cls):
        resultado = AgixCommand().run(args)

    salida = capsys.readouterr().out
    assert resultado == 1
    assert "evaluaciones rechazadas por AGIX" in salida
    evaluaciones = instancia.select_best_model.call_args.args[0]
    assert all(0.0 <= evaluacion["accuracy"] <= 0.75 for evaluacion in evaluaciones)
    assert all(evaluacion["interpretability"] >= 0.0 for evaluacion in evaluaciones)


def test_cli_agix_muestra_fallo_previsto_del_motor(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.cobra"
    archivo.write_text("var x = 5")
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )

    with patch(
        "pcobra.cobra.cli.commands.agix_cmd.generar_sugerencias",
        side_effect=FalloMotorAGIXError("servicio temporalmente ocupado"),
    ):
        resultado = AgixCommand().run(args)

    assert resultado == 1
    assert "No se pudo ejecutar el motor AGIX" in capsys.readouterr().out


def test_cli_agix_no_oculta_errores_de_programacion(tmp_path):
    archivo = tmp_path / "ejemplo.cobra"
    archivo.write_text("var x = 5")
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )

    with patch(
        "pcobra.cobra.cli.commands.agix_cmd.generar_sugerencias",
        side_effect=TypeError("fallo de programación"),
    ):
        with pytest.raises(TypeError, match="fallo de programación"):
            AgixCommand().run(args)
