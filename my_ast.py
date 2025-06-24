# Herramienta avanzada para generar el AST del lenguaje Cobra
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
import argparse
import json


def leer_codigo(archivo=None, entrada=None):
    if archivo:
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    if entrada:
        return entrada
    return ''


def generar_tokens(codigo):
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    return tokens


def generar_ast(tokens):
    parser = Parser(tokens)
    return parser.parsear()


def mostrar_tokens(tokens):
    print("Tokens generados:")
    for token in tokens:
        print(f"- {token}")


def mostrar_ast(ast):
    print("\nAST generado:")
    print(json.dumps(ast, default=lambda o: o.__dict__, indent=2))


def main():
    # Configurar argumentos de línea de comandos
    parser_args = argparse.ArgumentParser(description="Generador avanzado de AST para Cobra")
    parser_args.add_argument('-f', '--file', help="Archivo con código fuente en Cobra")
    parser_args.add_argument('-c', '--code', help="Código fuente en Cobra directamente")
    args = parser_args.parse_args()

    # Leer código
    codigo = leer_codigo(archivo=args.file, entrada=args.code)
    if not codigo:
        print("Por favor, proporciona código fuente con --file o --code.")
        return

    # Fases del proceso
    try:
        # Lexer
        tokens = generar_tokens(codigo)
        mostrar_tokens(tokens)

        # Parser
        ast = generar_ast(tokens)
        mostrar_ast(ast)
    except Exception as e:
        print(f"Error procesando el código: {e}")


if __name__ == "__main__":
    main()
