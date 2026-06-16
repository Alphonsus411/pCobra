from unittest.mock import patch

from pcobra.ia import analizador_sugerencias


def test_fachada_delega_en_agix_con_contrato_estable():
    with patch.object(
        analizador_sugerencias,
        "_generar_con_agix",
        return_value=["Usar nombres descriptivos"],
    ) as generar:
        resultado = analizador_sugerencias.generar_sugerencias(
            "var x = 5",
            peso_precision=0.8,
            peso_interpretabilidad=0.9,
            placer=0.1,
            activacion=0.2,
            dominancia=-0.3,
        )

    assert resultado == ["Usar nombres descriptivos"]
    generar.assert_called_once_with(
        "var x = 5",
        peso_precision=0.8,
        peso_interpretabilidad=0.9,
        placer=0.1,
        activacion=0.2,
        dominancia=-0.3,
    )
    assert analizador_sugerencias.MOTOR_SUGERENCIAS == "agix"
