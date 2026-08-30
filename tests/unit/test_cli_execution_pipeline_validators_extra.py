from types import SimpleNamespace

from pcobra.cobra.cli.execution_pipeline import validar_ast_seguro
from pcobra.core.semantic_validators.import_seguro import ValidadorImportSeguro


def test_validadores_extra_no_se_pierden_al_existir_cadena_del_interprete(
    tmp_path,
):
    extra = ValidadorImportSeguro()
    cadena_existente = object()
    cadena_contextual = object()
    main_file = tmp_path / "main.cobra"

    interpretador = SimpleNamespace(
        _validador=cadena_existente,
        _main_file=main_file,
        _project_root=tmp_path,
        _usar_symbol_metadata={},
    )

    llamadas = []

    def construir_cadena_prueba(validadores, **contexto):
        llamadas.append((validadores, contexto))
        return cadena_contextual

    validar_ast_seguro(
        [],
        validadores_extra=[extra],
        interpretador=interpretador,
        construir_cadena_fn=construir_cadena_prueba,
    )

    assert llamadas == [
        (
            [extra],
            {
                "main_file": main_file,
                "project_root": tmp_path,
            },
        )
    ]
