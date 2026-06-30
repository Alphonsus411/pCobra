from io import StringIO
from unittest.mock import patch, MagicMock
import os
import sys
from types import ModuleType
import hashlib
import pytest
import requests

dummy = ModuleType("tree_sitter_languages")
dummy.get_parser = lambda *args, **kwargs: None
sys.modules.setdefault("tree_sitter_languages", dummy)

from cobra.cli.commands import modules_cmd  # noqa: E402
from cobra.cli import cobrahub_client  # noqa: E402


class _PatchedSession:
    """Sesión mínima que redirige a ``requests`` real para los tests."""

    def get(self, *args, **kwargs):
        resp = cobrahub_client.requests.get(*args, **kwargs)

        if "headers" not in getattr(resp, "__dict__", {}):
            resp.headers = {}

        iter_content_attr = getattr(resp, "iter_content", None)
        if isinstance(iter_content_attr, MagicMock) or iter_content_attr is None:
            content = getattr(resp, "content", b"")
            resp.iter_content = lambda chunk_size: [content]

        if isinstance(getattr(resp, "__enter__", None), MagicMock):
            resp.__enter__ = lambda *a, **k: resp
        if isinstance(getattr(resp, "__exit__", None), MagicMock) or not hasattr(
            resp, "__exit__"
        ):
            resp.__exit__ = lambda *a, **k: False

        return resp

    def post(self, *args, **kwargs):
        return cobrahub_client.requests.post(*args, **kwargs)


@pytest.fixture(autouse=True)
def _use_patched_session(monkeypatch):
    """Fuerza que los clientes usen la sesión parcheada durante las pruebas."""

    original = cobrahub_client.CobraHubClient._configurar_sesion

    def _factory(self):
        return _PatchedSession()

    monkeypatch.setattr(cobrahub_client.CobraHubClient, "_configurar_sesion", _factory)
    monkeypatch.setattr(
        cobrahub_client, "_original_configurar_sesion", original, raising=False
    )

    if modules_cmd.yaml is None and "yaml" in sys.modules:
        modules_cmd.yaml = sys.modules["yaml"]

    session = _PatchedSession()
    monkeypatch.setattr(modules_cmd.client, "session", session)
    return session


def test_configurar_sesion_real_crea_sesion():
    original = getattr(cobrahub_client, "_original_configurar_sesion", None)
    assert original is not None, "La sesión real debe estar disponible para las pruebas"

    cliente = cobrahub_client.CobraHubClient.__new__(cobrahub_client.CobraHubClient)
    sesion = original(cliente)

    try:
        assert hasattr(sesion, "get")
        assert hasattr(sesion, "post")
    finally:
        sesion.close()


@pytest.mark.timeout(5)
def test_cli_modulos_publicar(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    args = type("obj", (), {"accion": "publicar", "ruta": str(archivo)})
    with (
        patch("cobra.cli.cobrahub_client.requests.post") as mock_post,
        patch("sys.stdout", new_callable=StringIO) as out,
    ):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        ret = modules_cmd.ModulesCommand().run(args)
    assert ret == 0
    assert "Módulo publicado correctamente" in out.getvalue().strip()
    mock_post.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_modulos_buscar(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", mods_dir)
    mod_file = tmp_path / "module_map.toml"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", mod_file)
    args = type("obj", (), {"accion": "buscar", "nombre": "remote.co"})
    with (
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
        patch("sys.stdout", new_callable=StringIO) as out,
    ):
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.content = b"data"
        response.url = f"{cobrahub_client.COBRAHUB_URL}/modulos/remote.co"
        mock_get.return_value = response
        ret = modules_cmd.ModulesCommand().run(args)
    archivo = mods_dir / "remote.co"
    assert archivo.exists()
    assert archivo.read_bytes() == b"data"
    assert ret == 0
    assert f"Módulo descargado en {archivo}" in out.getvalue().strip()
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_publicar_modulo_url_insegura(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.post") as mock_post,
    ):
        ok = cobrahub_client.publicar_modulo(str(mod))
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_url_insegura(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_absoluta(tmp_path):
    destino = tmp_path / "m.co"
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", str(destino))
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_traversal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "../salir.co"
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_parent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "../"
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_tmp_espacios():
    destino = "/tmp/proyecto falso"
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_valida(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "mods/m.co"
    (tmp_path / "mods").mkdir()
    with patch("cobra.cli.cobrahub_client.requests.get") as mock_get:
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.content = b"x"
        resp.url = f"{cobrahub_client.COBRAHUB_URL}/modulos/m.co"
        mock_get.return_value = resp
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert ok
    archivo = tmp_path / destino
    assert archivo.exists()
    assert archivo.read_bytes() == b"x"
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_absoluta_en_base(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / "mods"
    base.mkdir()
    destino = base / "m.co"

    with patch("cobra.cli.cobrahub_client.requests.get") as mock_get:
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.content = b"x"
        resp.headers = {}
        resp.url = f"{cobrahub_client.COBRAHUB_URL}/modulos/m.co"
        mock_get.return_value = resp
        ok = cobrahub_client.descargar_modulo(
            "m.co", str(destino), base_permitida=str(base)
        )

    assert ok
    assert destino.exists()
    assert destino.read_bytes() == b"x"
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_parent_fuera_base(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / "mods"
    base.mkdir()
    destino = base / ".." / "escape" / "m.co"

    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo(
            "m.co", str(destino), base_permitida=str(base)
        )

    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_symlink_fuera_base(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / "mods"
    base.mkdir()
    externo = tmp_path / "externo"
    externo.mkdir()
    destino_real = externo / "fuera.co"
    destino_real.write_text("")
    enlace = base / "link.co"
    os.symlink(destino_real, enlace)

    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo(
            "m.co", str(enlace), base_permitida=str(base)
        )

    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_streaming_con_checksum(tmp_path, monkeypatch):
    """Las descargas grandes deben usar streaming y validar encabezados."""

    monkeypatch.chdir(tmp_path)
    destino = "mods/m.co"
    (tmp_path / "mods").mkdir()

    client = cobrahub_client.CobraHubClient()

    chunks = [b"a" * client.CHUNK_SIZE, b"b" * 128]
    sha = hashlib.sha256()
    for chunk in chunks:
        sha.update(chunk)
    checksum = sha.hexdigest()

    class _StreamingResponse:
        def __init__(self):
            self.iter_calls = []
            self.closed = False
            self.headers = MagicMock()
            self.headers.get.return_value = checksum
            self.url = f"{client.base_url}/modulos/m.co"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.closed = True
            return False

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            self.iter_calls.append(chunk_size)
            for part in chunks:
                yield part

        def close(self):
            self.closed = True

        @property
        def content(self):  # pragma: no cover - asegura que no se use ``content``
            raise AssertionError("La descarga debe procesarse en streaming")

    response = _StreamingResponse()
    client.session.get = MagicMock(return_value=response)

    ok = client.descargar_modulo("m.co", destino)

    assert ok
    archivo = tmp_path / destino
    assert archivo.read_bytes() == b"".join(chunks)
    client.session.get.assert_called_once()
    assert client.session.get.call_args.kwargs["stream"] is True
    assert response.iter_calls == [client.CHUNK_SIZE]
    response.headers.get.assert_called_once_with("X-Content-Checksum")
    assert response.closed is True


@pytest.mark.timeout(5)
def test_descargar_modulo_redireccion_host_no_autorizado(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "mods").mkdir()
    destino = "mods/m.co"

    monkeypatch.setenv("COBRA_HOST_WHITELIST", "cobrahub.example.com")

    client = cobrahub_client.CobraHubClient()

    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [b"datos"]
    response.headers = {}
    response.url = "https://malicioso.example.com/modulos/m.co"
    response.close = MagicMock()

    client.session.get = MagicMock(return_value=response)

    with patch("cobra.cli.cobrahub_client.mostrar_error") as err:
        ok = client.descargar_modulo("m.co", destino)

    assert not ok
    err.assert_called_once()
    response.close.assert_called_once()
    client.session.get.assert_called_once()
    assert not (tmp_path / destino).exists()


@pytest.mark.timeout(5)
def test_descargar_modulo_whitelist_insensible_mayusculas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "mods").mkdir()
    destino = "mods/m.co"

    monkeypatch.setenv("COBRA_HOST_WHITELIST", "COBRAHUB.EXAMPLE.COM")
    monkeypatch.setenv("COBRAHUB_URL", "https://Cobrahub.Example.com/api")

    client = cobrahub_client.CobraHubClient()

    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [b"datos"]
    response.headers = {}
    response.url = "https://COBRAHUB.EXAMPLE.COM/modulos/m.co"

    client.session.get = MagicMock(return_value=response)

    ok = client.descargar_modulo("m.co", destino)

    assert ok
    archivo = tmp_path / destino
    assert archivo.exists()
    assert archivo.read_bytes() == b"datos"
    client.session.get.assert_called_once()


@pytest.mark.timeout(5)
def test_publicar_modulo_permission_error(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.post") as mock_post,
        patch("builtins.open", side_effect=PermissionError),
    ):
        ok = cobrahub_client.publicar_modulo(str(archivo))
    assert not ok
    err.assert_called_once()
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_publicar_modulo_duplicado(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    client = cobrahub_client.CobraHubClient()
    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.side_effect = lambda *args: response.close()
    error_resp = MagicMock()
    error_resp.status_code = 409
    http_error = requests.exceptions.HTTPError(response=error_resp)
    response.raise_for_status.side_effect = http_error
    client.session.post = MagicMock(return_value=response)
    with patch("cobra.cli.cobrahub_client.mostrar_info") as info:
        ok = client.publicar_modulo(str(archivo))
    assert ok
    info.assert_called_once()
    client.session.post.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_permission_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
        patch("builtins.open", side_effect=PermissionError),
    ):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.content = b"data"
        resp.url = f"{cobrahub_client.COBRAHUB_URL}/modulos/m.co"
        mock_get.return_value = resp
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_symlink(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino_real = tmp_path / "real.co"
    destino_real.write_text("")
    enlace = tmp_path / "link.co"
    enlace.symlink_to(destino_real)
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", str(enlace))
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_publicar_modulo_host_no_permitido(tmp_path, monkeypatch):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "cobrahub.example.com")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "https://otro.com/api")
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.post") as mock_post,
    ):
        ok = cobrahub_client.publicar_modulo(str(archivo))
    assert not ok
    err.assert_called_once()
    assert "Host" in err.call_args[0][0]
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_host_no_permitido(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "cobrahub.example.com")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "https://otro.com/api")
    with (
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    assert "Host" in err.call_args[0][0]
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_get_validated_base_url_prioriza_parametro_sobre_entorno(monkeypatch):
    monkeypatch.setenv("COBRAHUB_URL", "https://entorno.example.com/api")

    client = cobrahub_client.CobraHubClient(
        base_url="https://inyectada.example.com/api"
    )

    assert client.base_url == "https://inyectada.example.com/api"


@pytest.mark.timeout(5)
def test_funciones_conveniencia_no_modifican_cobrahub_url_en_entorno(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("COBRAHUB_URL", raising=False)
    monkeypatch.setattr(
        cobrahub_client, "COBRAHUB_URL", "https://inyectada.example.com/api"
    )

    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")

    with (
        patch("cobra.cli.cobrahub_client.requests.post") as mock_post,
        patch("cobra.cli.cobrahub_client.requests.get") as mock_get,
    ):
        post_resp = MagicMock()
        post_resp.__enter__.return_value = post_resp
        post_resp.__exit__.return_value = False
        post_resp.raise_for_status.return_value = None
        mock_post.return_value = post_resp

        get_resp = MagicMock()
        get_resp.__enter__.return_value = get_resp
        get_resp.__exit__.return_value = False
        get_resp.raise_for_status.return_value = None
        get_resp.iter_content = lambda chunk_size: [b"ok"]
        get_resp.headers = {}
        get_resp.url = "https://inyectada.example.com/api/modulos/m.co"
        mock_get.return_value = get_resp

        assert cobrahub_client.publicar_modulo(str(archivo))
        assert "COBRAHUB_URL" not in os.environ

        destino = tmp_path / "out.co"
        assert cobrahub_client.descargar_modulo(
            "m.co", str(destino), base_permitida=str(tmp_path)
        )
        assert "COBRAHUB_URL" not in os.environ


def test_metodos_paquete_estan_definidos_en_clase():
    assert "publicar_paquete" in cobrahub_client.CobraHubClient.__dict__
    assert "buscar_paquetes" in cobrahub_client.CobraHubClient.__dict__
    assert "instalar_paquete" in cobrahub_client.CobraHubClient.__dict__
    assert not hasattr(cobrahub_client, "_publicar_paquete")
    assert not hasattr(cobrahub_client, "_buscar_paquetes")
    assert not hasattr(cobrahub_client, "_instalar_paquete")


def test_buscar_paquetes_usa_metodo_real_de_clase(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def raise_for_status(self):
            return None

        def json(self):
            return {"results": [{"name": "demo", "version": "1.0.0"}]}

    class Session:
        def get(self, url, params, timeout):
            assert url == "https://cobrahub.example.com/api/paquetes"
            assert params == {"q": "demo"}
            assert timeout == (
                cobrahub_client.CobraHubClient.CONNECT_TIMEOUT,
                cobrahub_client.CobraHubClient.READ_TIMEOUT,
            )
            return Response()

    monkeypatch.setattr(
        cobrahub_client.CobraHubClient,
        "_configurar_sesion",
        lambda self: Session(),
    )

    client = cobrahub_client.CobraHubClient()

    assert client.buscar_paquetes("demo") == [{"name": "demo", "version": "1.0.0"}]


class _PackageStreamingResponse:
    def __init__(self, client, chunks, checksum=None):
        self.client = client
        self.chunks = chunks
        self.headers = {}
        if checksum is not None:
            self.headers["X-Content-Checksum"] = checksum
        self.iter_calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        self.iter_calls.append(chunk_size)
        yield from self.chunks

    @property
    def content(self):  # pragma: no cover - asegura que se use streaming
        raise AssertionError("La instalación debe descargar el paquete en streaming")


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

@pytest.mark.timeout(5)
def test_buscar_paquetes_normaliza_metadatos_disponibles(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {
                        "nombre": "demo",
                        "version": "2.0.0",
                        "archivo": "demo-2.0.0.co",
                        "sha256": "abc123",
                        "url": "https://example.test/demo-2.0.0.co",
                        "id": "pkg-1",
                    }
                ]
            }

    class Session:
        def get(self, url, params, timeout):
            return Response()

    monkeypatch.setattr(
        cobrahub_client.CobraHubClient,
        "_configurar_sesion",
        lambda self: Session(),
    )

    client = cobrahub_client.CobraHubClient()

    assert client.buscar_paquetes("demo") == [
        {
            "name": "demo",
            "version": "2.0.0",
            "filename": "demo-2.0.0.co",
            "checksum": "abc123",
            "download_url": "https://example.test/demo-2.0.0.co",
            "remote_id": "pkg-1",
        }
    ]


@pytest.mark.timeout(5)
def test_instalar_paquete_cache_versionada_si_servidor_entrega_version(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    install_dir = tmp_path / "instalados"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("COBRAHUB_INSTALL_DIR", str(install_dir))

    client = cobrahub_client.CobraHubClient()
    contenido = b"paquete-versionado"
    response = _PackageStreamingResponse(client, [contenido], _sha256_bytes(contenido))
    response.headers["X-Package-Version"] = "2.1.0"
    client.session.get = MagicMock(return_value=response)

    with patch("pcobra.cobra.packaging.extraer_paquete") as extraer:
        ok = client.instalar_paquete("demo")

    assert ok
    cache_path = cache_dir / "demo-2.1.0.co"
    assert cache_path.read_bytes() == contenido
    assert not (cache_dir / "demo.co").exists()
    extraer.assert_called_once_with(cache_path, install_dir / "demo")


@pytest.mark.timeout(5)
def test_instalar_paquete_cache_legacy_si_servidor_no_entrega_version(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    install_dir = tmp_path / "instalados"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("COBRAHUB_INSTALL_DIR", str(install_dir))

    client = cobrahub_client.CobraHubClient()
    contenido = b"paquete-legacy"
    response = _PackageStreamingResponse(client, [contenido], _sha256_bytes(contenido))
    client.session.get = MagicMock(return_value=response)

    with patch("pcobra.cobra.packaging.extraer_paquete") as extraer:
        ok = client.instalar_paquete("demo")

    assert ok
    cache_path = cache_dir / "demo.co"
    assert cache_path.read_bytes() == contenido
    extraer.assert_called_once_with(cache_path, install_dir / "demo")


@pytest.mark.timeout(5)
def test_instalar_paquete_descarga_valida(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    install_dir = tmp_path / "instalados"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("COBRAHUB_INSTALL_DIR", str(install_dir))

    client = cobrahub_client.CobraHubClient()
    chunks = [b"paquete-", b"valido"]
    contenido = b"".join(chunks)
    response = _PackageStreamingResponse(client, chunks, _sha256_bytes(contenido))
    client.session.get = MagicMock(return_value=response)

    with patch("pcobra.cobra.packaging.extraer_paquete") as extraer:
        ok = client.instalar_paquete("demo")

    assert ok
    cache_path = cache_dir / "demo.co"
    assert cache_path.read_bytes() == contenido
    extraer.assert_called_once_with(cache_path, install_dir / "demo")
    client.session.get.assert_called_once()
    assert client.session.get.call_args.kwargs["stream"] is True
    assert response.iter_calls == [client.CHUNK_SIZE]


@pytest.mark.timeout(5)
def test_instalar_paquete_descarga_demasiado_grande(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))

    client = cobrahub_client.CobraHubClient()
    monkeypatch.setattr(client, "MAX_FILE_SIZE", 4)
    response = _PackageStreamingResponse(client, [b"123", b"45"])
    client.session.get = MagicMock(return_value=response)

    with (
        patch("pcobra.cobra.packaging.extraer_paquete") as extraer,
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
    ):
        ok = client.instalar_paquete("demo")

    assert not ok
    assert not (cache_dir / "demo.co").exists()
    extraer.assert_not_called()
    err.assert_called_once()


@pytest.mark.timeout(5)
def test_instalar_paquete_checksum_incorrecto(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))

    client = cobrahub_client.CobraHubClient()
    response = _PackageStreamingResponse(client, [b"contenido"], "0" * 64)
    client.session.get = MagicMock(return_value=response)

    with (
        patch("pcobra.cobra.packaging.extraer_paquete") as extraer,
        patch("cobra.cli.cobrahub_client.mostrar_error") as err,
    ):
        ok = client.instalar_paquete("demo")

    assert not ok
    assert not (cache_dir / "demo.co").exists()
    extraer.assert_not_called()
    err.assert_called_once()


@pytest.mark.timeout(5)
def test_instalar_paquete_limpia_cache_parcial(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(cache_dir))

    client = cobrahub_client.CobraHubClient()

    class _ResponseConFallo(_PackageStreamingResponse):
        def iter_content(self, chunk_size):
            self.iter_calls.append(chunk_size)
            yield b"parcial"
            raise RuntimeError("conexión interrumpida")

    response = _ResponseConFallo(client, [])
    client.session.get = MagicMock(return_value=response)

    with patch("pcobra.cobra.packaging.extraer_paquete") as extraer:
        ok = client.instalar_paquete("demo")

    assert not ok
    assert not (cache_dir / "demo.co").exists()
    extraer.assert_not_called()
