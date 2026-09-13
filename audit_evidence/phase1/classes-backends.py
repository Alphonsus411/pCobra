import ast
import shutil
import subprocess
import tempfile
from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
cases = {
'declaracion_override': '''
clase Base:
    metodo valor(self):
        retorno 1
    fin
fin
clase Derivada(Base):
    metodo valor(self):
        retorno 2
    fin
fin
''',
'instanciacion': '''
clase C:
    metodo valor(self):
        retorno 1
    fin
fin
var c = C()
''',
'llamada_metodo': '''
clase C:
    metodo valor(self):
        retorno 1
    fin
fin
var c = C()
imprimir c.valor()
''',
'herencia_multiple': '''
clase A:
    metodo a(self):
        retorno 1
    fin
fin
clase B:
    metodo b(self):
        retorno 2
    fin
fin
clase C(A, B):
    metodo c(self):
        retorno 3
    fin
fin
''',
}


def validate_target(target, code, extension):
    """Valida el texto emitido sin confundir ausencia de herramienta con fallo."""
    if target == 'python':
        ast.parse(code)
        return 'OK ast.parse'

    executable = 'node' if target == 'js' else 'rustc'
    if shutil.which(executable) is None:
        return f'NO APLICA {executable} no disponible'

    with tempfile.TemporaryDirectory() as temporary_directory:
        output_path = f'{temporary_directory}/output{extension}'
        with open(output_path, 'w', encoding='utf-8') as output:
            output.write(code)
        command = (
            ['node', '--check', output_path]
            if target == 'js'
            else [
                'rustc',
                '--crate-type',
                'lib',
                output_path,
                '-o',
                f'{temporary_directory}/output.rlib',
            ]
        )
        process = subprocess.run(command, text=True, capture_output=True)

    check_name = 'node --check' if target == 'js' else 'rustc'
    result = ('OK' if process.returncode == 0 else 'FAIL') + f' {check_name}'
    if process.returncode:
        diagnostics = [
            line.strip()
            for line in process.stderr.splitlines()
            if line.startswith('error')
        ]
        result += ': ' + ' | '.join(diagnostics[:3])
    return result


for name, source in cases.items():
    print(f'CASE {name}')
    try:
        tree=Parser(Lexer(source).analizar_token()).parsear()
        print('parser=OK ast=' + ','.join(type(x).__name__ for x in tree))
    except Exception as e:
        print(f'parser=FAIL {type(e).__name__}: {e}')
        continue
    for target, tr, ext in [('python',TranspiladorPython(),'.py'),('js',TranspiladorJavaScript(),'.js'),('rust',TranspiladorRust(),'.rs')]:
        try:
            code=tr.generate_code(tree)
            result=validate_target(target, code, ext)
            print(f'{target}={result}')
        except Exception as e: print(f'{target}=FAIL {type(e).__name__}: {e}')
