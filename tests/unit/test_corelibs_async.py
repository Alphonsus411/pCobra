import asyncio

import pytest

import pcobra.corelibs.asincrono as asincrono
import pcobra.corelibs.red as red
import pcobra.corelibs.sistema as sistema


class _FakeStream:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeAsyncClient:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def stream(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self._responses.pop(0)
        return _FakeStream(response)


class _FakeResponse:
    def __init__(self, *, body=b"hola", url="https://example.com", headers=None):
        self.status_code = 200
        self.headers = headers or {}
        self.encoding = "utf-8"
        self.url = url
        self._body = body

    def raise_for_status(self):
        return None

    async def aiter_bytes(self, chunk_size=8192):
        yield self._body


@pytest.mark.asyncio
async def test_obtener_url_async(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")

    cliente = _FakeAsyncClient([_FakeResponse(body=b"hola", url="https://example.com")])

    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente)

    texto = await red.obtener_url_async("https://example.com")
    assert texto == "hola"
    assert cliente.calls[0][0] == "GET"


@pytest.mark.asyncio
async def test_descargar_archivo_async_elimina_si_falla(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")

    class _ResponseGrande(_FakeResponse):
        async def aiter_bytes(self, chunk_size=8192):
            yield b"a" * (red._MAX_RESP_SIZE + 1)

    cliente = _FakeAsyncClient([_ResponseGrande()])
    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente)

    destino = tmp_path / "archivo.bin"
    with pytest.raises(ValueError):
        await red.descargar_archivo("https://example.com", destino)
    assert not destino.exists()


@pytest.mark.asyncio
async def test_descargar_archivo_async(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    respuesta = _FakeResponse(body=b"contenido")
    cliente = _FakeAsyncClient([respuesta])
    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente)

    destino = tmp_path / "datos.bin"
    ruta = await red.descargar_archivo("https://example.com", destino)
    assert ruta.read_bytes() == b"contenido"


class _FakeProcBase:
    def __init__(self, *, stdout=b"", stderr=b"", returncode=0):
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode

    async def communicate(self):
        return self._stdout, self._stderr

    def kill(self):
        self.killed = True
        return None


@pytest.mark.asyncio
async def test_ejecutar_async_devuelve_stdout(monkeypatch):
    monkeypatch.setattr(sistema, "_resolver_ejecutable", lambda cmd, _: (cmd, "/bin/falso", 1))
    monkeypatch.setattr(sistema, "_verificar_inode", lambda *_args: None)

    async def fake_create(*_args, **_kwargs):
        return _FakeProcBase(stdout=b"ok", stderr=b"", returncode=0)

    async def fake_wait_for(awaitable, timeout=None):
        return await awaitable

    monkeypatch.setattr(sistema.asyncio, "create_subprocess_exec", fake_create)
    monkeypatch.setattr(sistema.asyncio, "wait_for", fake_wait_for)

    salida = await sistema.ejecutar_async(["cmd"], permitidos=["/bin/falso"])
    assert salida == "ok"


@pytest.mark.asyncio
async def test_ejecutar_async_retorna_stderr_en_error(monkeypatch):
    monkeypatch.setattr(sistema, "_resolver_ejecutable", lambda cmd, _: (cmd, "/bin/falso", 1))
    monkeypatch.setattr(sistema, "_verificar_inode", lambda *_args: None)

    async def fake_create(*_args, **_kwargs):
        return _FakeProcBase(stdout=b"", stderr=b"fallo", returncode=1)

    async def fake_wait_for(awaitable, timeout=None):
        return await awaitable

    monkeypatch.setattr(sistema.asyncio, "create_subprocess_exec", fake_create)
    monkeypatch.setattr(sistema.asyncio, "wait_for", fake_wait_for)

    salida = await sistema.ejecutar_async(["cmd"], permitidos=["/bin/falso"])
    assert salida == "fallo"


class _FakeStdout:
    def __init__(self, chunks):
        self._chunks = list(chunks)

    async def readline(self):
        if self._chunks:
            return self._chunks.pop(0)
        return b""


class _FakeStderr:
    def __init__(self, data=b""):
        self._data = data

    async def read(self):
        return self._data


class _FakeProcStream:
    def __init__(self, chunks, *, stderr=b"", returncode=0):
        self.stdout = _FakeStdout(chunks)
        self.stderr = _FakeStderr(stderr)
        self.returncode = returncode

    async def wait(self):
        return self.returncode

    def kill(self):
        self.killed = True
        return None


@pytest.mark.asyncio
async def test_ejecutar_stream_yield(monkeypatch):
    monkeypatch.setattr(sistema, "_resolver_ejecutable", lambda cmd, _: (cmd, "/bin/falso", 1))
    monkeypatch.setattr(sistema, "_verificar_inode", lambda *_args: None)

    async def fake_create(*_args, **_kwargs):
        return _FakeProcStream([b"uno\n", b"dos\n"], stderr=b"", returncode=0)

    async def fake_wait_for(awaitable, timeout=None):
        return await awaitable

    class _Loop:
        def time(self):
            return 0.0

    monkeypatch.setattr(sistema.asyncio, "create_subprocess_exec", fake_create)
    monkeypatch.setattr(sistema.asyncio, "wait_for", fake_wait_for)
    monkeypatch.setattr(sistema.asyncio, "get_running_loop", lambda: _Loop())

    chunks = []
    async for parte in sistema.ejecutar_stream(["cmd"], permitidos=["/bin/falso"]):
        chunks.append(parte)
    assert chunks == ["uno\n", "dos\n"]


@pytest.mark.asyncio
async def test_ejecutar_stream_error_provoca_excepcion(monkeypatch):
    monkeypatch.setattr(sistema, "_resolver_ejecutable", lambda cmd, _: (cmd, "/bin/falso", 1))
    monkeypatch.setattr(sistema, "_verificar_inode", lambda *_args: None)

    async def fake_create(*_args, **_kwargs):
        return _FakeProcStream([b"salida\n"], stderr=b"fallo", returncode=1)

    async def fake_wait_for(awaitable, timeout=None):
        return await awaitable

    class _Loop:
        def time(self):
            return 0.0

    monkeypatch.setattr(sistema.asyncio, "create_subprocess_exec", fake_create)
    monkeypatch.setattr(sistema.asyncio, "wait_for", fake_wait_for)
    monkeypatch.setattr(sistema.asyncio, "get_running_loop", lambda: _Loop())

    gen = sistema.ejecutar_stream(["cmd"], permitidos=["/bin/falso"])
    with pytest.raises(RuntimeError) as excinfo:
        async for _ in gen:
            pass
    assert "fallo" in str(excinfo.value)


@pytest.mark.asyncio
async def test_recolectar_retorna_valores_en_orden():
    async def producir(valor, demora):
        await asyncio.sleep(demora)
        return valor

    resultado = await asincrono.recolectar(producir("uno", 0.01), producir("dos", 0.02))
    assert resultado == ["uno", "dos"]


@pytest.mark.asyncio
async def test_recolectar_cancela_al_fallar():
    cancelada = asyncio.Event()

    async def fallar():
        await asyncio.sleep(0.01)
        raise RuntimeError("boom")

    async def lenta():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    with pytest.raises(RuntimeError):
        await asincrono.recolectar(fallar(), lenta())
    assert cancelada.is_set()


@pytest.mark.asyncio
async def test_carrera_devuelve_primer_resultado():
    cancelada = asyncio.Event()

    async def rapida():
        await asyncio.sleep(0.01)
        return "ok"

    async def lenta():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    resultado = await asincrono.carrera(rapida(), lenta())
    assert resultado == "ok"
    assert cancelada.is_set()


@pytest.mark.asyncio
async def test_carrera_propaga_excepcion_y_cancela():
    cancelada = asyncio.Event()

    async def fallar():
        await asyncio.sleep(0.01)
        raise ValueError("fallo")

    async def lenta():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    with pytest.raises(ValueError):
        await asincrono.carrera(fallar(), lenta())
    assert cancelada.is_set()


@pytest.mark.asyncio
async def test_esperar_timeout_devuelve_resultado():
    resultado = await asincrono.esperar_timeout(asyncio.sleep(0.01, result="hecho"), 0.5)
    assert resultado == "hecho"


@pytest.mark.asyncio
async def test_esperar_timeout_cancela_en_exceso():
    cancelada = asyncio.Event()

    async def lenta():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    with pytest.raises(asyncio.TimeoutError):
        await asincrono.esperar_timeout(lenta(), 0.01)
    assert cancelada.is_set()


@pytest.mark.asyncio
async def test_crear_tarea_envuelve_corrutinas():
    async def producir():
        await asyncio.sleep(0)
        return 42

    tarea = asincrono.crear_tarea(producir())
    assert isinstance(tarea, asyncio.Task)
    assert await tarea == 42


@pytest.mark.asyncio
async def test_crear_tarea_reutiliza_tareas_existentes():
    async def producir():
        await asyncio.sleep(0)
        return "ok"

    original = asyncio.create_task(producir())
    reutilizada = asincrono.crear_tarea(original)
    assert reutilizada is original
    assert await reutilizada == "ok"
