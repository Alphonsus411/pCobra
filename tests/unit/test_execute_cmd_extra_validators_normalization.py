from types import SimpleNamespace

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.core.semantic_validators.base import ValidadorBase


class DummyValidator(ValidadorBase):
    pass


class DummyNodo:
    def aceptar(self, visitante):
        return None


def _preparar_parser_lexer(monkeypatch, execute_module):
    monkeypatch.setattr(execute_module, "analizar_codigo", lambda _codigo: [DummyNodo()])


def _preparar_construir_cadena(monkeypatch, execute_module):
    monkeypatch.setattr(execute_module, "construir_cadena", lambda _extra: SimpleNamespace())


def test_ejecutar_normal_carga_validadores_desde_una_ruta(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    _preparar_parser_lexer(monkeypatch, execute_module)
    _preparar_construir_cadena(monkeypatch, execute_module)

    cargado = [DummyValidator()]

    class DummyInterp:
        def __init__(self, safe_mode=True, extra_validators=None):
            self.safe_mode = safe_mode
            self.extra_validators = extra_validators

        def ejecutar_ast(self, _ast):
            return None

        @staticmethod
        def _cargar_validadores(ruta):
            assert ruta == "ruta_unica.py"
            return cargado

    monkeypatch.setattr(execute_module, "_obtener_interpretador_cls", lambda: DummyInterp)

    resultado = ExecuteCommand()._ejecutar_normal("imprimir(1)", True, "ruta_unica.py")

    assert resultado == 0


def test_ejecutar_normal_carga_y_acumula_multiples_rutas(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    _preparar_parser_lexer(monkeypatch, execute_module)
    _preparar_construir_cadena(monkeypatch, execute_module)

    v1 = DummyValidator()
    v2 = DummyValidator()
    rutas_cargadas = []

    class DummyInterp:
        init_extra = None

        def __init__(self, safe_mode=True, extra_validators=None):
            DummyInterp.init_extra = extra_validators

        def ejecutar_ast(self, _ast):
            return None

        @staticmethod
        def _cargar_validadores(ruta):
            rutas_cargadas.append(ruta)
            return [v1] if ruta == "uno.py" else [v2]

    monkeypatch.setattr(execute_module, "_obtener_interpretador_cls", lambda: DummyInterp)

    resultado = ExecuteCommand()._ejecutar_normal("imprimir(1)", True, ["uno.py", "dos.py"])

    assert resultado == 0
    assert rutas_cargadas == ["uno.py", "dos.py"]
    assert DummyInterp.init_extra == [v1, v2]


def test_ejecutar_normal_acepta_lista_vacia_y_none(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    _preparar_parser_lexer(monkeypatch, execute_module)
    _preparar_construir_cadena(monkeypatch, execute_module)

    class DummyInterp:
        llamadas = []

        def __init__(self, safe_mode=True, extra_validators=None):
            DummyInterp.llamadas.append(extra_validators)

        def ejecutar_ast(self, _ast):
            return None

        @staticmethod
        def _cargar_validadores(_ruta):
            raise AssertionError("No debería cargar rutas para None o lista vacía")

    monkeypatch.setattr(execute_module, "_obtener_interpretador_cls", lambda: DummyInterp)

    cmd = ExecuteCommand()
    assert cmd._ejecutar_normal("imprimir(1)", True, []) == 0
    assert cmd._ejecutar_normal("imprimir(1)", True, None) == 0
    assert DummyInterp.llamadas == [[], None]


def test_ejecutar_normal_muestra_error_claro_si_falla_una_ruta(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    _preparar_parser_lexer(monkeypatch, execute_module)
    _preparar_construir_cadena(monkeypatch, execute_module)

    errores = []

    class DummyInterp:
        def __init__(self, safe_mode=True, extra_validators=None):
            self.safe_mode = safe_mode
            self.extra_validators = extra_validators

        def ejecutar_ast(self, _ast):
            return None

        @staticmethod
        def _cargar_validadores(ruta):
            if ruta == "mala.py":
                raise FileNotFoundError("archivo inexistente")
            return [DummyValidator()]

    monkeypatch.setattr(execute_module, "_obtener_interpretador_cls", lambda: DummyInterp)
    monkeypatch.setattr(execute_module, "mostrar_error", lambda msg, **_kwargs: errores.append(msg))

    resultado = ExecuteCommand()._ejecutar_normal("imprimir(1)", True, ["buena.py", "mala.py"])

    assert resultado == 1
    assert errores
    assert "mala.py" in errores[0]
    assert "archivo inexistente" in errores[0]
