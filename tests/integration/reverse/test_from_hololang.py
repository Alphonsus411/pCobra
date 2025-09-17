from pcobra.cobra.reverse import ReverseFromHololang
from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoEsperar,
    NodoFuncion,
    NodoHolobit,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoPara,
    NodoRetorno,
    NodoUsar,
    NodoValor,
)


def test_hololang_basic_structures():
    codigo = """
    let x = 10;
    fn sumar(a, b) {
        let resultado = a + b;
        return resultado;
    }
    sumar(1, 2);
    """

    ast = ReverseFromHololang().generate_ast(codigo)

    funcion = next(n for n in ast if isinstance(n, NodoFuncion))
    asignacion = funcion.cuerpo[0]
    assert isinstance(asignacion, NodoAsignacion)
    assert isinstance(asignacion.expresion, NodoOperacionBinaria)

    retorno = funcion.cuerpo[1]
    assert isinstance(retorno, NodoRetorno)

    llamada = next(n for n in ast if isinstance(n, NodoLlamadaFuncion) and n.nombre == "sumar")
    assert all(isinstance(arg, NodoValor) for arg in llamada.argumentos)


def test_hololang_control_flow():
    codigo = """
    while (x > 0) {
        let x = x - 1;
    }
    if (x > 5) {
        let y = 2;
    } else {
        let y = 3;
    }
    for (item in coleccion) {
        procesar(item);
    }
    """

    ast = ReverseFromHololang().generate_ast(codigo)

    bucle = next(n for n in ast if isinstance(n, NodoBucleMientras))
    assert isinstance(bucle.condicion, NodoOperacionBinaria)
    assert isinstance(bucle.cuerpo[0], NodoAsignacion)

    condicional = next(n for n in ast if isinstance(n, NodoCondicional))
    assert condicional.bloque_sino

    bucle_para = next(n for n in ast if isinstance(n, NodoPara))
    assert any(isinstance(stmt, NodoLlamadaFuncion) for stmt in bucle_para.cuerpo)


def test_hololang_holobit_async():
    codigo = """
    use holo.async::*;
    async fn principal() {
        await trabajo();
    }
    let miHolobit = Holobit::new([0.8, -0.5, 1.2]);
    """

    ast = ReverseFromHololang().generate_ast(codigo)

    usar = ast[0]
    assert isinstance(usar, NodoUsar)

    funcion = next(n for n in ast if isinstance(n, NodoFuncion))
    assert funcion.asincronica is True

    esperar = next(s for s in funcion.cuerpo if isinstance(s, NodoEsperar))
    assert isinstance(esperar.expresion, NodoLlamadaFuncion)

    holobit = next(n for n in ast if isinstance(n, NodoHolobit))
    assert holobit.nombre == "miHolobit"
    assert holobit.valores == [0.8, -0.5, 1.2]
