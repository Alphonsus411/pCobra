from copy import deepcopy
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


def test_usar_archivo_existe_imprime_booleano_sin_primitiva_peligrosa():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    salida = out.getvalue().strip()
    assert salida in {"verdadero", "falso"}




def test_usar_numero_es_finito_true_y_texto_carga_ok_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "numero"\nimprimir(es_finito(10))\nusar "texto"\nimprimir(mayusculas("ok"))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    assert "verdadero" in lineas
    assert "OK" in lineas


def test_usar_archivo_existe_readme_no_falla_por_metadata():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    salida = out.getvalue().strip().splitlines()
    assert salida
    assert salida[-1].strip() in {"verdadero", "falso"}
    assert "existe" in interp._usar_symbol_metadata
    assert "existe" in interp._validador._metadata_simbolos_usar


def test_sintaxis_usar_sin_cadena_rechaza_con_error_claro():
    with pytest.raises(Exception, match=r"Se esperaba una ruta de módulo entre comillas"):
        generar_ast('usar archivo')

def test_usar_datos_longitud_builtin_permanece_en_3():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "datos"\nvar xs = [1, 2, 3]\nimprimir(longitud(xs))\nimprimir(longitud([1,2,3]))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    assert lineas[-2:] == ["3", "3"]


def test_existe_backend_crudo_sigue_bloqueado_aun_con_usar_archivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nexiste = leer_archivo\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_regresion_existe_redefinido_local_sigue_bloqueado_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('func existe(ruta) { retorno verdadero }\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_regresion_alias_malicioso_existe_leer_archivo_tras_usar_archivo_se_bloquea():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nexiste = leer_archivo\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_regresion_import_no_publico_se_mantiene_bloqueado_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(leer_archivo("README.md"))')

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
    assert metadata["public_api"] is True
    assert metadata["is_sanitized_wrapper"] is True
    assert metadata["python_module"] in {
        "pcobra.standard_library.archivo",
        "cobra.standard_library.archivo",
    }

    metadata_validador = interp._validador._metadata_simbolos_usar["existe"]
    assert metadata_validador["module"] == "archivo"
    assert metadata_validador["origen_modulo"] == "archivo"
    assert metadata_validador["canonical_module"] == "archivo"
    assert metadata_validador["stable_signature"] == metadata["stable_signature"]


def test_usar_metadata_minima_y_consistente_entre_interprete_y_validador():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"')

    interp.ejecutar_ast(ast)

    requeridos = {
        "origin_kind",
        "module",
        "symbol",
        "sanitized",
        "callable",
        "origen_modulo",
        "exported_name",
        "is_sanitized_wrapper",
        "public_api",
        "backend_exposed",
    }

    for nombre, metadata in interp._usar_symbol_metadata.items():
        faltantes = requeridos - set(metadata.keys())
        assert not faltantes, f"metadata incompleta para {nombre}: {sorted(faltantes)}"
        assert isinstance(metadata, dict)
        assert isinstance(interp._validador._metadata_simbolos_usar[nombre], dict)
        assert metadata["module"] == "archivo"
        assert metadata["origin_kind"] == "usar"
        assert metadata["origen_modulo"] == "archivo"
        assert metadata["symbol"] == nombre
        assert metadata["exported_name"] == nombre
        assert metadata["sanitized"] is True
        assert isinstance(metadata["callable"], bool)
        assert metadata["is_sanitized_wrapper"] is True
        assert metadata["public_api"] is True
        assert metadata["backend_exposed"] is False

        metadata_validador = interp._validador._metadata_simbolos_usar[nombre]
        for clave in ("canonical_module", "origin_module", "callable_id", "stable_signature"):
            assert clave in metadata
            assert clave in metadata_validador
        assert metadata_validador == metadata


def test_roundtrip_metadata_usar_registro_y_sincronizacion_sin_mutaciones():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"')
    interp.ejecutar_ast(ast)

    metadata_original = deepcopy(interp._usar_symbol_metadata)
    metadata_validador_original = deepcopy(interp._validador._metadata_simbolos_usar)

    # Ejecutar una segunda fase para forzar validación/sincronización en runtime.
    interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))

    assert interp._usar_symbol_metadata == metadata_original
    assert interp._validador._metadata_simbolos_usar == metadata_validador_original
    assert interp._usar_symbol_metadata == interp._validador._metadata_simbolos_usar


def test_usar_detecta_divergencia_metadata_interprete_y_validador():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"]["public_api"] = False
    ast_llamada = generar_ast('imprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_ausente_sin_fallback_permisivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    # Simula bypass: símbolo registrado pero metadata ausente.
    interp._validador._metadata_simbolos_usar.pop("existe", None)
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)




def test_existe_rechaza_metadata_no_dict_sin_fallback_permisivo():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"] = []
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

    interp._validador._metadata_simbolos_usar["existe"].pop("introduced_by_usar", None)
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)

@pytest.mark.parametrize("modulo", ["io", "numpy"])
def test_existe_rechaza_metadata_con_modulo_distinto(modulo):
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"]["module"] = modulo
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_con_symbol_distinto():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"]["symbol"] = "leer_archivo"
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast_llamada)


def test_existe_rechaza_metadata_con_public_api_tipo_incorrecto():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"]["public_api"] = "true"
    ast_llamada = generar_ast('imprimir(existe("README.md"))')
    with pytest.raises(PrimitivaPeligrosaError, match="metadata usar inválida: metadata.public_api debe ser True"):
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


def test_usar_numpy_fallo_no_inyecta_estado_parcial_en_contexto():
    interp = InterpretadorCobra()
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match="No se puede usar 'numpy': módulo fuera del catálogo público"):
        interp.ejecutar_ast(generar_ast('usar "numpy"'))

    assert dict(interp.contextos[-1].values) == estado_pre
    assert "numpy" not in interp.contextos[-1].values
    assert "numpy" not in interp.variables


def test_existe_rechaza_metadata_con_sanitized_false():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(ast)

    interp._validador._metadata_simbolos_usar["existe"]["sanitized"] = False
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


def test_regresion_redefinicion_local_existe_permanece_bloqueada_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('func existe(ruta) { retorno verdadero }\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_regresion_alias_malicioso_post_usar_archivo_permanece_bloqueado():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nexiste = leer_archivo\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_regresion_imports_no_publicos_permanece_bloqueado_en_modo_seguro():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(leer_archivo("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_metadata_usar_error_expone_codigo_interno_missing_keys_y_mensaje_claro():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar.pop("existe", None)
    with pytest.raises(PrimitivaPeligrosaError) as err:
        interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "Divergencia de metadata usar entre intérprete y validador" in mensaje
    assert "codigo_interno='missing_keys'" in mensaje
    assert "claves divergentes" in mensaje


def test_metadata_usar_error_debug_agrega_detalle_estructurado():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar["existe"]["sanitized"] = False
    with patch("core.interpreter._usar_detalle_habilitado", return_value=True):
        with pytest.raises(PrimitivaPeligrosaError) as err:
            interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "validator_type" in mensaje
    assert "validate_usar_symbol_metadata" in mensaje
    assert "symbol" in mensaje
    assert "existe" in mensaje


def test_metadata_usar_error_invalid_container_incluye_tipo_y_troubleshooting():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar = []
    with pytest.raises(PrimitivaPeligrosaError) as err:
        interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "codigo_interno='invalid_container'" in mensaje
    assert "tipo='list'" in mensaje
    assert "troubleshooting='container_metadata_debe_ser_dict'" in mensaje


def test_metadata_usar_error_invalid_symbol_metadata_preserva_motivo_original():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar["existe"] = {"module": "archivo", "kind": "callable", "public_api": False, "sanitized": True}
    with pytest.raises(PrimitivaPeligrosaError) as err:
        interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "codigo_interno='invalid_symbol_metadata'" in mensaje
    assert "símbolo 'existe'" in mensaje
    assert "validation_reason='" in mensaje
    assert "troubleshooting='metadata_validador_no_cumple_contrato'" in mensaje


def test_metadata_usar_error_missing_keys_incluye_troubleshooting():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar.pop("existe", None)
    with pytest.raises(PrimitivaPeligrosaError) as err:
        interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "codigo_interno='missing_keys'" in mensaje
    assert "troubleshooting='claves_de_metadata_desincronizadas'" in mensaje


def test_metadata_usar_error_mismatch_payload_incluye_detalle_simbolo_tipo_y_clave():
    interp = InterpretadorCobra()
    with patch("sys.stdout", new_callable=StringIO):
        interp.ejecutar_ast(generar_ast('usar "archivo"\nimprimir(existe("README.md"))'))
    interp._validador._metadata_simbolos_usar["existe"] = dict(interp._validador._metadata_simbolos_usar["existe"])
    interp._validador._metadata_simbolos_usar["existe"]["module"] = "otro_modulo"
    with pytest.raises(PrimitivaPeligrosaError) as err:
        interp.ejecutar_ast(generar_ast('imprimir(existe("README.md"))'))
    mensaje = str(err.value)
    assert "codigo_interno='mismatch_payload'" in mensaje
    assert "símbolo='existe'" in mensaje
    assert "clave_esperada='module|kind|public_api|sanitized'" in mensaje
    assert "tipo='dict'" in mensaje
    assert "troubleshooting='payload_de_metadata_difiere'" in mensaje
