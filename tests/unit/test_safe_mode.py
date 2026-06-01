from io import StringIO
from unittest.mock import patch

import pytest

import pcobra  # garantiza rutas para submódulos
from cobra.cli.cli import CliApplication
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoLlamadaFuncion, NodoValor
from core.interpreter import InterpretadorCobra
from core.semantic_validators import PrimitivaPeligrosaError


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens).parsear()


def metadata_validador_usar(interp):
    cursor = interp._validador
    while cursor is not None:
        metadata = getattr(cursor, "_metadata_simbolos_usar", None)
        if metadata is not None:
            return metadata
        cursor = getattr(cursor, "siguiente", None)
    raise AssertionError("validador de metadata usar no encontrado")


@pytest.mark.parametrize(
    "codigo",
    [
        "leer_archivo('x.txt')",
        "obtener_url('ejemplo')",
        "leer('x.txt')",
        "escribir('x.txt', 'hola')",
        "enviar_post('u', 'd')",
        "ejecutar(['ls'])",
        "listar_dir('.')",
    ],
)
def test_primitivas_rechazadas_en_modo_seguro(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_codigo_seguro_se_ejecuta_en_modo_seguro():
    interp = InterpretadorCobra()
    nodo = NodoLlamadaFuncion("imprimir", [NodoValor("hola")])
    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_llamada_funcion(nodo)
    assert out.getvalue().strip() == "hola"


def test_existe_no_se_habilita_solo_por_nombre_sin_usar_archivo():
    interp = InterpretadorCobra()
    ast = generar_ast('func existe(ruta) { retorno verdadero }\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_existe_publico_desde_usar_acepta_ruta_relativa():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    salida = out.getvalue()
    assert "verdadero" in salida or "falso" in salida


def test_existe_backend_crudo_sigue_bloqueado_aun_con_usar_archivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nexiste = leer_archivo\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_metadata_usar_archivo_existe_cadena_completa():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata = interp._usar_symbol_metadata["existe"]
    assert metadata["module"] == "archivo"
    assert metadata["origen_modulo"] == "archivo"
    assert metadata["canonical_module"] == "archivo"
    assert metadata["origin_module"] == "archivo"
    assert metadata["origen_tipo"] == "public_wrapper"
    assert metadata["is_public_export"] is True
    assert metadata["public_api"] is True
    assert metadata["is_sanitized_wrapper"] is True
    assert metadata["safe_wrapper"] is True
    assert metadata["introduced_by"] == "usar"
    assert metadata["introduced_by_usar"] is True
    assert metadata["python_module"] in {
        "pcobra.standard_library.archivo",
        "cobra.standard_library.archivo",
    }

    metadata_validador = metadata_validador_usar(interp)["existe"]
    assert metadata_validador["module"] == "archivo"
    assert metadata_validador["origen_modulo"] == "archivo"
    assert metadata_validador["canonical_module"] == "archivo"
    assert metadata_validador["origen_tipo"] == "public_wrapper"
    assert metadata_validador["introduced_by_usar"] is True


def test_usar_metadata_minima_y_consistente_entre_interprete_y_validador():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"')

    interp.ejecutar_ast(ast)

    requeridos = {
        "module",
        "origen_modulo",
        "exported_name",
        "is_sanitized_wrapper",
        "public_api",
        "introduced_by_usar",
    }

    for nombre, metadata in interp._usar_symbol_metadata.items():
        faltantes = requeridos - set(metadata.keys())
        assert not faltantes, f"metadata incompleta para {nombre}: {sorted(faltantes)}"
        assert metadata["module"] == "archivo"
        assert metadata["origen_modulo"] == "archivo"
        assert metadata["exported_name"] == nombre
        assert metadata["is_sanitized_wrapper"] is True
        assert metadata["public_api"] is True
        assert metadata["introduced_by_usar"] is True

        metadata_validador = metadata_validador_usar(interp)[nombre]
        assert metadata_validador == metadata


def test_usar_numero_reimport_idempotente_conserva_modulo_original():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "numero"\nusar "numero"')

    interp.ejecutar_ast(ast)

    assert interp._usar_symbol_metadata["absoluto"]["module"] == "numero"
    assert metadata_validador_usar(interp)["absoluto"]["module"] == "numero"


def test_usar_metadata_se_sincroniza_con_validador_detras_de_auditoria():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    assert (
        metadata_validador_usar(interp)["existe"]
        == interp._usar_symbol_metadata["existe"]
    )


def test_usar_metadata_no_fuga_entre_interpretes():
    primer_interp = InterpretadorCobra()
    primer_interp.ejecutar_ast(generar_ast('usar "archivo"'))

    segundo_interp = InterpretadorCobra()
    with pytest.raises(PrimitivaPeligrosaError):
        segundo_interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))


def test_usar_detecta_divergencia_metadata_interprete_y_validador():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"]["public_api"] = False
    ast_llamada = generar_ast('imprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_ausente_sin_fallback_permisivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    # Simula bypass: símbolo registrado pero metadata ausente.
    metadata_validador_usar(interp).pop("existe", None)
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)




def test_existe_rechaza_metadata_no_dict_sin_fallback_permisivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"] = []
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_interprete_no_dict_sin_fallback_permisivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._usar_symbol_metadata["existe"] = []
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_sin_clave_obligatoria():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"].pop("introduced_by_usar", None)
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)

@pytest.mark.parametrize("modulo", ["io", "numpy"])
def test_existe_rechaza_metadata_con_modulo_distinto(modulo):
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"]["module"] = modulo
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_con_exported_name_distinto():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"]["exported_name"] = "leer_archivo"
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_con_public_api_tipo_incorrecto():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"]["public_api"] = "true"
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


@pytest.mark.parametrize(
    "codigo",
    [
        'usar "archivo"\nimprimir(existe("/etc/passwd"))',
        'usar "archivo"\nimprimir(existe("../secreto.txt"))',
        'usar "archivo"\nimprimir(existe("C:/Windows/System32/drivers/etc/hosts"))',
        'usar "archivo"\nimprimir(existe("\\\\servidor\\compartido\\secreto.txt"))',
    ],
)
def test_existe_publico_desde_usar_bloquea_rutas_fuera_de_politica(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)



def test_existe_publico_no_habilita_simbolos_backend_crudos_no_publicos():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(leer_archivo("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_existe_local_con_nombre_existe_sigue_bloqueado():
    interp = InterpretadorCobra()
    ast = generar_ast('func existe(ruta) { retorno verdadero }\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


@pytest.mark.parametrize(
    "codigo",
    [
        'imprimir(eliminar("README.md"))',
        'func obtener_url(x) { retorno x }\nimprimir(obtener_url("https://ejemplo"))',
        'usar "archivo"\nimprimir(leer_archivo("README.md"))',
    ],
)
def test_otros_simbolos_peligrosos_siguen_bloqueados(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)

def test_cli_default_mantiene_modo_seguro_y_fallback_inseguro_deshabilitado():
    app = CliApplication()
    app.initialize()
    args = app._parse_arguments([])
    assert args.seguro is True
    assert args.allow_insecure_fallback is False


@pytest.mark.parametrize(
    "codigo",
    [
        'usar "archivo"\nimprimir(existe("./../secreto.txt"))',
        'usar "archivo"\nimprimir(existe("carpeta/../../secreto.txt"))',
    ],
)
def test_existe_publico_desde_usar_bloquea_traversal_normalizado(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_usar_numpy_rechaza_con_error_corto():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "numpy"')

    with pytest.raises(PermissionError, match="No se puede usar 'numpy': módulo fuera del catálogo público"):
        interp.ejecutar_ast(ast)


def test_existe_rechaza_metadata_con_is_sanitized_wrapper_false():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    metadata_validador_usar(interp)["existe"]["is_sanitized_wrapper"] = False
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_como_metodo_sigue_bloqueado_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('obj = { existe: func(ruta) { retorno verdadero } }\nimprimir(obj.existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_hilo_con_primitiva_peligrosa_fuera_de_ruta_canonica_se_bloquea():
    interp = InterpretadorCobra()
    ast = generar_ast('hilo(leer_archivo, "README.md")')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)
