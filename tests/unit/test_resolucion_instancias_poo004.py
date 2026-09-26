"""Pruebas focales de POO-004: instanciación alcanzable desde fuente."""

import logging
from argparse import Namespace
from types import SimpleNamespace

import pcobra.jupyter_kernel as jupyter_kernel
from pcobra.cobra.core import resolucion_instancias
from pcobra.cobra.cli.commands import (
    bench_transpilers_cmd,
    benchthreads_cmd,
    compile_cmd,
    profile_cmd,
)
from pcobra.cobra.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.services import test_service, verification_service
from pcobra.cobra.cli.services.contracts import TestRequest as CobraTestRequest
from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoDel,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoValor,
)
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.core.resolucion_instancias import resolver_instanciaciones
from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.import_utils import cargar_ast_modulo


def _parsear(codigo: str):
    ast_sintactico = Parser(Lexer(codigo).analizar_token()).parsear()
    return resolver_instanciaciones(ast_sintactico)


def _valor_asignado(nodo):
    assert type(nodo) is NodoAsignacion
    return nodo.expresion


def _fallar_si_se_usa_cache(_codigo):
    raise AssertionError("La caché no debe usarse sin una SQLITE_DB_KEY efectiva")


def _ultima_llamada(codigo: str):
    ast = _parsear(codigo)
    llamada = ast[-1]
    if type(llamada) is NodoAsignacion:
        llamada = _valor_asignado(llamada)
    return ast, llamada


def test_del_global_invalida_clase_sin_reemplazarla_por_otro_binding():
    ast, llamada = _ultima_llamada("clase C:\nfin\neliminar C\nC()")

    assert type(ast[1]) is NodoDel
    assert type(llamada) is NodoLlamadaFuncion


def test_procedencia_mixta_con_clase_comun_conserva_binding_visible():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    si condicion:\n"
        "        clase C:\n        fin\n"
        "    sino:\n"
        "        var marcador = 0\n"
        "    fin\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_head_de_merge_no_crea_history_en_el_mismo_environment():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    si condicion:\n"
        "        clase C:\n        fin\n"
        "    sino:\n"
        "        var marcador = 0\n"
        "    fin\n"
        "    var C = 0\n"
        "    eliminar C\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_head_sintetica_de_merge_no_se_hereda_como_ancestry_lexica():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    con recurso:\n"
        "        si condicion:\n"
        "            clase C:\n            fin\n"
        "        sino:\n"
        "            var marcador = 0\n"
        "        fin\n"
        "        func interior():\n"
        "            eliminar C\n"
        "            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_head_sintetica_preserva_ambiguedad_posterior_a_del():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    func C():\n    fin\n"
        "    con recurso:\n"
        "        si condicion:\n"
        "            func C():\n            fin\n"
        "        sino:\n"
        "            var marcador = 0\n"
        "        fin\n"
        "        func interior():\n"
        "            eliminar C\n"
        "            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_fusion_mixta_con_post_del_comun_conserva_tail_real():
    tail = (("clase", "local"),)
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion,
        ({"C": tail}, {"C": tail}),
        bindings_caminos=({"C": "otro"}, {"C": "otro"}),
        alcances_caminos=({"C": "local_propio"}, {"C": "local"}),
        procedencias_caminos=({"C": "local"}, {"C": "exterior"}),
    )

    assert fusion["C"] == tail


def test_fusion_mixta_sin_tail_no_inventa_ancestry():
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion,
        ({}, {}),
        bindings_caminos=({"C": "otro"}, {"C": "otro"}),
        alcances_caminos=({"C": "local_propio"}, {"C": "local"}),
        procedencias_caminos=({"C": "local"}, {"C": "exterior"}),
    )

    assert "C" not in fusion


def test_fusion_mixta_con_heads_alineadas_marca_post_del_ambiguo():
    funcion = (("otro", "local"),)
    clase = (("clase", "global"),)
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion,
        ({"C": (*funcion, *clase)}, {"C": clase}),
        bindings_caminos=({"C": "otro"}, {"C": "otro"}),
        alcances_caminos=({"C": "local_propio"}, {"C": "local"}),
        procedencias_caminos=({"C": "local"}, {"C": "exterior"}),
    )

    assert fusion["C"] == resolucion_instancias._CADENA_EXTERIOR_AMBIGUA


def test_del_preserva_clase_recuperada_con_ownership_distinto():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    con recurso:\n"
        "        si condicion:\n"
        "            clase C:\n            fin\n"
        "        sino:\n"
        "            var marcador = 0\n"
        "        fin\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_fusion_post_del_separa_kind_owner_y_tail():
    fusionar = resolucion_instancias._fusionar_cadenas_post_del
    ambigua = resolucion_instancias._CADENA_EXTERIOR_AMBIGUA

    assert fusionar(((('clase', 'local'),), (('clase', 'global'),))) == (
        ("clase", "alcance_ambiguo"),
    )
    assert fusionar(((('otro', 'local'),), (('otro', 'global'),))) == (
        ("otro", "alcance_ambiguo"),
    )
    assert fusionar(((('clase', 'local'),), (('otro', 'global'),))) == ambigua
    assert fusionar(((('clase', 'local'),), (('ambiguo', 'global'),))) == ambigua
    assert fusionar(((('clase', 'local'),), (('clase', 'local'),))) == (
        ("clase", "local"),
    )
    assert fusionar(
        (
            (("clase", "local"), ("clase", "global")),
            (("clase", "global"), ("otro", "local")),
        )
    ) == (("clase", "alcance_ambiguo"), *ambigua)


def test_fusion_sintetica_conserva_kind_inmediato_sin_inventar_owner():
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion,
        (
            {"C": (("clase", "local"), ("otro", "global"))},
            {"C": (("clase", "global"),)},
        ),
        bindings_caminos=({"C": "clase"}, {"C": "clase"}),
        alcances_caminos=({"C": "local_propio"}, {"C": "local"}),
        procedencias_caminos=({"C": "local"}, {"C": "exterior"}),
    )

    assert fusion["C"] == (
        ("clase", "alcance_ambiguo"),
        *resolucion_instancias._CADENA_EXTERIOR_AMBIGUA,
    )


def test_fusion_sintetica_con_kinds_inmediatos_distintos_es_ambigua():
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion,
        ({"C": (("clase", "local"),)}, {"C": (("otro", "global"),)}),
        bindings_caminos=({"C": "otro"}, {"C": "otro"}),
        alcances_caminos=({"C": "local_propio"}, {"C": "local"}),
        procedencias_caminos=({"C": "local"}, {"C": "exterior"}),
    )

    assert fusion["C"] == resolucion_instancias._CADENA_EXTERIOR_AMBIGUA


def test_descendiente_recupera_ancestry_lexica_real_tras_del():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    func C():\n    fin\n"
        "    func interior():\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_procedencia_mixta_con_estados_distintos_permanece_neutral_tras_del():
    ast = _parsear(
        "func C():\nfin\n"
        "func f():\n"
        "    si condicion:\n"
        "        clase C:\n        fin\n"
        "    sino:\n"
        "        var marcador = 0\n"
        "    fin\n"
        "    var C = 0\n"
        "    eliminar C\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_condicional_en_una_o_ambas_ramas_es_conservador():
    _, una_rama = _ultima_llamada(
        "clase C:\nfin\nsi condicion:\n    eliminar C\nfin\nC()"
    )
    _, ambas_ramas = _ultima_llamada(
        "clase C:\nfin\nsi condicion:\n    eliminar C\nsino:\n    eliminar C\nfin\nC()"
    )

    assert type(una_rama) is NodoLlamadaFuncion
    assert type(ambas_ramas) is NodoLlamadaFuncion


def test_del_en_bucles_conserva_camino_de_cero_iteraciones():
    _, mientras = _ultima_llamada(
        "clase C:\nfin\nmientras condicion:\n    eliminar C\nfin\nC()"
    )
    _, para = _ultima_llamada(
        "clase C:\nfin\npara elemento en []:\n    eliminar C\nfin\nC()"
    )

    assert type(mientras) is NodoLlamadaFuncion
    assert type(para) is NodoLlamadaFuncion


def test_del_en_ambas_ramas_consume_la_misma_capa_exterior():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior(C):\n"
        "        si condicion:\n            eliminar C\n"
        "        sino:\n            eliminar C\n        fin\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_fusion_exterior_normaliza_ausencia_y_cadena_vacia():
    fusion = {"C": ()}

    resolucion_instancias._fusionar_bindings_exteriores(fusion, ({}, {"C": ()}))

    assert "C" not in fusion


def test_fusion_exterior_conserva_ambiguedad_real_y_cadenas_distintas():
    capa_a = (("clase", "local"),)
    capa_b = (("otro", "local"),)
    cadena_a_b = (*capa_a, *capa_b)
    casos = [
        ({}, {"C": capa_a}),
        ({"C": cadena_a_b}, {"C": capa_b}),
    ]

    for camino_a, camino_b in casos:
        fusion = {}
        resolucion_instancias._fusionar_bindings_exteriores(
            fusion, (camino_a, camino_b)
        )

        assert fusion["C"] == resolucion_instancias._CADENA_EXTERIOR_AMBIGUA


def test_fusion_exterior_conserva_cadenas_iguales():
    cadena = (("clase", "local"),)
    fusion = {}

    resolucion_instancias._fusionar_bindings_exteriores(
        fusion, ({"C": cadena}, {"C": cadena})
    )

    assert fusion["C"] == cadena


def test_cadena_vacia_fusionada_no_recarga_global_eliminado():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    si condicion:\n"
        "        func C():\n        fin\n"
        "        eliminar C\n"
        "    fin\n"
        "    eliminar C\n"
        "    global C\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_en_una_rama_deja_ambigua_la_cadena_exterior():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior(C):\n"
        "        si condicion:\n            eliminar C\n        fin\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_a_distinta_profundidad_no_elige_una_cadena_exterior():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior(C):\n"
        "        si condicion:\n            eliminar C\n"
        "        sino:\n            eliminar C\n            eliminar C\n        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_en_mientras_fusiona_cero_iteraciones_con_una_iteracion():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior(C):\n"
        "        mientras condicion:\n            eliminar C\n        fin\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_en_para_fusiona_cero_iteraciones_con_una_iteracion():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior(C):\n"
        "        para elemento en valores:\n            eliminar C\n        fin\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_local_de_funcion_invalida_clase_local():
    ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n    eliminar C\n    C()\nfin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_desde_con_y_alias_no_materializado_eliminan_binding_exterior():
    ast = _parsear(
        "clase C:\nfin\ncon recurso:\n    eliminar C\nfin\nC()"
    )
    alias = _parsear(
        "clase C:\nfin\ncon recurso como C:\n    eliminar C\nfin\nC()"
    )

    assert type(ast[-1]) is NodoLlamadaFuncion
    assert type(alias[-1]) is NodoLlamadaFuncion


def test_del_local_reexpone_clase_exterior():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n    var C = otra\n    eliminar C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_del_parametro_reexpone_clase_exterior():
    ast = _parsear(
        "clase C:\nfin\nfunc f(C):\n    eliminar C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_del_parametro_sin_exterior_no_inventa_clase():
    ast = _parsear("func f(C):\n    eliminar C\n    C()\nfin")

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_parametro_reexpone_funcion_exterior_como_llamada():
    ast = _parsear(
        "func C():\nfin\nfunc f(C):\n    eliminar C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_dos_del_avanzan_de_parametro_a_clase_exterior_y_funcion_global():
    ast = _parsear(
        "func C():\nfin\nfunc exterior():\n    clase C:\n    fin\n"
        "    func interior(C):\n        eliminar C\n        eliminar C\n"
        "        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[-1].cuerpo[-1]) is NodoLlamadaFuncion


def test_tres_del_avanzan_por_toda_la_cadena_de_bindings_lexicos():
    ast = _parsear(
        "func C():\nfin\nfunc nivel_uno():\n    clase C:\n    fin\n"
        "    func nivel_dos():\n        clase C:\n        fin\n"
        "        func nivel_tres(C):\n            eliminar C\n"
        "            eliminar C\n            eliminar C\n            C()\n"
        "        fin\n    fin\nfin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_del_parametro_no_inicial_reexpone_clase_exterior():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f(x, C, y):\n    eliminar C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_del_parametro_de_metodo_reexpone_clase_sin_afectar_receptor():
    ast = _parsear(
        "clase C:\nfin\nclase Contenedor:\n"
        "    metodo crear(este, C):\n        eliminar C\n        C()\n    fin\n"
        "fin"
    )

    assert ast[1].metodos[0].parametros == ["este", "C"]
    assert type(ast[1].metodos[0].cuerpo[-1]) is NodoInstancia


def test_del_condicional_de_parametro_es_conservador():
    ast = _parsear(
        "clase C:\nfin\nfunc f(C):\n"
        "    si condicion:\n        eliminar C\n    fin\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_redeclaracion_tras_del_parametro_reemplaza_estado_eliminado():
    ast = _parsear(
        "clase C:\nfin\nfunc f(C):\n"
        "    eliminar C\n    clase C:\n    fin\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_target_para_nuevo_eliminado_no_inventa_clase():
    ast = _parsear(
        "func f():\n    para C en valores:\n"
        "        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(ast[0].cuerpo[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_target_para_existente_no_restaura_clase_sobrescrita():
    ast = _parsear(
        "clase C:\nfin\nfunc f():\n    para C en valores:\n"
        "        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_target_para_existente_sobre_funcion_permanece_llamada():
    ast = _parsear(
        "func C():\nfin\nfunc f():\n    para C en valores:\n"
        "        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_target_para_distinto_no_afecta_clase_visible():
    ast = _parsear(
        "clase C:\nfin\nfunc f():\n    para x en valores:\n"
        "        eliminar x\n        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[0].cuerpo[-1]) is NodoInstancia


def test_del_condicional_del_target_para_es_conservador():
    ast = _parsear(
        "clase C:\nfin\nfunc f():\n    para C en valores:\n"
        "        si condicion:\n            eliminar C\n        fin\n"
        "        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_target_para_sobrescribe_clase_local_sin_restaurarla():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    para C en valores:\n"
        "        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(ast[0].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_target_para_sombrea_clase_de_funcion_exterior_y_del_la_reexpone():
    ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n    func interior():\n"
        "        para C en valores:\n            eliminar C\n            C()\n"
        "        fin\n    fin\nfin"
    )

    llamada = ast[0].cuerpo[-1].cuerpo[0].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_target_para_tras_del_parametro_reexpone_clase_de_funcion_exterior():
    ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n    func interior(C):\n"
        "        eliminar C\n        para C en valores:\n"
        "            eliminar C\n            C()\n        fin\n    fin\nfin"
    )

    llamada = ast[0].cuerpo[-1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_target_para_preserva_ownership_ambiguo_tras_global_condicional():
    ast = _parsear(
        "clase C:\nfin\nfunc exterior():\n    clase C:\n    fin\n"
        "    func interior():\n        si condicion:\n            global C\n"
        "        fin\n        para C en valores:\n            eliminar C\n"
        "            C()\n        fin\n    fin\nfin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_target_para_enclosing_funcion_reexpone_funcion_tras_del():
    ast = _parsear(
        "func exterior():\n    func C():\n    fin\n    func interior():\n"
        "        para C en valores:\n            eliminar C\n            C()\n"
        "        fin\n    fin\nfin"
    )

    llamada = ast[0].cuerpo[-1].cuerpo[0].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_target_para_nolocal_y_global_no_crean_shadow_local():
    nolocal_ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n    func interior():\n"
        "        nolocal C\n        para C en valores:\n            eliminar C\n"
        "            C()\n        fin\n    fin\nfin"
    )
    global_ast = _parsear(
        "clase C:\nfin\nfunc f():\n    global C\n    para C en valores:\n"
        "        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(nolocal_ast[0].cuerpo[-1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion
    assert type(global_ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_condicional_del_target_local_enclosing_es_conservador():
    ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n    func interior():\n"
        "        para C en valores:\n            si condicion:\n"
        "                eliminar C\n            fin\n            C()\n"
        "        fin\n    fin\nfin"
    )

    llamada = ast[0].cuerpo[-1].cuerpo[0].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_redeclaracion_tras_reexposicion_crea_nuevo_binding_local():
    ast = _parsear(
        "clase C:\nfin\nfunc f(C):\n    eliminar C\n    clase C:\n    fin\n"
        "    eliminar C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_redeclaracion_variable_mismo_scope_no_reexpone_clase_sobrescrita():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    var C = otra\n"
        "    eliminar C\n    C()\nfin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_redeclaracion_funcion_mismo_scope_no_reexpone_clase_sobrescrita():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    func C():\n    fin\n"
        "    eliminar C\n    C()\nfin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_clase_en_con_reexpone_clase_del_environment_padre_tras_del():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    con recurso:\n"
        "        clase C:\n        fin\n        eliminar C\n        C()\n"
        "    fin\nfin"
    )

    assert type(ast[0].cuerpo[-1].cuerpo[-1]) is NodoInstancia


def test_variable_en_con_reexpone_clase_del_environment_padre_tras_del():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    con recurso:\n"
        "        var C = otra\n        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(ast[0].cuerpo[-1].cuerpo[-1]) is NodoInstancia


def test_con_anidado_reexpone_cada_capa_lexica_tras_del():
    ast = _parsear(
        "func f():\n    clase C:\n    fin\n    con exterior:\n"
        "        clase C:\n        fin\n        con interior:\n"
        "            var C = otra\n            eliminar C\n            C()\n"
        "        fin\n        eliminar C\n        C()\n    fin\nfin"
    )

    con_exterior = ast[0].cuerpo[-1]
    assert type(con_exterior.cuerpo[1].cuerpo[-1]) is NodoInstancia
    assert type(con_exterior.cuerpo[-1]) is NodoInstancia


def test_dos_del_en_con_reexponen_clase_global_tras_clase_padre():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    clase C:\n    fin\n"
        "    con recurso:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        eliminar C\n        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1].cuerpo[-1]) is NodoInstancia


def test_tres_del_en_con_recorren_toda_la_cadena_de_clases():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        clase C:\n        fin\n"
        "        con recurso:\n"
        "            clase C:\n            fin\n"
        "            eliminar C\n            eliminar C\n"
        "            eliminar C\n            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_dos_del_en_con_reexponen_funcion_global_tras_clase_padre():
    ast = _parsear(
        "func C():\nfin\n"
        "func f():\n"
        "    clase C:\n    fin\n"
        "    con recurso:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        eliminar C\n        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1].cuerpo[-1]) is NodoLlamadaFuncion


def test_dos_del_en_con_atraviesan_variable_hasta_clase_global():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    var C = otra\n"
        "    con recurso:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        eliminar C\n        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1].cuerpo[-1]) is NodoInstancia


def test_con_no_concretiza_cadena_exterior_ambigua_heredada():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    clase C:\n    fin\n"
        "    si condicion:\n        eliminar C\n    fin\n"
        "    con recurso:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        eliminar C\n        C()\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_global_y_nolocal_invalidan_binding_dirigido():
    global_ast = _parsear(
        "clase C:\nfin\nfunc f():\n    global C\n    eliminar C\n    C()\nfin"
    )
    nolocal_ast = _parsear(
        "func exterior():\n    clase C:\n    fin\n"
        "    func interior():\n        nolocal C\n        eliminar C\n        C()\n    fin\nfin"
    )

    assert type(global_ast[1].cuerpo[-1]) is NodoLlamadaFuncion
    assert type(nolocal_ast[0].cuerpo[-1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_inexistente_no_inventa_binding_y_redeclaraciones_lo_reemplazan():
    _, inexistente = _ultima_llamada("eliminar X\nX()")
    _, redeclarada = _ultima_llamada(
        "clase C:\nfin\neliminar C\nclase C:\nfin\nC()"
    )
    _, asignada = _ultima_llamada(
        "clase C:\nfin\neliminar C\nvar C = f\nC()"
    )

    assert type(inexistente) is NodoLlamadaFuncion
    assert type(redeclarada) is NodoInstancia
    assert type(asignada) is NodoLlamadaFuncion


def test_del_preserva_identidad_ast_y_memoizacion_del_objetivo():
    ast_sintactico = Parser(Lexer("clase C:\nfin\neliminar C").analizar_token()).parsear()
    nodo_del = ast_sintactico[1]
    objetivo = nodo_del.objetivo

    resuelto = resolver_instanciaciones(ast_sintactico)

    assert resuelto[1] is nodo_del
    assert resuelto[1].objetivo is objetivo


def test_parser_puro_conserva_llamada_sintactica():
    ast = Parser(
        Lexer("clase Persona:\nfin\nvar persona = Persona()").analizar_token()
    ).parsear()

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_frontera_publica_sin_variable_sqlite_devuelve_instancia(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr("pcobra.core.ast_cache.obtener_ast", _fallar_si_se_usa_cache)

    ast = parsear_codigo_resuelto(
        "clase Persona:\nfin\nvar persona = Persona()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_frontera_publica_con_clave_sqlite_vacia_devuelve_instancia(monkeypatch):
    monkeypatch.setenv("SQLITE_DB_KEY", "")
    monkeypatch.setattr("pcobra.core.ast_cache.obtener_ast", _fallar_si_se_usa_cache)

    ast = parsear_codigo_resuelto(
        "clase Persona:\nfin\nvar persona = Persona()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_frontera_publica_con_clave_sqlite_blanca_devuelve_instancia(monkeypatch):
    monkeypatch.setenv("SQLITE_DB_KEY", "   ")
    monkeypatch.setattr("pcobra.core.ast_cache.obtener_ast", _fallar_si_se_usa_cache)

    ast = parsear_codigo_resuelto(
        "clase Persona:\nfin\nvar persona = Persona()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_frontera_publica_con_clave_sqlite_real_usa_cache(monkeypatch):
    ast_cacheado = [object()]
    monkeypatch.setenv("SQLITE_DB_KEY", "clave-valida")
    monkeypatch.setattr(
        "pcobra.core.ast_cache.obtener_ast", lambda _codigo: ast_cacheado
    )

    ast = parsear_codigo_resuelto(
        "clase Persona:\nfin\nvar persona = Persona()"
    )

    assert ast is ast_cacheado


def test_jupyter_entrega_ast_resuelto_al_interprete(monkeypatch):
    capturado = {}

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    kernel = SimpleNamespace(
        _lexer_cls=Lexer,
        _parser_cls=Parser,
        _get_suggestions=lambda: [],
        interpreter=Interprete(),
        use_python=False,
        execution_count=1,
    )
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)

    resultado = jupyter_kernel.CobraKernel.do_execute(
        kernel,
        "clase Persona:\nfin\nvar persona = Persona()",
        silent=True,
    )

    assert resultado["status"] == "ok"
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_profile_entrega_ast_resuelto_al_interprete(
    tmp_path, monkeypatch, capsys
):
    capturado = {}
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(profile_cmd, "validar_dependencias", lambda *_args: None)
    monkeypatch.setattr(
        profile_cmd,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )

    resultado = profile_cmd.ProfileCommand().run(
        Namespace(
            archivo=str(archivo),
            output=None,
            ui=None,
            depurar=False,
            formatear=False,
            seguro=False,
            extra_validators=None,
            analysis=True,
        )
    )

    assert resultado == 0
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia
    salida = capsys.readouterr().out
    assert "Parser profile" in salida


def test_benchthreads_entrega_ast_resuelto_al_interprete(tmp_path, monkeypatch):
    capturado = {}
    archivo = tmp_path / "sequential.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(benchthreads_cmd, "SEQUENTIAL_CODE", archivo)
    monkeypatch.setattr(
        benchthreads_cmd,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )

    benchthreads_cmd.BenchThreadsCommand()._run_sequential()

    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_test_service_entrega_ast_resuelto_a_runtime_y_transpilacion(monkeypatch):
    capturados = []
    codigo = "clase Persona:\nfin\nvar persona = Persona()"

    class Interprete:
        def ejecutar_ast(self, ast):
            capturados.append(ast)

    servicio = test_service.TestService.__new__(test_service.TestService)
    servicio._interprete = Interprete()
    servicio._logger = logging.getLogger(__name__)
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(servicio, "read_source_file", lambda _archivo: codigo)
    monkeypatch.setattr(
        servicio,
        "verify_language",
        lambda _lang, ast, _esperado: (capturados.append(ast) or ("python", None)),
    )

    resultado = servicio.run(CobraTestRequest("persona.cobra", ["python"]))

    assert resultado == 0
    assert len(capturados) == 2
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_verification_service_entrega_ast_resuelto_a_runtime_y_transpilacion(
    tmp_path, monkeypatch
):
    capturados = []
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturados.append(ast)

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(
        verification_service,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )
    monkeypatch.setattr(
        verification_service,
        "_compile_and_execute",
        lambda ast, _lang: (capturados.append(ast) or ("", None)),
    )

    resultado = verification_service.execute_runtime_verification(
        str(archivo), ["python"]
    )

    assert resultado == 0
    assert len(capturados) == 2
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_compile_sin_sqlite_alcanza_transpilacion_con_ast_resuelto(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("SQLITE_DB_KEY", "")
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )
    capturado = {}

    monkeypatch.setattr(compile_cmd, "validar_politica_modo", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(compile_cmd, "cli_transpilers", lambda: {"python": object})
    monkeypatch.setattr(compile_cmd, "cli_plugin_transpilers", lambda: {})
    monkeypatch.setattr(compile_cmd, "cli_toml_map", lambda: {})
    monkeypatch.setattr(
        compile_cmd, "validar_dependencias_con_alias", lambda *_args: None
    )
    monkeypatch.setattr(
        compile_cmd.backend_pipeline,
        "resolve_backend_runtime",
        lambda *_args, **_kwargs: (SimpleNamespace(backend="python"), {}),
    )
    monkeypatch.setattr(
        compile_cmd,
        "_transpile_with_pipeline_or_plugin",
        lambda ast, *_args, **_kwargs: capturado.setdefault("ast", ast) or "ok",
    )

    assert CompileCommand.requires_sqlite_key is False
    resultado = CompileCommand().run(
        SimpleNamespace(
            archivo=str(archivo),
            tipo="python",
            backend=None,
            tipos=None,
            modo="mixto",
        )
    )

    assert resultado == 0
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_benchtranspilers_sin_sqlite_alcanza_transpilacion_con_ast_resuelto(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("SQLITE_DB_KEY", "")
    codigo = "clase Persona:\nfin\nvar persona = Persona()"
    capturados = []
    for size in bench_transpilers_cmd.VALID_SIZES:
        (tmp_path / f"{size}.cobra").write_text(codigo, encoding="utf-8")

    class Transpilador:
        def generate_code(self, ast):
            capturados.append(ast)
            return "ok"

    monkeypatch.setattr(bench_transpilers_cmd, "PROGRAM_DIR", tmp_path)
    monkeypatch.setattr(
        bench_transpilers_cmd, "cli_transpilers", lambda: {"python": Transpilador}
    )

    assert BenchTranspilersCommand.requires_sqlite_key is False
    resultado = BenchTranspilersCommand().run(
        SimpleNamespace(output=None, profile=False, perfil="publico")
    )

    assert resultado == 0
    assert len(capturados) == len(bench_transpilers_cmd.VALID_SIZES)
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_parser_incremental_conserva_contrato_sintactico(
    monkeypatch, base_datos_temporal
):
    codigo = "clase Persona:\nfin\nvar persona = Persona()"
    tokens = Lexer(codigo).analizar_token()

    ast = Parser(tokens).parsear(incremental=True)

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_carga_modulo_usa_ast_resuelto(tmp_path):
    modulo = tmp_path / "persona.cobra"
    modulo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    ast = cargar_ast_modulo(
        str(modulo), modules_path=str(tmp_path), whitelist={str(tmp_path)}
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_clase_sin_argumentos_produce_instancia():
    ast = _parsear("clase Vacia:\nfin\nvar x = Vacia()")

    assert type(ast[0]) is NodoClase
    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Vacia"
    assert instancia.argumentos == []


def test_clase_con_un_argumento_preserva_valor_y_tipo():
    ast = _parsear(
        'clase Persona:\n'
        '    metodo inicializar(este, nombre):\n'
        '        imprimir nombre\n'
        'fin\n'
        'var persona = Persona("Adolfo")'
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Persona"
    assert len(instancia.argumentos) == 1
    assert type(instancia.argumentos[0]) is NodoValor
    assert instancia.argumentos[0].valor == "Adolfo"


def test_clase_con_varios_argumentos_preserva_orden_y_tipos():
    ast = _parsear(
        "clase Punto:\n"
        "    metodo inicializar(este, x, y):\n"
        "        imprimir x\n"
        "fin\n"
        "var p = Punto(1, 2)"
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Punto"
    assert [type(arg) for arg in instancia.argumentos] == [NodoValor, NodoValor]
    assert [arg.valor for arg in instancia.argumentos] == [1, 2]


def test_funcion_normal_permanece_llamada_funcion():
    ast = _parsear(
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        "var resultado = procesar(1)"
    )

    llamada = _valor_asignado(ast[1])
    assert type(llamada) is NodoLlamadaFuncion
    assert llamada.nombre == "procesar"
    assert type(llamada.argumentos[0]) is NodoValor


def test_clase_y_funcion_resuelven_cada_nombre_a_su_nodo():
    ast = _parsear(
        "clase Persona:\nfin\n"
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        'var resultado = procesar("Adolfo")'
    )

    assert type(_valor_asignado(ast[2])) is NodoInstancia
    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_instancia_y_llamada_postfix_son_expresiones_distintas():
    ast = _parsear(
        "clase Persona:\n"
        "    metodo saludar(este):\n"
        '        imprimir "Hola"\n'
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        "persona.saludar()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia
    llamada = ast[2]
    assert type(llamada) is NodoLlamadaMetodo
    assert type(llamada.objeto) is NodoIdentificador
    assert llamada.objeto.nombre == "persona"
    assert llamada.nombre_metodo == "saludar"
    assert llamada.argumentos == []


def test_referencia_hacia_delante_no_se_resuelve_como_instancia():
    ast = _parsear("var x = Posterior()\nclase Posterior:\nfin")

    assert type(_valor_asignado(ast[0])) is NodoLlamadaFuncion


def test_colision_clase_funcion_no_inventa_precedencia():
    ast = _parsear(
        "clase Duplicado:\nfin\n"
        "func Duplicado():\n"
        "    retornar 1\n"
        "fin\n"
        "var x = Duplicado()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_asignacion_posterior_sombrea_clase_visible():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    retornar 1\n"
        "fin\n"
        "var C = f\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_parametro_sombrea_clase_externa_dentro_de_funcion():
    ast = _parsear(
        "clase C:\nfin\n"
        "func probar(C):\n"
        "    retornar C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1]) is NodoLlamadaFuncion


def test_asignacion_local_sombrea_clase_externa_dentro_de_funcion():
    ast = _parsear(
        "clase C:\nfin\n"
        "func probar():\n"
        "    var C = otra\n"
        "    retornar C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[2]) is NodoLlamadaFuncion


def test_clase_de_bloque_condicional_no_se_asume_ejecutada():
    ast = _parsear(
        "si verdadero:\n"
        "    clase C:\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_clase_de_bucle_no_se_asume_ejecutada():
    ast = _parsear(
        "mientras falso:\n"
        "    clase C:\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_variable_de_bucle_sombrea_clase_solo_en_el_camino_iterado():
    ast = _parsear(
        "clase C:\n"
        "fin\n"
        "para C en [1]:\n"
        "    C()\n"
        "fin\n"
        "var x = C()"
    )

    assert type(ast[1].cuerpo[0]) is NodoLlamadaFuncion
    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_if_con_shadowing_condicional_deja_binding_ambiguo():
    ast = _parsear(
        "clase C:\nfin\n"
        "si falso:\n"
        "    var C = 0\n"
        "fin\n"
        "var x = C()"
    )

    # El resolver no hace constant folding: considera ejecutada y no ejecutada.
    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_ambas_ramas_con_la_misma_clase_conservan_binding_seguro():
    ast = _parsear(
        "si condicion:\n"
        "    clase C:\n"
        "    fin\n"
        "sino:\n"
        "    clase C:\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_while_con_shadowing_no_asume_una_iteracion():
    ast = _parsear(
        "clase C:\nfin\n"
        "mientras condicion:\n"
        "    var C = 0\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_para_con_shadowing_no_asume_una_iteracion():
    ast = _parsear(
        "clase C:\nfin\n"
        "para elemento en []:\n"
        "    var C = 0\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_con_alcance_global_o_local_condicional_propaga_efecto_ambiguo():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    si condicion:\n"
        "        var C = 0\n"
        "    fin\n"
        "    C = f\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_clase_global_en_ambas_ramas_permite_write_externo_posterior():
    ast = _parsear(
        "si condicion:\n"
        "    clase C:\n"
        "    fin\n"
        "sino:\n"
        "    clase C:\n"
        "    fin\n"
        "fin\n"
        "con recurso:\n"
        "    C = f\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_fusiona_rama_local_y_rama_global_como_alcance_ambiguo():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    si condicion:\n"
        "        var C = 0\n"
        "    sino:\n"
        "        C = f\n"
        "    fin\n"
        "    C = f\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_no_inventa_global_ante_declaracion_local_condicional():
    ast = _parsear(
        "con recurso:\n"
        "    si condicion:\n"
        "        var X = 1\n"
        "    fin\n"
        "    X = f\n"
        "fin\n"
        "var resultado = X()"
    )

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_con_con_while_de_alcance_ambiguo_conserva_posible_write_global():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    mientras condicion:\n"
        "        var C = 0\n"
        "    fin\n"
        "    C = f\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_con_para_de_alcance_ambiguo_conserva_posible_write_global():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    para elemento en [1]:\n"
        "        var C = 0\n"
        "    fin\n"
        "    C = f\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_shadowing_interno_de_con_no_escapa():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    var C = 0\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoInstancia


def test_asignacion_externa_en_con_persiste_fuera():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    retornar 1\n"
        "fin\n"
        "con recurso:\n"
        "    C = f\n"
        "    C()\n"
        "fin\n"
        "var x = C()"
    )

    assert type(ast[2].cuerpo[1]) is NodoLlamadaFuncion
    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_con_propaga_asignacion_externa_si_ambas_ramas_escriben():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    retornar 1\n"
        "fin\n"
        "con recurso:\n"
        "    si condicion:\n"
        "        C = f\n"
        "    sino:\n"
        "        C = f\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_con_deja_ambiguo_write_externo_de_una_sola_rama():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    si condicion:\n"
        "        C = f\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_deja_ambiguo_write_externo_dentro_de_mientras():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    mientras condicion:\n"
        "        C = f\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_deja_ambiguo_write_externo_dentro_de_para():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    para elemento en [1]:\n"
        "        C = f\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_anidado_propaga_write_hasta_binding_global():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso1:\n"
        "    con recurso2:\n"
        "        C = f\n"
        "    fin\n"
        "fin\n"
        "var x = C()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_con_en_funcion_no_reemplaza_clase_local_de_funcion():
    ast = _parsear(
        "func probar():\n"
        "    clase C:\n"
        "    fin\n"
        "    con recurso:\n"
        "        C = f\n"
        "    fin\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoInstancia


def test_con_anidado_no_reemplaza_clase_local_de_funcion():
    ast = _parsear(
        "func probar():\n"
        "    clase C:\n"
        "    fin\n"
        "    con recurso1:\n"
        "        con recurso2:\n"
        "            C = f\n"
        "        fin\n"
        "    fin\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoInstancia


def test_nolocal_reemplaza_binding_exterior_sin_con():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        nolocal C\n"
        "        C = f\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_propaga_write_al_salir_de_con():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        nolocal C\n"
        "        con recurso:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_propaga_write_a_traves_de_con_anidados():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        nolocal C\n"
        "        con uno:\n"
        "            con dos:\n"
        "                C = f\n"
        "            fin\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_declarado_en_con_persiste_para_con_hermano():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        con uno:\n"
        "            nolocal C\n"
        "        fin\n"
        "        con dos:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_declarado_en_con_anidado_persiste_fuera_de_ambos():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        con uno:\n"
        "            con dos:\n"
        "                nolocal C\n"
        "            fin\n"
        "        fin\n"
        "        con tres:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_declarado_y_escrito_dentro_del_mismo_con_persiste():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            nolocal C\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_declarado_condicionalmente_en_con_no_es_inequivoco():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n"
        "                nolocal C\n"
        "            fin\n"
        "        fin\n"
        "        con escritura:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_declarado_en_loop_dentro_de_con_conserva_cero_iteraciones():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            mientras condicion:\n"
        "                nolocal C\n"
        "            fin\n"
        "        fin\n"
        "        con escritura:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_con_condicional_con_nolocal_conserva_camino_sin_declaracion():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        si condicion:\n"
        "            con recurso:\n"
        "                nolocal C\n"
        "            fin\n"
        "        fin\n"
        "        con escritura:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_condicional_en_con_deja_binding_ambiguo():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        nolocal C\n"
        "        con recurso:\n"
        "            si condicion:\n"
        "                C = f\n"
        "            fin\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_en_bucle_conserva_camino_de_cero_iteraciones():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "    fin\n"
        "    func interior():\n"
        "        nolocal C\n"
        "        mientras condicion:\n"
        "            C = f\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[1]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_nolocal_sin_binding_exterior_no_inventa_alcance():
    ast = _parsear(
        "func exterior():\n"
        "    func interior():\n"
        "        nolocal X\n"
        "        con recurso:\n"
        "            X = f\n"
        "        fin\n"
        "        X()\n"
        "    fin\n"
        "fin"
    )

    interior = ast[0].cuerpo[0]
    assert type(interior.cuerpo[-1]) is NodoLlamadaFuncion


def test_asignacion_de_nombre_nuevo_en_con_no_escapa():
    ast = _parsear(
        "func f():\n"
        "    retornar 1\n"
        "fin\n"
        "con recurso:\n"
        "    X = f\n"
        "fin\n"
        "var x = X()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion


def test_alias_de_con_es_local_y_no_sombrea_binding_exterior():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso como C:\n"
        "    C()\n"
        "fin\n"
        "var x = C()"
    )

    assert type(ast[1].cuerpo[0]) is NodoLlamadaFuncion
    assert type(_valor_asignado(ast[2])) is NodoInstancia


def test_shadowing_local_de_con_afecta_llamada_interna_pero_no_externa():
    ast = _parsear(
        "clase C:\nfin\n"
        "con recurso:\n"
        "    var C = 0\n"
        "    C()\n"
        "fin\n"
        "var x = C()"
    )

    assert type(ast[1].cuerpo[1]) is NodoLlamadaFuncion
    assert type(_valor_asignado(ast[2])) is NodoInstancia


def test_clase_local_de_con_no_escapa():
    ast = _parsear(
        "con recurso:\n"
        "    clase Local:\n"
        "    fin\n"
        "fin\n"
        "var x = Local()"
    )

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_clase_local_de_funcion_no_escapa_al_ambito_externo():
    ast = _parsear(
        "func crear():\n"
        "    clase Local:\n"
        "    fin\n"
        "fin\n"
        "var x = Local()"
    )

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_resolucion_preserva_identidad_de_aliases_de_asignacion():
    ast = Parser(
        Lexer("clase C:\nfin\nvar x = C()").analizar_token()
    ).parsear()
    asignacion = ast[1]
    assert asignacion.valor is asignacion.expresion

    resolver_instanciaciones(ast)

    assert asignacion.valor is asignacion.expresion
    assert type(asignacion.valor) is NodoInstancia


def test_global_recupera_funcion_raiz_oculta_por_clase_exterior():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n        global C\n        C()\n    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_sin_binding_raiz_no_resucita_cadena_lexica_en_con():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func intermedia():\n"
        "        func C():\n        fin\n"
        "        func interior():\n"
        "            global C\n"
        "            con recurso:\n"
        "                clase C:\n                fin\n"
        "                eliminar C\n"
        "                C()\n"
        "            fin\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[0].cuerpo[1].cuerpo[1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_global_existente_no_deja_cadena_lexica_detras_en_con():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func intermedia():\n"
        "        clase C:\n        fin\n"
        "        func interior():\n"
        "            global C\n"
        "            con recurso:\n"
        "                clase C:\n                fin\n"
        "                eliminar C\n"
        "                C()\n"
        "                eliminar C\n"
        "                C()\n"
        "            fin\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    cuerpo_con = ast[1].cuerpo[1].cuerpo[1].cuerpo[-1].cuerpo
    assert type(cuerpo_con[-3]) is NodoLlamadaFuncion
    assert type(cuerpo_con[-1]) is NodoLlamadaFuncion


def test_metodo_con_global_instancia_su_clase_raiz_actual():
    ast = _parsear(
        "clase C:\n"
        "    metodo crear(este):\n        global C\n        C()\n    fin\n"
        "fin"
    )

    assert type(ast[0].metodos[0].cuerpo[-1]) is NodoInstancia


def test_dos_metodos_con_global_instancian_su_clase_raiz_actual():
    ast = _parsear(
        "clase C:\n"
        "    metodo uno(este):\n        global C\n        C()\n    fin\n"
        "    metodo dos(este):\n        global C\n        C()\n    fin\n"
        "fin"
    )

    assert all(type(metodo.cuerpo[-1]) is NodoInstancia for metodo in ast[0].metodos)


def test_clase_local_no_se_registra_como_binding_global():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n"
        "        metodo crear(este):\n"
        "            global C\n"
        "            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    assert type(ast[0].cuerpo[0].metodos[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_clase_raiz_ambigua_no_se_registra_como_clase_inequivoca():
    ast = _parsear(
        "func C():\nfin\n"
        "clase C:\n"
        "    metodo crear(este):\n        global C\n        C()\n    fin\n"
        "fin"
    )

    assert type(ast[1].metodos[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_selecciona_clase_raiz():
    ast = _parsear(
        "clase C:\nfin\nfunc interior():\n    global C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_global_selecciona_funcion_raiz():
    ast = _parsear(
        "func C():\nfin\nfunc interior():\n    global C\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_recupera_clase_raiz_oculta_por_binding_exterior():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    var C = f\n"
        "    func interior():\n        global C\n        C()\n    fin\n"
        "fin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoInstancia


def test_escritura_posterior_a_global_invalida_clase_raiz():
    ast = _parsear(
        "clase C:\nfin\n"
        "func interior():\n    global C\n    C = f\n    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_declarado_y_escrito_en_con_persiste_fuera():
    ast = _parsear(
        "clase C:\nfin\n"
        "func interior():\n"
        "    con recurso:\n        global C\n        C = f\n    fin\n"
        "    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_en_con_persiste_para_escritura_en_con_hermano():
    ast = _parsear(
        "clase C:\nfin\n"
        "func interior():\n"
        "    con uno:\n        global C\n    fin\n"
        "    con dos:\n        C = f\n    fin\n"
        "    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_en_con_invalida_ancestry_para_con_hermano():
    ast = _parsear(
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func intermedia():\n"
        "        func C():\n        fin\n"
        "        func interior():\n"
        "            con uno:\n                global C\n            fin\n"
        "            con dos:\n"
        "                clase C:\n                fin\n"
        "                eliminar C\n                C()\n"
        "            fin\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[0].cuerpo[1].cuerpo[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_global_existente_en_con_prevalece_en_con_hermano():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con uno:\n            global C\n        fin\n"
        "        con dos:\n"
        "            clase C:\n            fin\n"
        "            eliminar C\n            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_global_condicional_en_con_propaga_ancestry_ambigua_al_hermano():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con uno:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        con dos:\n"
        "            clase C:\n            fin\n"
        "            eliminar C\n            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_global_condicional_en_con_preserva_binding_clase_compartido():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_shadow_conserva_clase_conocida_sobre_ancestry_ambigua():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        var C = f\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoInstancia


def test_redeclaracion_local_no_recupera_head_del_mismo_environment():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    func C():\n    fin\n"
        "    func interior():\n"
        "        si condicion:\n"
        "            clase C:\n            fin\n"
        "        sino:\n"
        "            global C\n"
        "        fin\n"
        "        var C = 0\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_segundo_del_penetra_en_tail_ambigua_bajo_head_conocida():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        var C = f\n"
        "        eliminar C\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_multiples_heads_conocidas_se_consumen_antes_de_tail_ambigua():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        func capa_uno():\n"
        "            clase C:\n            fin\n"
        "            func capa_dos():\n"
        "                var C = f\n"
        "                eliminar C\n"
        "                C()\n"
        "                eliminar C\n"
        "                C()\n"
        "                eliminar C\n"
        "                C()\n"
        "            fin\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    cuerpo = ast[1].cuerpo[1].cuerpo[1].cuerpo[1].cuerpo
    assert type(cuerpo[2]) is NodoInstancia
    assert type(cuerpo[4]) is NodoInstancia
    assert type(cuerpo[6]) is NodoLlamadaFuncion


def test_declaraciones_clase_y_funcion_anteponen_head_a_tail_ambigua():
    prefijo = (
        "clase C:\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
    )
    sufijo = (
        "        eliminar C\n"
        "        C()\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    for shadow in ("        clase C:\n        fin\n", "        func C():\n        fin\n"):
        ast = _parsear(prefijo + shadow + sufijo)
        cuerpo = ast[1].cuerpo[1].cuerpo
        assert type(cuerpo[-3]) is NodoInstancia
        assert type(cuerpo[-1]) is NodoLlamadaFuncion


def test_global_condicional_en_con_fusiona_bindings_realmente_distintos():
    ast = _parsear(
        "func C():\nfin\n"
        "func exterior():\n"
        "    clase C:\n    fin\n"
        "    func interior():\n"
        "        con recurso:\n"
        "            si condicion:\n                global C\n            fin\n"
        "        fin\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_con_hermanos_sin_global_preservan_ancestry_del_padre():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    clase C:\n    fin\n"
        "    con uno:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        C()\n"
        "    fin\n"
        "    con dos:\n"
        "        clase C:\n        fin\n"
        "        eliminar C\n        C()\n"
        "    fin\n"
        "fin"
    )

    llamadas = (ast[1].cuerpo[1].cuerpo[-1], ast[1].cuerpo[2].cuerpo[-1])
    assert all(type(llamada) is NodoInstancia for llamada in llamadas)


def test_global_en_con_anidado_persiste_fuera():
    ast = _parsear(
        "clase C:\nfin\n"
        "func interior():\n"
        "    con uno:\n        con dos:\n            global C\n        fin\n    fin\n"
        "    C()\nfin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_global_condicional_no_se_convierte_en_instancia_segura():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    var C = f\n"
        "    func interior():\n"
        "        si condicion:\n            global C\n        fin\n"
        "        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_en_mientras_conserva_camino_de_cero_iteraciones():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n    var C = f\n"
        "    func interior():\n"
        "        mientras condicion:\n            global C\n        fin\n"
        "        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_en_para_conserva_camino_de_cero_iteraciones():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n    var C = f\n"
        "    func interior():\n"
        "        para elemento en []:\n            global C\n        fin\n"
        "        C()\n    fin\nfin"
    )

    assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_conflictos_global_nolocal_no_producen_instancia_segura():
    for declaraciones in ("global C\n        nolocal C", "nolocal C\n        global C"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func exterior():\n    clase C:\n    fin\n"
            f"    func interior():\n        {declaraciones}\n        C()\n    fin\n"
            "fin"
        )

        assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_sin_binding_raiz_no_inventa_clase():
    ast = _parsear("func interior():\n    global X\n    X()\nfin")

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_global_de_modulo_no_altera_el_binding_visible():
    ast = _parsear("clase C:\nfin\nglobal C\nC()")

    assert type(ast[-1]) is NodoInstancia


def test_global_no_anticipa_declaracion_raiz_futura():
    ast = _parsear(
        "func interior():\n    global C\n    C()\nfin\nclase C:\nfin"
    )

    assert type(ast[0].cuerpo[-1]) is NodoLlamadaFuncion


def test_bucles_preservan_clase_recuperable_comun_tras_sombreado():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            f"    {bucle}\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    var C = 0\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_bucles_preservan_funcion_recuperable_comun_tras_sombreado():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "func C():\nfin\n"
            "func f():\n"
            f"    {bucle}\n"
            "        func C():\n        fin\n"
            "    fin\n"
            "    var C = 0\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_bucles_no_unifican_clase_y_funcion_recuperables():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func exterior():\n"
            "    func C():\n    fin\n"
            "    func interior():\n"
            f"        {bucle}\n"
            "            global C\n"
            "        fin\n"
            "        var C = 0\n"
            "        eliminar C\n"
            "        C()\n"
            "    fin\n"
            "fin"
        )

        assert type(ast[1].cuerpo[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_bucles_no_convierten_estado_diferido_en_ancestry_inmediata():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        sin_exterior = _parsear(
            "func f():\n"
            f"    {bucle}\n"
            "        clase X:\n        fin\n"
            "    fin\n"
            "    var X = 0\n"
            "    eliminar X\n"
            "    X()\n"
            "fin"
        )
        mismo_environment = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            f"    {bucle}\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(sin_exterior[0].cuerpo[-1]) is NodoLlamadaFuncion
        assert type(mismo_environment[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_bucles_preservan_frontera_real_de_con_sin_resucitar_tail():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            "    con recurso:\n"
            f"        {bucle}\n"
            "            clase C:\n            fin\n"
            "        fin\n"
            "        var C = 0\n"
            "        eliminar C\n"
            "        C()\n"
            "        eliminar C\n"
            "        C()\n"
            "    fin\n"
            "fin"
        )
        cuerpo = ast[1].cuerpo[0].cuerpo

        assert type(cuerpo[-3]) is NodoInstancia
        assert type(cuerpo[-1]) is NodoLlamadaFuncion


def test_marker_de_bucle_no_es_binding_exterior_consumible_por_doble_del():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func exterior():\n"
            f"    {bucle}\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    func interior():\n"
            "        eliminar C\n"
            "        eliminar C\n"
            "        C()\n"
            "    fin\n"
            "fin"
        )

        llamada = ast[1].cuerpo[-1].cuerpo[-1]
        assert type(llamada) is NodoLlamadaFuncion


def test_marker_de_bucle_con_procedencia_mixta_no_es_ancestry_inmediata():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    eliminar C\n"
        "    eliminar C\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_marker_de_bucle_sigue_siendo_metadata_en_segundo_scope_descendiente():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    func a():\n"
        "        func b():\n"
        "            eliminar C\n"
        "            eliminar C\n"
        "            C()\n"
        "        fin\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_del_invalida_marker_de_bucle_antes_de_sombreado_posterior():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            f"    {bucle}\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    eliminar C\n"
            "    var C = 0\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_en_con_propaga_invalidacion_de_marker_de_bucle_al_padre():
    for bucle in ("mientras condicion:", "para elemento en valores:"):
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            f"    {bucle}\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    con recurso:\n"
            "        eliminar C\n"
            "    fin\n"
            "    var C = 0\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_del_en_con_anidado_propaga_invalidacion_de_marker_al_padre():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    con exterior:\n"
        "        con interior:\n"
        "            eliminar C\n"
        "        fin\n"
        "    fin\n"
        "    func descendiente():\n"
        "        var C = 0\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_con_no_invalida_marker_por_operaciones_locales_o_ajenas():
    cuerpos = (
        "        var X = 0\n",
        "        var C = 0\n",
        "        eliminar X\n",
    )
    for cuerpo_con in cuerpos:
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            "    mientras condicion:\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    con recurso:\n"
            f"{cuerpo_con}"
            "    fin\n"
            "    var C = 0\n"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoInstancia


def test_del_invalida_marker_antes_de_declaraciones_con_nombre_reutilizado():
    declaraciones = (
        "    func C():\n    fin\n",
        "    clase C:\n    fin\n",
    )
    for declaracion in declaraciones:
        ast = _parsear(
            "clase C:\nfin\n"
            "func f():\n"
            "    mientras condicion:\n"
            "        clase C:\n        fin\n"
            "    fin\n"
            "    eliminar C\n"
            f"{declaracion}"
            "    eliminar C\n"
            "    C()\n"
            "fin"
        )

        assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def test_marker_invalidada_no_se_hereda_a_scope_descendiente():
    ast = _parsear(
        "clase C:\nfin\n"
        "func exterior():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    eliminar C\n"
        "    func interior():\n"
        "        var C = 0\n"
        "        eliminar C\n"
        "        C()\n"
        "    fin\n"
        "fin"
    )

    llamada = ast[1].cuerpo[-1].cuerpo[-1]
    assert type(llamada) is NodoLlamadaFuncion


def test_dos_del_sin_sombreado_no_convierten_marker_en_ancestry():
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    eliminar C\n"
        "    eliminar C\n"
        "    var C = 0\n"
        "    eliminar C\n"
        "    C()\n"
        "fin"
    )

    assert type(ast[1].cuerpo[-1]) is NodoLlamadaFuncion


def _resolver_marker_tras_con(cuerpo_con):
    ast = _parsear(
        "clase C:\nfin\n"
        "func f():\n"
        "    mientras condicion:\n"
        "        clase C:\n        fin\n"
        "    fin\n"
        "    con recurso:\n"
        f"{cuerpo_con}"
        "    fin\n"
        "    var C = 0\n"
        "    eliminar C\n"
        "    C()\n"
        "fin"
    )
    return ast[1].cuerpo[-1]


def test_del_path_sensitive_en_si_de_con_invalida_marker():
    casos = (
        "        si condicion:\n            eliminar C\n        fin\n",
        "        si condicion:\n            eliminar C\n"
        "        sino:\n            var X = 0\n        fin\n",
        "        si condicion:\n            eliminar C\n"
        "        sino:\n            eliminar C\n        fin\n",
    )

    for cuerpo_con in casos:
        assert type(_resolver_marker_tras_con(cuerpo_con)) is NodoLlamadaFuncion


def test_ramas_de_con_sin_del_no_invalidan_marker():
    casos = (
        "        si condicion:\n            var X = 0\n"
        "        sino:\n            var Y = 0\n        fin\n",
        "        si condicion:\n            var C = 0\n        fin\n",
        "        si condicion:\n            global C\n        fin\n",
    )

    for cuerpo_con in casos:
        assert type(_resolver_marker_tras_con(cuerpo_con)) is NodoInstancia


def test_del_path_sensitive_en_bucles_de_con_invalida_marker():
    for bucle in ("mientras otra_condicion:", "para x en valores:"):
        llamada = _resolver_marker_tras_con(
            f"        {bucle}\n            eliminar C\n        fin\n"
        )

        assert type(llamada) is NodoLlamadaFuncion


def test_bucles_de_con_sin_del_no_invalidan_marker():
    for bucle in ("mientras otra_condicion:", "para x en valores:"):
        llamada = _resolver_marker_tras_con(
            f"        {bucle}\n            var X = 0\n        fin\n"
        )

        assert type(llamada) is NodoInstancia


def test_del_ajeno_y_shadow_local_path_sensitive_no_invalidan_marker():
    casos = (
        "        si condicion:\n            eliminar X\n        fin\n",
        "        si condicion:\n            var C = 0\n"
        "        sino:\n            clase C:\n            fin\n        fin\n",
    )

    for cuerpo_con in casos:
        assert type(_resolver_marker_tras_con(cuerpo_con)) is NodoInstancia


def test_del_path_sensitive_en_con_anidado_y_hermano_invalida_marker():
    anidado = _resolver_marker_tras_con(
        "        con interior:\n"
        "            si condicion:\n                eliminar C\n"
        "            fin\n"
        "        fin\n"
    )
    hermanos = _resolver_marker_tras_con(
        "        si condicion:\n            eliminar C\n        fin\n"
        "    fin\n"
        "    con hermano:\n"
        "        var X = 0\n"
    )

    assert type(anidado) is NodoLlamadaFuncion
    assert type(hermanos) is NodoLlamadaFuncion


def test_del_en_funcion_descendiente_de_con_no_invalida_marker_del_padre():
    llamada = _resolver_marker_tras_con(
        "        func descendiente():\n"
        "            si condicion:\n                eliminar C\n"
        "            fin\n"
        "        fin\n"
    )

    assert type(llamada) is NodoInstancia


def test_global_y_nolocal_con_del_condicional_invalidan_marker_afectado():
    global_ast = _parsear(
        "clase C:\nfin\nfunc f():\n"
        "    mientras condicion:\n        clase C:\n        fin\n    fin\n"
        "    con recurso:\n        global C\n"
        "        si condicion:\n            eliminar C\n        fin\n    fin\n"
        "    var C = 0\n    eliminar C\n    C()\nfin"
    )
    nolocal_ast = _parsear(
        "clase C:\nfin\nfunc exterior():\n"
        "    mientras condicion:\n        clase C:\n        fin\n    fin\n"
        "    func interior():\n        con recurso:\n            nolocal C\n"
        "            si condicion:\n                eliminar C\n            fin\n"
        "        fin\n        var C = 0\n        eliminar C\n        C()\n"
        "    fin\nfin"
    )

    assert type(global_ast[1].cuerpo[-1]) is NodoLlamadaFuncion
    assert type(nolocal_ast[1].cuerpo[-1].cuerpo[-1]) is NodoLlamadaFuncion
