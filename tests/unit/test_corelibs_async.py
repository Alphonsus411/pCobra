import asyncio
import functools

import os
from types import SimpleNamespace

import pytest

import pcobra.corelibs.asincrono as asincrono
import pcobra.corelibs.red as red
import pcobra.corelibs.sistema as sistema


@pytest.mark.asyncio
async def test_iterar_completadas_respeta_orden_de_finalizacion():
    async def tarea(valor, espera):
        await asyncio.sleep(espera)
        return valor

    resultados = [
        resultado
        async for resultado in asincrono.iterar_completadas(
            tarea("lento", 0.03),
            tarea("rapido", 0.0),
            tarea("medio", 0.01),
        )
    ]

    assert resultados == ["rapido", "medio", "lento"]


@pytest.mark.asyncio
async def test_proteger_tarea_no_provoca_cancelacion_de_trabajo():
    cancelada = False

    async def tarea_lenta():
        nonlocal cancelada
        try:
            await asyncio.sleep(0.01)
            return "ok"
        except asyncio.CancelledError:
            cancelada = True
            raise

    original = asyncio.create_task(tarea_lenta())
    protegida = asincrono.proteger_tarea(original)

    assert protegida is not original

    protegida.cancel()
    await asyncio.sleep(0)

    assert not original.cancelled()

    resultado = await original
    assert resultado == "ok"
    assert not cancelada


@pytest.mark.asyncio
async def test_proteger_tarea_acepta_corutinas_directas():
    resultado = await asincrono.proteger_tarea(asyncio.sleep(0, result=42))

    assert resultado == 42


@pytest.mark.asyncio
async def test_limitar_tiempo_permite_finalizar():
    async with asincrono.limitar_tiempo(0.05):
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_limitar_tiempo_expira_con_mensaje_y_cancela_tarea():
    cancelada = False

    async def tarea_lenta():
        nonlocal cancelada
        try:
            await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            cancelada = True
            raise

    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with asincrono.limitar_tiempo(0.01, mensaje="agotado"):
            await tarea_lenta()

    assert "agotado" in str(excinfo.value)
    assert cancelada


@pytest.mark.asyncio
async def test_limitar_tiempo_funciona_sin_asyncio_timeout(monkeypatch):
    monkeypatch.delattr(asincrono.asyncio, "timeout", raising=False)

    async def tarea_lenta():
        await asyncio.sleep(0.05)

    with pytest.raises(asyncio.TimeoutError):
        async with asincrono.limitar_tiempo(0.01):
            await tarea_lenta()


@pytest.mark.asyncio
async def test_ejecutar_en_hilo_prefiere_to_thread(monkeypatch):
    llamado = {}

    async def falso_to_thread(funcion, *args, **kwargs):
        llamado["args"] = args
        llamado["kwargs"] = kwargs
        return funcion(*args, **kwargs)

    monkeypatch.setattr(asincrono.asyncio, "to_thread", falso_to_thread)

    resultado = await asincrono.ejecutar_en_hilo(lambda x, y=0: x + y, 1, y=2)

    assert resultado == 3
    assert llamado["args"] == (1,)
    assert llamado["kwargs"] == {"y": 2}


@pytest.mark.asyncio
async def test_ejecutar_en_hilo_degrada_a_run_in_executor(monkeypatch):
    loop = asyncio.get_running_loop()
    original = loop.run_in_executor
    llamado = {}

    def falso_run_in_executor(executor, funcion, *args):
        llamado["executor"] = executor
        llamado["funcion"] = funcion
        llamado["args"] = args
        return original(executor, funcion, *args)

    monkeypatch.setattr(loop, "run_in_executor", falso_run_in_executor)
    monkeypatch.delattr(asincrono.asyncio, "to_thread", raising=False)

    resultado = await asincrono.ejecutar_en_hilo(lambda x, *, y: x + y, 1, y=2)

    assert resultado == 3
    assert llamado["executor"] is None
    assert isinstance(llamado["funcion"], functools.partial)
    assert llamado["args"] == ()


@pytest.mark.asyncio
async def test_iterar_completadas_cancela_pendientes_en_error():
    cancelada = asyncio.Event()

    async def exitosa():
        await asyncio.sleep(0.005)
        return "ok"

    async def fallida():
        await asyncio.sleep(0.01)
        raise RuntimeError("boom")

    async def larga():
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    resultados = []
    with pytest.raises(RuntimeError):
        async for resultado in asincrono.iterar_completadas(
            exitosa(), fallida(), larga()
        ):
            resultados.append(resultado)

    assert resultados == ["ok"]
    assert cancelada.is_set()


@pytest.mark.asyncio
async def test_primero_exitoso_devuelve_primer_resultado_sin_excepcion():
    async def fallida():
        await asyncio.sleep(0.005)
        raise RuntimeError("fallo")

    async def exitosa():
        await asyncio.sleep(0.01)
        return "hecho"

    resultado = await asincrono.primero_exitoso(fallida(), exitosa())

    assert resultado == "hecho"


@pytest.mark.asyncio
async def test_primero_exitoso_agrupar_errores_si_todo_falla():
    async def fallida(mensaje):
        await asyncio.sleep(0.0)
        raise ValueError(mensaje)

    with pytest.raises(ExceptionGroup) as excinfo:
        await asincrono.primero_exitoso(fallida("uno"), fallida("dos"))

    assert len(excinfo.value.exceptions) == 2
    assert {type(ex) for ex in excinfo.value.exceptions} == {ValueError}


@pytest.mark.asyncio
async def test_mapear_concurrencia_respeta_limite():
    contador = 0
    maximo = 0
    candado = asyncio.Lock()

    def construir(indice):
        async def tarea():
            nonlocal contador, maximo
            async with candado:
                contador += 1
                maximo = max(maximo, contador)
            try:
                await asyncio.sleep(0.001)
                return indice
            finally:
                async with candado:
                    contador -= 1

        return tarea

    funciones = [construir(i) for i in range(5)]
    resultados = await asincrono.mapear_concurrencia(funciones, limite=2)

    assert resultados == list(range(5))
    assert maximo <= 2


@pytest.mark.asyncio
async def test_mapear_concurrencia_return_exceptions():
    def fallida():
        async def tarea():
            await asyncio.sleep(0)
            raise RuntimeError("boom")

        return tarea

    def exitosa(valor):
        async def tarea():
            await asyncio.sleep(0)
            return valor

        return tarea

    funciones = [fallida(), exitosa("ok")]
    resultados = await asincrono.mapear_concurrencia(
        funciones, limite=3, return_exceptions=True
    )

    assert isinstance(resultados[0], RuntimeError)
    assert resultados[1] == "ok"


@pytest.mark.asyncio
async def test_recolectar_resultados_reporta_estados():
    cancelada = asyncio.Event()

    async def exitosa():
        await asyncio.sleep(0.0)
        return 42

    async def fallida():
        await asyncio.sleep(0.0)
        raise ValueError("error")

    async def cancelable():
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            cancelada.set()
            raise

    tarea_cancelada = asyncio.create_task(cancelable())
    await asyncio.sleep(0)
    tarea_cancelada.cancel()
    await asyncio.sleep(0)

    estados = await asincrono.recolectar_resultados(
        exitosa(), fallida(), tarea_cancelada
    )

    assert estados[0]["estado"] == "cumplida"
    assert estados[0]["resultado"] == 42
    assert estados[0]["excepcion"] is None

    assert estados[1]["estado"] == "rechazada"
    assert isinstance(estados[1]["excepcion"], ValueError)

    assert estados[2]["estado"] == "cancelada"
    assert estados[2]["resultado"] is None
    assert isinstance(estados[2]["excepcion"], asyncio.CancelledError)
    assert cancelada.is_set()


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

    if red.httpx is None:
        monkeypatch.setattr(red, "httpx", SimpleNamespace())
    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente, raising=False)

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
    if red.httpx is None:
        monkeypatch.setattr(red, "httpx", SimpleNamespace())
    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente, raising=False)

    destino = tmp_path / "archivo.bin"
    with pytest.raises(ValueError):
        await red.descargar_archivo("https://example.com", destino)
    assert not destino.exists()


@pytest.mark.asyncio
async def test_descargar_archivo_async(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    respuesta = _FakeResponse(body=b"contenido")
    cliente = _FakeAsyncClient([respuesta])
    if red.httpx is None:
        monkeypatch.setattr(red, "httpx", SimpleNamespace())
    monkeypatch.setattr(red.httpx, "AsyncClient", lambda **_kwargs: cliente, raising=False)

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
    def fake_resolver(cmd, _):
        args = list(cmd)
        args[0] = "/bin/falso"
        fd = os.open(os.devnull, os.O_RDONLY)
        return args, "/bin/falso", fd, 0, 0

    monkeypatch.setattr(sistema, "_resolver_ejecutable", fake_resolver)
    monkeypatch.setattr(sistema, "_verificar_descriptor", lambda *_args: None)
    monkeypatch.setattr(sistema, "_verificar_ruta", lambda *_args: None)

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
    def fake_resolver(cmd, _):
        args = list(cmd)
        args[0] = "/bin/falso"
        fd = os.open(os.devnull, os.O_RDONLY)
        return args, "/bin/falso", fd, 0, 0

    monkeypatch.setattr(sistema, "_resolver_ejecutable", fake_resolver)
    monkeypatch.setattr(sistema, "_verificar_descriptor", lambda *_args: None)
    monkeypatch.setattr(sistema, "_verificar_ruta", lambda *_args: None)

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
    def fake_resolver(cmd, _):
        args = list(cmd)
        args[0] = "/bin/falso"
        fd = os.open(os.devnull, os.O_RDONLY)
        return args, "/bin/falso", fd, 0, 0

    monkeypatch.setattr(sistema, "_resolver_ejecutable", fake_resolver)
    monkeypatch.setattr(sistema, "_verificar_descriptor", lambda *_args: None)
    monkeypatch.setattr(sistema, "_verificar_ruta", lambda *_args: None)

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
    def fake_resolver(cmd, _):
        args = list(cmd)
        args[0] = "/bin/falso"
        fd = os.open(os.devnull, os.O_RDONLY)
        return args, "/bin/falso", fd, 0, 0

    monkeypatch.setattr(sistema, "_resolver_ejecutable", fake_resolver)
    monkeypatch.setattr(sistema, "_verificar_descriptor", lambda *_args: None)
    monkeypatch.setattr(sistema, "_verificar_ruta", lambda *_args: None)

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
