import ast
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
            if target=='python': ast.parse(code); result='OK ast.parse'
            else:
                with tempfile.NamedTemporaryFile('w',suffix=ext,delete=False) as f: f.write(code); path=f.name
                cmd=['node','--check',path] if target=='js' else ['rustc','--crate-type','lib',path,'-o',path+'.rlib']
                p=subprocess.run(cmd,text=True,capture_output=True)
                result=('OK' if p.returncode==0 else 'FAIL')+' '+('node --check' if target=='js' else 'rustc')
                if p.returncode: result += ': '+(p.stderr.strip().splitlines()[0] if p.stderr.strip() else '')
            print(f'{target}={result}')
        except Exception as e: print(f'{target}=FAIL {type(e).__name__}: {e}')
