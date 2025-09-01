import sys
import types
from io import StringIO
from unittest.mock import patch

# Crear modulos ficticios para dependencias opcionales
cli_mod = types.ModuleType("cli")
utils_mod = types.ModuleType("cli.utils")
semver_mod = types.ModuleType("cli.utils.semver")
semver_mod.es_version_valida = lambda v: True
utils_mod.semver = semver_mod
cli_mod.utils = utils_mod
sys.modules.setdefault("cli", cli_mod)
sys.modules.setdefault("cli.utils", utils_mod)
sys.modules.setdefault("cli.utils.semver", semver_mod)

# En caso de que tree_sitter_languages no esté instalado
if "tree_sitter_languages" not in sys.modules:
    tsl_mod = types.ModuleType("tree_sitter_languages")
    tsl_mod.get_parser = lambda lang: None
    sys.modules["tree_sitter_languages"] = tsl_mod

from core.ast_nodes import NodoHilo, NodoLlamadaFuncion, NodoValor, NodoFuncion
from core.interpreter import InterpretadorCobra


def test_hilo_es_daemon():
    interp = InterpretadorCobra()
    funcion = NodoFuncion('marca', [], [NodoLlamadaFuncion('imprimir', [NodoValor('ok')])])
    interp.ejecutar_funcion(funcion)
    with patch('sys.stdout', new_callable=StringIO):
        hilo = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('marca', [])))
        assert hilo.daemon
        hilo.join()
