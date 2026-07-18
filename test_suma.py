
from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.core.parser import parse

code = '''func sumar(a, b):
    c = a + b
    imprimir(c)
fin

sumar(2, 3)
'''

ast = parse(code)
print("AST:", ast)

interpreter = InterpretadorCobra(safe_mode=False)
interpreter.ejecutar(ast)
