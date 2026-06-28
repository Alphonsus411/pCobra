from __future__ import annotations

from datetime import datetime
from platform import system
from types import SimpleNamespace

import pytest

from pcobra.cobra.usar_loader import usar_modulo


def _exports_publicos(nombre: str) -> dict[str, object]:
    exports = usar_modulo(nombre)
    return {
        clave: valor
        for clave, valor in exports.items()
        if clave not in {"simbolos", "metadata"}
    }


@pytest.mark.parametrize(
    ("modulo", "funciones", "casos", "ausentes"),
    [
        ("numero", ("es_finito", "signo"), ((("es_finito", (10,), True), ("signo", (-5,), -1))), ("isfinite", "sign")),
        ("texto", ("mayusculas", "recortar"), ((("mayusculas", ("cobra",), "COBRA"), ("recortar", ("  cobra  ",), "cobra"))), ("upper", "strip")),
        ("datos", ("longitud", "elemento"), ((("longitud", ([1, 2, 3],), 3), ("elemento", ([1, 2, 3], 0), 1))), ("len", "getitem")),
        ("logica", ("conjuncion", "negacion"), ((("conjuncion", (True, False), False), ("negacion", (True,), False))), ("and", "not")),
    ],
)
def test_usar_modulos_publicos_basicos(modulo, funciones, casos, ausentes):
    exports = _exports_publicos(modulo)

    for funcion in funciones:
        assert funcion in exports
        assert callable(exports[funcion])
        assert funcion in usar_modulo(modulo)["metadata"]

    for funcion, args, esperado in casos:
        assert exports[funcion](*args) == esperado

    for alias in ausentes:
        assert alias not in exports


def test_usar_asincrono_proteger_tarea(monkeypatch):
    shield_result = object()
    mock_task = SimpleNamespace(cancel=lambda: None, done=lambda: True)
    exports = _exports_publicos("asincrono")

    monkeypatch.setattr(
        "pcobra.corelibs.asincrono._asegurar_tarea",
        lambda _awaitable: mock_task,
    )
    monkeypatch.setattr("asyncio.shield", lambda tarea: shield_result if tarea is mock_task else None)

    assert "proteger_tarea" in exports
    assert exports["proteger_tarea"](object()) is shield_result


def test_usar_sistema_obtener_os_y_ejecutar(monkeypatch):
    exports = _exports_publicos("sistema")

    monkeypatch.setattr(
        "pcobra.corelibs.sistema._resolver_ejecutable",
        lambda comando, permitidos: ([r"C:\cobra\mock.exe", *comando[1:]], r"C:\cobra\mock.exe", 10, 1, 2),
    )
    monkeypatch.setattr("pcobra.corelibs.sistema._verificar_descriptor", lambda *args: None)
    monkeypatch.setattr("pcobra.corelibs.sistema._verificar_ruta", lambda *args: None)
    monkeypatch.setattr("os.close", lambda _fd: None)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(stdout="mocked output", stderr="", returncode=0),
    )

    assert exports["obtener_os"]() == system()
    assert exports["ejecutar"](["cobra"], permitidos=[r"C:\cobra\mock.exe"]) == "mocked output"


def test_usar_archivo_existe(tmp_path, monkeypatch):
    (tmp_path / "demo.txt").write_text("cobra", encoding="utf-8")
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))

    exports = _exports_publicos("archivo")

    assert exports["existe"]("demo.txt") is True
    assert exports["existe"]("../fuera.txt") is False


def test_usar_tiempo_ahora(monkeypatch):
    instante = datetime(2026, 6, 28, 12, 0, 0)
    monkeypatch.setattr("pcobra.corelibs.tiempo._hoy", lambda: instante)

    exports = _exports_publicos("tiempo")

    assert exports["ahora"]() == instante


def test_usar_red_obtener_url(monkeypatch):
    class _FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}
        encoding = "utf-8"
        url = "https://example.com"

        def iter_content(self, chunk_size=8192):
            _ = chunk_size
            yield b"contenido remoto"

        def raise_for_status(self):
            return None

        def close(self):
            return None

    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: _FakeResponse())

    exports = _exports_publicos("red")

    assert exports["obtener_url"]("https://example.com") == "contenido remoto"


def test_usar_holobit_crear_holobit():
    exports = _exports_publicos("holobit")

    assert "crear_holobit" in exports
    resultado = exports["crear_holobit"]([1.0, 2.0, 3.0])
    assert resultado == {"tipo": "holobit", "valores": [1.0, 2.0, 3.0]}
