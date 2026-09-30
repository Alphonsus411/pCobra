from cobra.core import Lexer, Parser, TipoToken
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoCondicional,
    NodoFuncion,
    NodoImprimir,
    NodoMetodo,
)


def _parsear(codigo: str):
    return Parser(Lexer(codigo).analizar_token()).parsear()


def _clase(codigo: str) -> NodoClase:
    ast = _parsear(codigo)
    assert len(ast) == 1
    assert isinstance(ast[0], NodoClase)
    return ast[0]


def test_un_metodo_sin_fin_individual_y_fin_cierra_clase():
    clase = _clase(
        '''
clase Persona:
    metodo saludar(este):
        imprimir "Hola"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == ["saludar"]
    assert len(clase.metodos[0].cuerpo) == 1
    assert isinstance(clase.metodos[0].cuerpo[0], NodoImprimir)


def test_dos_metodos_consecutivos_tienen_cuerpos_independientes():
    clase = _clase(
        '''
clase Persona:
    metodo primero(este):
        imprimir "uno"

    metodo segundo(este):
        imprimir "dos"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "primero",
        "segundo",
    ]
    assert [len(metodo.cuerpo) for metodo in clase.metodos] == [1, 1]
    assert all(isinstance(metodo.cuerpo[0], NodoImprimir) for metodo in clase.metodos)


def test_tres_metodos_consecutivos_no_se_absorben():
    clase = _clase(
        '''
clase Contador:
    metodo uno(este):
        imprimir "uno"
    metodo dos(este):
        imprimir "dos"
    metodo tres(este):
        imprimir "tres"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "uno",
        "dos",
        "tres",
    ]
    assert [len(metodo.cuerpo) for metodo in clase.metodos] == [1, 1, 1]


def test_metodo_con_varias_instrucciones_conserva_solo_su_cuerpo():
    clase = _clase(
        '''
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre
        imprimir nombre

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
fin
'''
    )

    assert len(clase.metodos) == 2
    inicializar, saludar = clase.metodos
    assert inicializar.nombre_original == "inicializar"
    assert [type(nodo) for nodo in inicializar.cuerpo] == [
        NodoAsignacion,
        NodoImprimir,
    ]
    assert saludar.nombre_original == "saludar"
    assert [type(nodo) for nodo in saludar.cuerpo] == [NodoImprimir]


def test_fin_de_bloque_interno_no_cierra_metodo_ni_clase():
    clase = _clase(
        '''
clase Ejemplo:
    metodo comprobar(este, valor):
        si valor:
            imprimir valor
        fin
        imprimir "comprobado"

    metodo siguiente(este):
        imprimir "ok"
fin
'''
    )

    assert len(clase.metodos) == 2
    comprobar, siguiente = clase.metodos
    assert [type(nodo) for nodo in comprobar.cuerpo] == [
        NodoCondicional,
        NodoImprimir,
    ]
    assert [type(nodo) for nodo in siguiente.cuerpo] == [NodoImprimir]


def test_metodos_normales_y_asincronicos_delimitan_el_metodo_anterior():
    clase = _clase(
        '''
clase Servicio:
    metodo normal(este):
        imprimir "normal"
    asincronico metodo remoto(este):
        imprimir "remoto"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "normal",
        "remoto",
    ]
    assert clase.metodos[1].asincronica is True


def test_smoke_normativo_parsea_clase_y_deja_el_resto_para_el_parser():
    codigo = '''
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
fin

var persona = Persona("Adolfo")
persona.saludar()
'''
    parser = Parser(Lexer(codigo).analizar_token())
    clase = parser.declaracion()

    assert isinstance(clase, NodoClase)
    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "inicializar",
        "saludar",
    ]
    assert [len(metodo.cuerpo) for metodo in clase.metodos] == [1, 1]
    assert all(isinstance(metodo, NodoMetodo) for metodo in clase.metodos)
    assert parser.token_actual().tipo == TipoToken.VAR


def test_codigo_parseable_fuera_de_clase_no_se_absorbe_en_ultimo_metodo():
    ast = _parsear(
        '''
clase Persona:
    metodo saludar(este):
        imprimir "Hola"
fin
var fuera = 1
imprimir fuera
'''
    )

    assert len(ast) == 3
    assert isinstance(ast[0], NodoClase)
    assert len(ast[0].metodos[0].cuerpo) == 1
    assert isinstance(ast[1], NodoAsignacion)
    assert isinstance(ast[2], NodoImprimir)


def test_forma_historica_con_fin_individual_sigue_aceptada():
    clase = _clase(
        '''
clase Persona:
    metodo primero(este):
        imprimir "uno"
    fin
    metodo segundo(este):
        imprimir "dos"
    fin
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "primero",
        "segundo",
    ]
    assert [len(metodo.cuerpo) for metodo in clase.metodos] == [1, 1]


def test_funcion_local_permanece_en_metodo_y_no_en_clase():
    clase = _clase(
        '''
clase Ejemplo:
    metodo exterior(este):
        func interior(x):
            imprimir x
        fin

        imprimir "seguimos"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == ["exterior"]
    assert [type(nodo) for nodo in clase.metodos[0].cuerpo] == [
        NodoFuncion,
        NodoImprimir,
    ]
    assert clase.metodos[0].cuerpo[0].nombre == "interior"


def test_funcion_local_asincronica_permanece_en_metodo():
    clase = _clase(
        '''
clase Ejemplo:
    metodo exterior(este):
        asincronico func interior(x):
            imprimir x
        fin

        imprimir "seguimos"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == ["exterior"]
    assert [type(nodo) for nodo in clase.metodos[0].cuerpo] == [
        NodoFuncion,
        NodoImprimir,
    ]
    assert clase.metodos[0].cuerpo[0].asincronica is True


def test_funcion_local_con_varias_instrucciones_antes_de_otro_metodo():
    clase = _clase(
        '''
clase Ejemplo:
    metodo exterior(este):
        func interior(x):
            imprimir x
            imprimir "dentro"
        fin

        imprimir "fin exterior"

    metodo segundo(este):
        imprimir "segundo"
fin
'''
    )

    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "exterior",
        "segundo",
    ]
    exterior, segundo = clase.metodos
    assert [type(nodo) for nodo in exterior.cuerpo] == [NodoFuncion, NodoImprimir]
    assert [type(nodo) for nodo in exterior.cuerpo[0].cuerpo] == [
        NodoImprimir,
        NodoImprimir,
    ]
    assert [type(nodo) for nodo in segundo.cuerpo] == [NodoImprimir]


def test_func_sigue_siendo_alias_historico_de_metodo_con_fin_individual():
    clase = _clase(
        '''
clase Ejemplo:
    func primero(este):
        imprimir "uno"
    fin
    func segundo(este):
        imprimir "dos"
    fin
fin
'''
    )

    assert [type(metodo) for metodo in clase.metodos] == [NodoMetodo, NodoMetodo]
    assert [metodo.nombre_original for metodo in clase.metodos] == [
        "primero",
        "segundo",
    ]
