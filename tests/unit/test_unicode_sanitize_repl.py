from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    SafeFileHistory,
)
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        ignore_memory_limit=True,
        debug=False,
        memory_limit=InteractiveCommand.MEMORY_LIMIT_MB,
    )


def test_sanitize_input_multilingue_y_emoji_se_conserva():
    texto = "Español العربية हिंदी 日本語 🚀"

    assert sanitize_input(texto) == texto


def test_sanitize_input_surrogate_alto_suelto_se_reemplaza():
    assert sanitize_input("\ud83d") == "�"


def test_sanitize_input_surrogate_bajo_suelto_se_reemplaza():
    assert sanitize_input("\udc00") == "�"


def test_sanitize_input_par_valido_se_conserva():
    # Par surrogate válido (U+1F680 ROCKET)
    texto = "\ud83d\ude80"

    assert sanitize_input(texto) == "🚀"


def test_sanitize_input_mezcla_unicode_valido_y_surrogate_invalido():
    texto = "áéíóú 🚀\ud83d"

    saneado = sanitize_input(texto)

    # Se preserva el Unicode válido visible y el surrogate roto se reemplaza.
    assert saneado == "áéíóú 🚀�"
    # No deben quedar surrogates aislados internamente.
    assert all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in saneado)
    # Debe poder codificarse a UTF-8 sin UnicodeEncodeError.
    assert saneado.encode("utf-8") == "áéíóú 🚀�".encode("utf-8")


def test_interactive_command_sanitiza_surrogate_invalido_y_no_crashea(tmp_path):
    cmd = InteractiveCommand(MagicMock())
    capturado = {"history": [], "validar": []}
    entrada_rota = "\ud83d"

    class DummySafeHistory:
        def __init__(self, _path: str) -> None:
            self.path = _path

        def append_string(self, value: str) -> None:
            saneado = sanitize_input(value)
            if "\ud83d" in saneado or "\udc00" in saneado:
                raise UnicodeEncodeError("utf-8", saneado, 0, 1, "surrogates not allowed")
            capturado["history"].append(saneado)

    class DummyPromptSession:
        def __init__(self, *args, **kwargs) -> None:
            self.history = kwargs["history"]
            self._calls = 0

        def prompt(self, _prompt: str) -> str:
            self._calls += 1
            if self._calls == 1:
                # Simula flujo real: la sesión intenta persistir la línea leída.
                self.history.append_string(entrada_rota)
                return entrada_rota
            return "salir"

    with patch("pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias"), \
         patch("pcobra.cobra.cli.commands.interactive_cmd.limitar_memoria_mb"), \
         patch("pcobra.cobra.cli.commands.interactive_cmd.os.path.expanduser", return_value=str(tmp_path / ".cobra_history")), \
         patch("pcobra.cobra.cli.commands.interactive_cmd.SafeFileHistory", DummySafeHistory), \
         patch("pcobra.cobra.cli.commands.interactive_cmd.PromptSession", DummyPromptSession), \
         patch.object(cmd, "validar_entrada", side_effect=lambda linea: capturado["validar"].append(linea) or True), \
         patch.object(cmd, "_procesar_comando_especial", return_value=False), \
         patch.object(cmd, "_actualizar_buffer_y_obtener_codigo_listo", return_value=None):
        ret = cmd.run(_args())

    assert ret == 0
    assert capturado["history"] == ["�"]
    assert capturado["validar"][0] == "�"
    assert all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in capturado["validar"][0])
    assert capturado["validar"][0].encode("utf-8") == "�".encode("utf-8")


def test_run_repl_loop_debug_detecta_surrogate_remanente_en_frontera():
    cmd = InteractiveCommand(MagicMock())
    cmd._debug_mode = True
    args = _args()
    entradas = iter(["\ud83d"])

    def _leer_linea(_prompt: str) -> str:
        return next(entradas)

    with patch(
        "pcobra.cobra.cli.commands.interactive_cmd.sanitize_input",
        side_effect=lambda value: value,
    ):
        try:
            cmd._run_repl_loop(
                args=args,
                validador=None,
                leer_linea=_leer_linea,
                sandbox=False,
                sandbox_docker=None,
            )
            assert False, "Se esperaba AssertionError por surrogate aislado remanente."
        except AssertionError as exc:
            assert "pre-validacion" in str(exc)


def test_safe_file_history_append_string_none_se_coacciona_y_sanea(tmp_path, monkeypatch):
    if SafeFileHistory is None:
        return

    capturado: list[str] = []
    monkeypatch.setattr(
        SafeFileHistory.__mro__[1],
        "append_string",
        lambda _self, value: capturado.append(value),
        raising=False,
    )
    history = SafeFileHistory(str(tmp_path / ".cobra_history"))
    history.append_string(None)

    assert capturado == [""]


def test_safe_file_history_append_string_objeto_custom_usa_str(tmp_path, monkeypatch):
    if SafeFileHistory is None:
        return

    capturado: list[str] = []
    monkeypatch.setattr(
        SafeFileHistory.__mro__[1],
        "append_string",
        lambda _self, value: capturado.append(value),
        raising=False,
    )

    class EntradaCustom:
        def __str__(self) -> str:
            return "objeto-🚀-válido"

    history = SafeFileHistory(str(tmp_path / ".cobra_history"))
    history.append_string(EntradaCustom())

    assert capturado == ["objeto-🚀-válido"]


def test_safe_file_history_append_string_surrogate_aislado_no_lanza_unicode_encode_error(
    tmp_path, monkeypatch
):
    if SafeFileHistory is None:
        return

    capturado: list[str] = []
    monkeypatch.setattr(
        SafeFileHistory.__mro__[1],
        "append_string",
        lambda _self, value: capturado.append(value),
        raising=False,
    )
    history = SafeFileHistory(str(tmp_path / ".cobra_history"))

    try:
        history.append_string("\ud83d")
    except UnicodeEncodeError as exc:  # pragma: no cover - condición de regresión explícita
        assert False, f"No debía propagarse UnicodeEncodeError: {exc}"

    payload = capturado[0]
    assert payload == "�"
    assert all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in payload)
    assert payload.encode("utf-8") == "�".encode("utf-8")


def test_safe_file_history_append_string_muy_larga_multilenguaje_surrogate(tmp_path, monkeypatch):
    if SafeFileHistory is None:
        return

    capturado: list[str] = []
    monkeypatch.setattr(
        SafeFileHistory.__mro__[1],
        "append_string",
        lambda _self, value: capturado.append(value),
        raising=False,
    )

    segmento = "Español العربية हिंदी 日本語 🚀\ud83d"
    entrada = segmento * 2000
    esperado = sanitize_input(entrada)
    history = SafeFileHistory(str(tmp_path / ".cobra_history"))
    history.append_string(entrada)
    payload = capturado[0]

    assert payload == esperado
    assert "�" in payload
    assert all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in payload)
