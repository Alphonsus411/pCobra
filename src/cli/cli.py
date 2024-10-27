import argparse
import logging

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.transpiler.to_python import TranspiladorPython

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(message)s')  # Muestra solo mensajes importantes


def ejecutar_cobra_interactivamente():
    print("Bienvenido a la interfaz interactiva de Cobra. Escribe 'salir' o 'salir()' para salir.")
    interpretador = InterpretadorCobra()

    while True:
        try:
            linea = input("cobra> ").strip()
            if linea in ["salir", "salir()"]:  # Permitir ambas variantes
                print("Saliendo de la interfaz interactiva.")
                break  # Salir del bucle
            elif linea:
                tokens = Lexer(linea).tokenizar()
                ast = Parser(tokens).parsear()
                interpretador.ejecutar_ast(ast)  # Ejecuta el AST con el intérprete
        except Exception as e:
            print(f"Error: {e}")


def transpilar_archivo(archivo, transpilador):
    with open(archivo, 'r') as f:
        codigo = f.read()
        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()

        if transpilador == "python":
            transpilador = TranspiladorPython()
        elif transpilador == "js":
            transpilador = TranspiladorJavaScript()
        else:
            raise ValueError("Transpilador no soportado.")

        resultado = transpilador.transpilar(ast)
        print(f"Código {transpilador}:")
        print(resultado)


def main():
    parser = argparse.ArgumentParser(description="CLI para Cobra")
    parser.add_argument("archivo", nargs="?", help="Archivo con código Cobra para ejecutar o transpilar")
    parser.add_argument("--transpilador", choices=["python", "js"],
                        help="Opcional: Transpila el archivo a Python o JavaScript.")

    args = parser.parse_args()

    if args.archivo:
        transpilar_archivo(args.archivo, args.transpilador)
    else:
        ejecutar_cobra_interactivamente()


if __name__ == "__main__":
    main()
