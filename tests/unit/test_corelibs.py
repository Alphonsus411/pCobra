import operator
import os
import random
import sys
from collections import OrderedDict
from datetime import datetime
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

sys.modules.setdefault("yaml", ModuleType("yaml"))

import core.ast_nodes as core_ast_nodes

sys.modules.setdefault("cobra.core.ast_nodes", core_ast_nodes)

import pcobra.corelibs as core
import pcobra.corelibs.tiempo as core_tiempo
import pcobra.corelibs.sistema as core_sistema
from cobra.transpilers.import_helper import get_standard_imports
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.ast_nodes import NodoLlamadaFuncion, NodoValor

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_texto_funcs():
    assert core.mayusculas("hola") == "HOLA"
    assert core.minusculas("HOLA") == "hola"
    assert core.capitalizar("cobra") == "Cobra"
    assert core.capitalizar("") == ""
    assert core.titulo("árbol de navidad") == "Árbol De Navidad"
    assert core.invertir("abc") == "cba"
    assert core.concatenar("a", "b") == "ab"
    assert core.quitar_espacios("  hola  ") == "hola"
    assert core.quitar_espacios("--hola--", modo="derecha", caracteres="-") == "--hola"
    with pytest.raises(ValueError):
        core.quitar_espacios("hola", modo="otro")
    assert core.dividir("  hola   mundo  ") == ["hola", "mundo"]
    assert core.dividir("a,b,c", ",", 1) == ["a", "b,c"]
    assert core.unir("-", ["1", 2, "3"]) == "1-2-3"
    assert core.reemplazar("banana", "na", "NA", 1) == "baNAna"
    assert core.reemplazar("abc", "", "-", 2) == "-a-bc"
    assert core.empieza_con("cobral", ("co", "za")) is True
    assert core.termina_con("cobral", ("co", "al")) is True
    assert core.incluye("hola", "ol") is True
    assert core.quitar_prefijo("prefijo", "pre") == "fijo"
    assert core.quitar_prefijo("prefijo", "prE") == "prefijo"
    assert core.quitar_sufijo("archivo.tmp", ".tmp") == "archivo"
    assert core.quitar_sufijo("archivo.tmp", ".tm") == "archivo.tmp"
    assert core.dividir_lineas("uno\r\ndos\n") == ["uno", "dos"]
    assert core.dividir_lineas("uno\r\ndos\n", conservar_delimitadores=True) == [
        "uno\r\n",
        "dos\n",
    ]
    assert core.dividir_lineas("") == []
    assert core.contar_subcadena("banana", "na") == 2
    assert core.contar_subcadena("banana", "na", 0, 3) == 0
    assert core.centrar_texto("cobra", 9, "*") == "**cobra**"
    with pytest.raises(TypeError):
        core.centrar_texto("cobra", 10, "--")
    assert core.rellenar_ceros("7", 3) == "007"
    assert core.rellenar_ceros("-5", 4) == "-005"
    assert core.rellenar_ceros("猫", 3) == "00猫"
    assert core.minusculas_casefold("Straße") == "strasse"
    assert core.rellenar_izquierda("7", 3, "0") == "007"
    assert core.rellenar_derecha("7", 3, "0") == "700"
    with pytest.raises(ValueError):
        core.rellenar_izquierda("hola", 10, "")
    assert core.normalizar_unicode("A\u0301", "NFC") == "Á"
    with pytest.raises(ValueError):
        core.normalizar_unicode("hola", "XYZ")


def test_numero_funcs():
    assert core.absoluto(-5) == 5
    assert core.absoluto(-5.2) == pytest.approx(5.2)
    assert core.redondear(3.14159, 2) == pytest.approx(3.14)
    assert core.redondear(3.6) == 4
    assert core.piso(3.9) == 3
    assert core.techo(3.1) == 4
    assert core.mcd(48, 18) == 6
    assert core.mcm(4, 6, 8) == 24
    assert core.es_cercano(1.0, 1.0 + 1e-10) is True
    assert core.es_cercano(1.0, 1.1, tolerancia_relativa=0.2) is True
    assert core.raiz(9) == pytest.approx(3.0)
    assert core.raiz(-8, 3) == pytest.approx(-2.0)
    assert core.potencia(2, 3) == pytest.approx(8.0)
    assert core.clamp(5, 0, 3) == 3
    assert 1 <= core.aleatorio(1, 2, semilla=42) <= 2
    assert core.mediana([1, 2, 3, 4]) == 2.5
    assert core.moda([1, 1, 2, 2, 2]) == 2
    assert core.producto([2, 3, 5]) == 30
    assert core.producto([], inicio=10) == 10
    assert core.entero_a_base(255, 16) == "FF"
    assert core.entero_a_base(-10, 2) == "-1010"
    assert core.entero_desde_base("ff", 16) == 255
    assert core.entero_desde_base("-1010", 2) == -10
    datos = [2, 4, 4, 4, 5, 5, 7, 9]
    assert core.desviacion_estandar(datos) == pytest.approx(2.0)
    assert core.desviacion_estandar(datos, muestral=True) == pytest.approx(
        2.1380899353
    )
    assert core.es_par(4) is True
    assert core.es_par(5) is False
    assert core.es_primo(7) is True
    assert core.es_primo(4) is False
    assert core.factorial(5) == 120
    assert core.promedio([1, 2, 3]) == 2.0


def test_logica_funcs():
    casos = [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]
    for a, b in casos:
        assert core.conjuncion(a, b) is (a and b)
        assert core.disyuncion(a, b) is (a or b)
        assert core.negacion(a) is (not a)
        assert core.xor(a, b) is ((a and not b) or (not a and b))
        assert core.nand(a, b) is (not (a and b))
        assert core.nor(a, b) is (not (a or b))
        assert core.implica(a, b) is ((not a) or b)
        assert core.equivale(a, b) is (a is b)

    assert core.xor_multiple(True, False, True) is False
    assert core.xor_multiple(False, False, False) is False
    assert core.xor_multiple(True, True, True, False) is True

    assert core.todas([True, True, True]) is True
    assert core.todas([True, False, True]) is False
    assert core.alguna([False, False, True]) is True
    assert core.alguna([False, False, False]) is False

    with pytest.raises(TypeError):
        core.conjuncion(1, True)
    with pytest.raises(TypeError):
        core.disyuncion(True, "no bool")
    with pytest.raises(TypeError):
        core.negacion("no bool")
    with pytest.raises(ValueError):
        core.xor_multiple(True)
    with pytest.raises(TypeError):
        core.xor_multiple(True, 0)
    with pytest.raises(TypeError):
        core.todas([True, 1])
    with pytest.raises(TypeError):
        core.alguna([False, None])


def test_archivo_funcs(tmp_path, monkeypatch):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    nombre = "f.txt"
    core.escribir(nombre, "data")
    ruta = tmp_path / nombre
    assert core.existe(ruta)
    assert core.leer(nombre) == "data"
    core.eliminar(ruta)
    assert not core.existe(ruta)


@pytest.mark.parametrize(
    "func",
    [core.leer, lambda ruta: core.escribir(ruta, "dato")],
)
@pytest.mark.parametrize(
    "ruta",
    [
        lambda base: str((base / "absoluta.txt").resolve()),
        lambda _base: "../escape.txt",
    ],
)
def test_archivo_rechaza_rutas_invalidas(monkeypatch, tmp_path, func, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        func(ruta(tmp_path))


def test_tiempo_funcs(monkeypatch):
    ahora = core.ahora()
    assert isinstance(ahora, datetime)
    fecha = datetime(2020, 1, 2, 3, 4, 5)
    assert core.formatear(fecha, "%Y") == "2020"
    called = {}

    def fake_sleep(seg):
        called["v"] = seg

    monkeypatch.setattr(core_tiempo.time, "sleep", fake_sleep)
    core.dormir(0.01)
    assert called["v"] == 0.01


def test_coleccion_funcs():
    datos = [3, 1, 2, 1]
    assert core.ordenar(datos) == [1, 1, 2, 3]
    assert core.maximo(datos) == 3
    assert core.minimo(datos) == 1
    assert core.sin_duplicados(datos) == [3, 1, 2]
    assert core.mapear(datos, lambda x: x + 1) == [4, 2, 3, 2]
    assert core.filtrar(datos, lambda x: x % 2 == 0) == [2]
    assert core.reducir([1, 2, 3], operator.add) == 6
    assert core.reducir([1, 2, 3], operator.add, 10) == 16
    assert core.encontrar(datos, lambda x: x > 2) == 3
    assert core.encontrar(datos, lambda x: x > 10, predeterminado="ninguno") == "ninguno"
    assert core.aplanar([[1, 2], (3, 4)]) == [1, 2, 3, 4]
    estructuras = [
        {"tipo": "a", "valor": 1},
        {"tipo": "b", "valor": 2},
        {"tipo": "a", "valor": 3},
    ]
    agrupado = core.agrupar_por(estructuras, lambda x: x["tipo"])
    assert isinstance(agrupado, OrderedDict)
    assert list(agrupado.keys()) == ["a", "b"]
    assert [e["valor"] for e in agrupado["a"]] == [1, 3]

    class Objeto:
        def __init__(self, categoria):
            self.categoria = categoria

    objetos = [Objeto("x"), Objeto("x"), Objeto("y")]
    agrupados_objetos = core.agrupar_por(objetos, "categoria")
    assert list(agrupados_objetos.keys()) == ["x", "y"]

    pares, impares = core.particionar(range(5), lambda x: x % 2 == 0)
    assert pares == [0, 2, 4]
    assert impares == [1, 3]
    esperado = [1, 2, 3]
    random.Random(7).shuffle(esperado)
    assert core.mezclar([1, 2, 3], semilla=7) == esperado
    assert core.zip_listas([1, 2], ["a", "b", "c"]) == [(1, "a"), (2, "b")]
    assert core.zip_listas() == []
    assert core.tomar(datos, 2) == [3, 1]
    assert core.tomar(datos, 0) == []
    assert core.mapear([], lambda x: x) == []


def test_coleccion_validaciones():
    with pytest.raises(ValueError):
        core.maximo([])
    with pytest.raises(ValueError):
        core.minimo([])
    with pytest.raises(TypeError):
        core.mapear([1], None)
    with pytest.raises(TypeError):
        core.filtrar([1], "no callable")
    with pytest.raises(ValueError):
        core.reducir([], operator.add)
    with pytest.raises(TypeError):
        core.particionar([1], None)
    with pytest.raises(KeyError):
        core.agrupar_por([{"tipo": "a"}], "categoria")
    with pytest.raises(ValueError):
        core.tomar([1], -1)
    with pytest.raises(TypeError):
        core.tomar([1], 1.5)


def test_seguridad_funcs():
    assert (
        core.hash_sha256("a")
        == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"
    )
    uuid = core.generar_uuid()
    assert isinstance(uuid, str) and len(uuid) == 36


def test_red_funcs(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "x")
    mock_resp_get = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_get.iter_content.return_value = [b"ok"]
    mock_resp_get.raise_for_status.return_value = None
    mock_resp_post = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_post.iter_content.return_value = [b"ok"]
    mock_resp_post.raise_for_status.return_value = None
    with patch(
        "pcobra.corelibs.red.requests.get", return_value=mock_resp_get
    ) as mock_get, patch(
        "pcobra.corelibs.red.requests.post", return_value=mock_resp_post
    ) as mock_post:
        assert core.obtener_url("https://x") == "ok"
        assert core.enviar_post("https://x", {"a": 1}) == "ok"
        mock_get.assert_called_once_with(
            "https://x", timeout=5, allow_redirects=False, stream=True
        )
        mock_post.assert_called_once_with(
            "https://x", data={"a": 1}, timeout=5, allow_redirects=False, stream=True
        )


def test_red_obtener_url_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("ftp://ejemplo.com")
        mock_get.assert_not_called()


def test_red_obtener_url_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("file:///tmp/archivo.txt")
        mock_get.assert_not_called()


def test_red_enviar_post_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("ftp://ejemplo.com", {"a": 1})
        mock_post.assert_not_called()


def test_red_enviar_post_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("file:///tmp/archivo.txt", {"a": 1})
        mock_post.assert_not_called()


def test_red_host_whitelist_permite(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(url="https://example.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp) as mock_get:
        assert core.obtener_url("https://example.com") == "ok"
        mock_get.assert_called_once_with(
            "https://example.com", timeout=5, allow_redirects=False, stream=True
        )


def test_red_host_whitelist_rechaza(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://otro.com")
        mock_get.assert_not_called()


def test_red_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://otro.com"}
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)


def test_red_enviar_post_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://otro.com"}
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.post", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.enviar_post(
                "https://example.com", {"a": 1}, permitir_redirecciones=True
            )


def test_red_obtener_url_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=grande):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com")
    grande.close.assert_called_once()


def test_red_enviar_post_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.post", return_value=grande):
        with pytest.raises(ValueError):
            core.enviar_post("https://example.com", {"a": 1})
    grande.close.assert_called_once()


def test_sistema_funcs(tmp_path, monkeypatch):
    assert core.obtener_os() == os.uname().sysname
    proc = MagicMock()
    proc.stdout = "hola\n"

    def fake_run(*a, **k):
        assert k["timeout"] == 1
        return proc

    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)
    permitido = core_sistema.os.path.realpath("/usr/bin/echo")
    assert (
        core.ejecutar(["echo", "hola"], permitidos=[permitido], timeout=1)
        == "hola\n"
    )
    os.environ["PRUEBA"] = "1"
    assert core.obtener_env("PRUEBA") == "1"
    d = tmp_path
    (d / "x").write_text("")
    assert "x" in core.listar_dir(d)


def test_transpile_texto():
    ast = [
        NodoLlamadaFuncion("mayusculas", [NodoValor("'hola'")]),
        NodoLlamadaFuncion("minusculas", [NodoValor("'HOLA'")]),
        NodoLlamadaFuncion("capitalizar", [NodoValor("'cobra'")]),
        NodoLlamadaFuncion("titulo", [NodoValor("'cobra feroz'")]),
        NodoLlamadaFuncion("invertir", [NodoValor("'abc'")]),
        NodoLlamadaFuncion("concatenar", [NodoValor("'a'"), NodoValor("'b'")]),
        NodoLlamadaFuncion("quitar_espacios", [NodoValor("'  hola  '")]),
        NodoLlamadaFuncion("dividir", [NodoValor("'a b c'")]),
        NodoLlamadaFuncion("unir", [NodoValor("'-'"), NodoValor('["a","b"]')]),
        NodoLlamadaFuncion(
            "reemplazar",
            [
                NodoValor("'banana'"),
                NodoValor("'na'"),
                NodoValor("'NA'"),
                NodoValor(1),
            ],
        ),
        NodoLlamadaFuncion("empieza_con", [NodoValor("'cobra'"), NodoValor("'co'")]),
        NodoLlamadaFuncion("termina_con", [NodoValor("'cobra'"), NodoValor("'bra'")]),
        NodoLlamadaFuncion("incluye", [NodoValor("'cobra'"), NodoValor("'ob'")]),
        NodoLlamadaFuncion(
            "rellenar_izquierda",
            [NodoValor("'7'"), NodoValor(3), NodoValor("'0'")],
        ),
        NodoLlamadaFuncion(
            "rellenar_derecha",
            [NodoValor("'7'"), NodoValor(3), NodoValor("'0'")],
        ),
        NodoLlamadaFuncion(
            "normalizar_unicode", [NodoValor("'Á'"), NodoValor("'NFD'")]
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "mayusculas('hola')\n"
        + "minusculas('HOLA')\n"
        + "capitalizar('cobra')\n"
        + "titulo('cobra feroz')\n"
        + "invertir('abc')\n"
        + "concatenar('a', 'b')\n"
        + "quitar_espacios('  hola  ')\n"
        + "dividir('a b c')\n"
        + "unir('-', [\"a\",\"b\"])\n"
        + "reemplazar('banana', 'na', 'NA', 1)\n"
        + "empieza_con('cobra', 'co')\n"
        + "termina_con('cobra', 'bra')\n"
        + "incluye('cobra', 'ob')\n"
        + "rellenar_izquierda('7', 3, '0')\n"
        + "rellenar_derecha('7', 3, '0')\n"
        + "normalizar_unicode('Á', 'NFD')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "mayusculas('hola');\n"
        + "minusculas('HOLA');\n"
        + "capitalizar('cobra');\n"
        + "titulo('cobra feroz');\n"
        + "invertir('abc');\n"
        + "concatenar('a', 'b');\n"
        + "quitar_espacios('  hola  ');\n"
        + "dividir('a b c');\n"
        + "unir('-', [\"a\",\"b\"]);\n"
        + "reemplazar('banana', 'na', 'NA', 1);\n"
        + "empieza_con('cobra', 'co');\n"
        + "termina_con('cobra', 'bra');\n"
        + "incluye('cobra', 'ob');\n"
        + "rellenar_izquierda('7', 3, '0');\n"
        + "rellenar_derecha('7', 3, '0');\n"
        + "normalizar_unicode('Á', 'NFD');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_numero():
    ast = [
        NodoLlamadaFuncion("absoluto", [NodoValor(-5)]),
        NodoLlamadaFuncion("redondear", [NodoValor(3.14159), NodoValor(2)]),
        NodoLlamadaFuncion("piso", [NodoValor(3.9)]),
        NodoLlamadaFuncion("techo", [NodoValor(3.1)]),
        NodoLlamadaFuncion("raiz", [NodoValor(9)]),
        NodoLlamadaFuncion("potencia", [NodoValor(2), NodoValor(3)]),
        NodoLlamadaFuncion("clamp", [NodoValor(5), NodoValor(0), NodoValor(3)]),
        NodoLlamadaFuncion("aleatorio", [NodoValor(1), NodoValor(2)]),
        NodoLlamadaFuncion("mediana", [NodoValor("[1,2,3]")]),
        NodoLlamadaFuncion("moda", [NodoValor("[1,1,2]")]),
        NodoLlamadaFuncion("desviacion_estandar", [NodoValor("[1,2,3]")]),
        NodoLlamadaFuncion("es_par", [NodoValor(2)]),
        NodoLlamadaFuncion("es_primo", [NodoValor(3)]),
        NodoLlamadaFuncion("factorial", [NodoValor(3)]),
        NodoLlamadaFuncion("promedio", [NodoValor("[1,2]")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "absoluto(-5)\n"
        + "redondear(3.14159, 2)\n"
        + "piso(3.9)\n"
        + "techo(3.1)\n"
        + "raiz(9)\n"
        + "potencia(2, 3)\n"
        + "clamp(5, 0, 3)\n"
        + "aleatorio(1, 2)\n"
        + "mediana([1,2,3])\n"
        + "moda([1,1,2])\n"
        + "desviacion_estandar([1,2,3])\n"
        + "es_par(2)\n"
        + "es_primo(3)\n"
        + "factorial(3)\n"
        + "promedio([1,2])\n"
    )
    js_exp = (
        IMPORTS_JS
        + "absoluto(-5);\n"
        + "redondear(3.14159, 2);\n"
        + "piso(3.9);\n"
        + "techo(3.1);\n"
        + "raiz(9);\n"
        + "potencia(2, 3);\n"
        + "clamp(5, 0, 3);\n"
        + "aleatorio(1, 2);\n"
        + "mediana([1,2,3]);\n"
        + "moda([1,1,2]);\n"
        + "desviacion_estandar([1,2,3]);\n"
        + "es_par(2);\n"
        + "es_primo(3);\n"
        + "factorial(3);\n"
        + "promedio([1,2]);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_archivo():
    ast = [
        NodoLlamadaFuncion("leer", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("escribir", [NodoValor("'f.txt'"), NodoValor("'x'")]),
        NodoLlamadaFuncion("existe", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("eliminar", [NodoValor("'f.txt'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "leer('f.txt')\n"
        + "escribir('f.txt', 'x')\n"
        + "existe('f.txt')\n"
        + "eliminar('f.txt')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "leer('f.txt');\n"
        + "escribir('f.txt', 'x');\n"
        + "existe('f.txt');\n"
        + "eliminar('f.txt');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_tiempo():
    ast = [
        NodoLlamadaFuncion("ahora", []),
        NodoLlamadaFuncion("formatear", [NodoValor("fecha"), NodoValor("'%Y'")]),
        NodoLlamadaFuncion("dormir", [NodoValor(1)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "ahora()\n" + "formatear(fecha, '%Y')\n" + "dormir(1)\n"
    js_exp = IMPORTS_JS + "ahora();\n" + "formatear(fecha, '%Y');\n" + "dormir(1);"
    assert py == py_exp
    assert js == js_exp


def test_transpile_coleccion():
    ast = [
        NodoLlamadaFuncion("ordenar", [NodoValor("[3,1]")]),
        NodoLlamadaFuncion("maximo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("minimo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("sin_duplicados", [NodoValor("[1,1]")]),
        NodoLlamadaFuncion("mapear", [NodoValor("[1,2]"), NodoValor("duplicar")]),
        NodoLlamadaFuncion("filtrar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion(
            "reducir",
            [NodoValor("[1,2,3]"), NodoValor("sumar"), NodoValor(0)],
        ),
        NodoLlamadaFuncion("encontrar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion("aplanar", [NodoValor("[[1,2],[3,4]]")]),
        NodoLlamadaFuncion("agrupar_por", [NodoValor("datos"), NodoValor("'tipo'")]),
        NodoLlamadaFuncion("particionar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion("mezclar", [NodoValor("[1,2,3]"), NodoValor(1)]),
        NodoLlamadaFuncion("zip_listas", [NodoValor("[1,2]"), NodoValor("[3,4]")]),
        NodoLlamadaFuncion("tomar", [NodoValor("[1,2,3]"), NodoValor(2)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "ordenar([3,1])\n"
        + "maximo([1,2])\n"
        + "minimo([1,2])\n"
        + "sin_duplicados([1,1])\n"
        + "mapear([1,2], duplicar)\n"
        + "filtrar([1,2,3], es_par)\n"
        + "reducir([1,2,3], sumar, 0)\n"
        + "encontrar([1,2,3], es_par)\n"
        + "aplanar([[1,2],[3,4]])\n"
        + "agrupar_por(datos, 'tipo')\n"
        + "particionar([1,2,3], es_par)\n"
        + "mezclar([1,2,3], 1)\n"
        + "zip_listas([1,2], [3,4])\n"
        + "tomar([1,2,3], 2)\n"
    )
    js_exp = (
        IMPORTS_JS
        + "ordenar([3,1]);\n"
        + "maximo([1,2]);\n"
        + "minimo([1,2]);\n"
        + "sin_duplicados([1,1]);\n"
        + "mapear([1,2], duplicar);\n"
        + "filtrar([1,2,3], es_par);\n"
        + "reducir([1,2,3], sumar, 0);\n"
        + "encontrar([1,2,3], es_par);\n"
        + "aplanar([[1,2],[3,4]]);\n"
        + "agrupar_por(datos, 'tipo');\n"
        + "particionar([1,2,3], es_par);\n"
        + "mezclar([1,2,3], 1);\n"
        + "zip_listas([1,2], [3,4]);\n"
        + "tomar([1,2,3], 2);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_seguridad():
    ast = [
        NodoLlamadaFuncion("hash_sha256", [NodoValor("'a'")]),
        NodoLlamadaFuncion("generar_uuid", []),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "hash_sha256('a')\n" + "generar_uuid()\n"
    js_exp = IMPORTS_JS + "hash_sha256('a');\n" + "generar_uuid();"
    assert py == py_exp
    assert js == js_exp


def test_transpile_red():
    ast = [
        NodoLlamadaFuncion("obtener_url", [NodoValor("'https://x'")]),
        NodoLlamadaFuncion(
            "enviar_post", [NodoValor("'https://x'"), NodoValor('{"a":1}')]
        ),
        NodoLlamadaFuncion("obtener_url_async", [NodoValor("'https://x'")]),
        NodoLlamadaFuncion(
            "enviar_post_async",
            [NodoValor("'https://x'"), NodoValor('{"a":1}')],
        ),
        NodoLlamadaFuncion(
            "descargar_archivo",
            [NodoValor("'https://x'"), NodoValor("'salida.bin'")],
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_url('https://x')\n"
        + "enviar_post('https://x', {\"a\":1})\n"
        + "obtener_url_async('https://x')\n"
        + "enviar_post_async('https://x', {\"a\":1})\n"
        + "descargar_archivo('https://x', 'salida.bin')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_url('https://x');\n"
        + "enviar_post('https://x', {\"a\":1});\n"
        + "obtener_url_async('https://x');\n"
        + "enviar_post_async('https://x', {\"a\":1});\n"
        + "descargar_archivo('https://x', 'salida.bin');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_sistema():
    ast = [
        NodoLlamadaFuncion("obtener_os", []),
        NodoLlamadaFuncion("ejecutar", [NodoValor("['ls']")]),
        NodoLlamadaFuncion("obtener_env", [NodoValor("'PATH'")]),
        NodoLlamadaFuncion("listar_dir", [NodoValor("'.'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_os()\n"
        + "ejecutar(['ls'])\n"
        + "obtener_env('PATH')\n"
        + "listar_dir('.')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_os();\n"
        + "ejecutar(['ls']);\n"
        + "obtener_env('PATH');\n"
        + "listar_dir('.');"
    )
    assert py == py_exp
    assert js == js_exp
