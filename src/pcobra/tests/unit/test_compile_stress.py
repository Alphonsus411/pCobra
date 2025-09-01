import os
import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from cobra.cli.commands.compile_cmd import CompileCommand


def _fake_transpile(self, ast):
    import time
    time.sleep(0.05)
    return str(os.getpid())


@pytest.mark.timeout(10)
def test_compile_command_parallel_outputs_unique(tmp_path):
    archivo = tmp_path / 'c.co'
    archivo.write_text('var x = 5')
    args = argparse.Namespace(
        archivo=str(archivo),
        tipo='python',
        backend=None,
        tipos='python,js,c,cpp',
    )
    with patch(
        'cobra.transpilers.transpiler.to_python.TranspiladorPython.transpilar',
        _fake_transpile,
    ), patch(
        'cobra.transpilers.transpiler.to_js.TranspiladorJavaScript.transpilar',
        _fake_transpile,
    ), patch(
        'cobra.transpilers.transpiler.to_c.TranspiladorC.transpilar',
        _fake_transpile,
    ), patch(
        'cobra.transpilers.transpiler.to_cpp.TranspiladorCPP.transpilar',
        _fake_transpile,
    ), patch(
        'cobra.transpilers.module_map.get_toml_map',
        lambda: {},
    ), patch('sys.stdout', new_callable=StringIO) as out:
        CompileCommand().run(args)

    lineas = out.getvalue().strip().splitlines()
    pids = {lineas[1], lineas[3], lineas[5], lineas[7]}
    assert len(pids) == 4
