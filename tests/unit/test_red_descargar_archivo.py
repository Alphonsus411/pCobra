from __future__ import annotations

from collections import deque
from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.corelibs import red


class _Respuesta:
    def __init__(
        self,
        *,
        url: str = "https://permitido.test/archivo",
        chunks: tuple[bytes, ...] = (b"contenido",),
        status_code: int = 200,
        location: str | None = None,
    ) -> None:
        self.url = url
        self.status_code = status_code
        self.headers = {} if location is None else {"Location": location}
        self._chunks = chunks

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def raise_for_status(self) -> None:
        return None

    async def aiter_bytes(self, chunk_size: int = 8192):
        del chunk_size
        for chunk in self._chunks:
            yield chunk


class _Cliente:
    def __init__(self, respuestas: list[_Respuesta]) -> None:
        self.respuestas = deque(respuestas)
        self.llamadas: list[tuple[str, str, bool]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def stream(self, metodo: str, url: str, *, follow_redirects: bool, **_kwargs):
        self.llamadas.append((metodo, url, follow_redirects))
        return self.respuestas.popleft()


def _preparar(monkeypatch, tmp_path: Path, respuestas: list[_Respuesta]) -> _Cliente:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "permitido.test")
    cliente = _Cliente(respuestas)
    if red.httpx is None:
        monkeypatch.setattr(red, "httpx", SimpleNamespace())
    monkeypatch.setattr(
        red.httpx, "AsyncClient", lambda **_kwargs: cliente, raising=False
    )
    return cliente


@pytest.mark.asyncio
async def test_descarga_destino_valido_y_crea_directorios(monkeypatch, tmp_path):
    _preparar(monkeypatch, tmp_path, [_Respuesta()])

    destino = await red.descargar_archivo(
        "https://permitido.test/archivo", "subdirectorio/archivo.bin"
    )

    assert destino == tmp_path / "subdirectorio" / "archivo.bin"
    assert destino.read_bytes() == b"contenido"


@pytest.mark.asyncio
@pytest.mark.parametrize("destino", ["/tmp/archivo.bin", "../archivo.bin"])
async def test_descarga_rechaza_ruta_absoluta_y_traversal(
    monkeypatch, tmp_path, destino
):
    cliente = _preparar(monkeypatch, tmp_path, [_Respuesta()])

    with pytest.raises(ValueError):
        await red.descargar_archivo("https://permitido.test/archivo", destino)

    assert cliente.llamadas == []


@pytest.mark.asyncio
async def test_descarga_rechaza_symlink_saliente(monkeypatch, tmp_path):
    exterior = tmp_path.parent / f"{tmp_path.name}-exterior"
    exterior.mkdir()
    (tmp_path / "enlace").symlink_to(exterior, target_is_directory=True)
    cliente = _preparar(monkeypatch, tmp_path, [_Respuesta()])

    with pytest.raises(ValueError):
        await red.descargar_archivo(
            "https://permitido.test/archivo", "enlace/archivo.bin"
        )

    assert cliente.llamadas == []
    assert not (exterior / "archivo.bin").exists()


@pytest.mark.asyncio
async def test_fallo_por_tamano_preserva_archivo_previo(monkeypatch, tmp_path):
    destino = tmp_path / "archivo.bin"
    destino.write_bytes(b"original")
    _preparar(
        monkeypatch,
        tmp_path,
        [_Respuesta(chunks=(b"a" * red._MAX_RESP_SIZE, b"exceso"))],
    )

    with pytest.raises(ValueError, match="demasiado grande"):
        await red.descargar_archivo("https://permitido.test/archivo", "archivo.bin")

    assert destino.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destino]


@pytest.mark.asyncio
async def test_descarga_no_sigue_redireccion_por_defecto(monkeypatch, tmp_path):
    cliente = _preparar(
        monkeypatch,
        tmp_path,
        [_Respuesta(status_code=302, location="https://permitido.test/final")],
    )

    with pytest.raises(ValueError, match="Redirecciones no permitidas"):
        await red.descargar_archivo("https://permitido.test/inicio", "archivo.bin")

    assert cliente.llamadas == [("GET", "https://permitido.test/inicio", False)]
    assert not (tmp_path / "archivo.bin").exists()


@pytest.mark.asyncio
async def test_descarga_valida_cada_redireccion_autorizada(monkeypatch, tmp_path):
    cliente = _preparar(
        monkeypatch,
        tmp_path,
        [
            _Respuesta(status_code=302, location="https://permitido.test/final"),
            _Respuesta(url="https://permitido.test/final", chunks=(b"final",)),
        ],
    )

    destino = await red.descargar_archivo(
        "https://permitido.test/inicio",
        "archivo.bin",
        permitir_redirecciones=True,
    )

    assert destino.read_bytes() == b"final"
    assert cliente.llamadas == [
        ("GET", "https://permitido.test/inicio", False),
        ("GET", "https://permitido.test/final", False),
    ]


@pytest.mark.asyncio
async def test_descarga_rechaza_host_inicial_y_redireccion_no_permitidos(
    monkeypatch, tmp_path
):
    cliente = _preparar(monkeypatch, tmp_path, [_Respuesta()])
    with pytest.raises(ValueError, match="Host no permitido"):
        await red.descargar_archivo("https://otro.test/archivo", "inicial.bin")
    assert cliente.llamadas == []

    cliente.respuestas.clear()
    cliente.respuestas.append(
        _Respuesta(status_code=302, location="https://otro.test/final")
    )
    with pytest.raises(ValueError, match="Host no permitido"):
        await red.descargar_archivo(
            "https://permitido.test/inicio",
            "redireccion.bin",
            permitir_redirecciones=True,
        )
    assert len(cliente.llamadas) == 1
    assert not (tmp_path / "redireccion.bin").exists()


@pytest.mark.asyncio
async def test_descarga_rechaza_esquema_inicial_y_en_redireccion(
    monkeypatch, tmp_path
):
    cliente = _preparar(monkeypatch, tmp_path, [])
    with pytest.raises(ValueError, match="Esquema de URL no soportado"):
        await red.descargar_archivo("http://permitido.test/archivo", "inicial.bin")
    assert cliente.llamadas == []

    cliente.respuestas.append(
        _Respuesta(status_code=302, location="http://permitido.test/final")
    )
    with pytest.raises(ValueError, match="Esquema de URL no soportado"):
        await red.descargar_archivo(
            "https://permitido.test/inicio",
            "redireccion.bin",
            permitir_redirecciones=True,
        )
    assert len(cliente.llamadas) == 1
    assert not (tmp_path / "redireccion.bin").exists()
