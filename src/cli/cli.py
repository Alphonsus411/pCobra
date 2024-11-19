import argparse
import logging
from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.transpiler.to_python import TranspiladorPython
import os

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(message)s')  # Muestra solo mensajes importantes


def ejecutar_cobra_interactivamente():
    print("Bienvenido a la interfaz interactiva de Cobra. Escribe 'salir' o 'salir()' para salir.")
    print("Comandos especiales: 'tokens' y 'ast' para inspección avanzada.")
    interpretador = InterpretadorCobra()

    while True:
        try:
            linea = input("cobra> ").strip()
            if linea in ["salir", "salir()"]:  # Permitir ambas variantes
                print("Saliendo de la interfaz interactiva.")
                break  # Salir del bucle
            elif linea == "tokens":
                print("Mostrando tokens de la última línea procesada:")
                tokens = Lexer(linea).tokenizar()
                for token in tokens:
                    print(token)
                continue
            elif linea == "ast":
                print("Mostrando AST de la última línea procesada:")
                tokens = Lexer(linea).tokenizar()
                ast = Parser(tokens).parsear()
                print(ast)
                continue
            elif linea:
                tokens = Lexer(linea).tokenizar()
                ast = Parser(tokens).parsear()
                interpretador.ejecutar_ast(ast)  # Ejecuta el AST con el intérprete
        except Exception as e:
            print(f"Error procesando la entrada: {e}")


def transpilar_archivo(archivo, transpilador):
    if not os.path.exists(archivo):
        print(f"Error: El archivo '{archivo}' no existe.")
        return

    with open(archivo, 'r') as f:
        codigo = f.read()
        try:
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
        except Exception as e:
            print(f"Error durante la transpilación: {e}")


def inspeccionar_archivo(archivo, modo):
    if not os.path.exists(archivo):
        print(f"Error: El archivo '{archivo}' no existe.")
        return

    with open(archivo, 'r') as f:
        codigo = f.read()
        try:
            tokens = Lexer(codigo).tokenizar()
            if modo == "tokens":
                print("Tokens generados:")
                for token in tokens:
                    print(token)
            elif modo == "ast":
                ast = Parser(tokens).parsear()
                print("AST generado:")
                print(ast)
        except Exception as e:
            print(f"Error durante la inspección: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI para Cobra")
    parser.add_argument("archivo", nargs="?", help="Archivo con código Cobra para ejecutar o transpilar")
    parser.add_argument("--transpilador", choices=["python", "js"],
                        help="Opcional: Transpila el archivo a Python o JavaScript.")
    parser.add_argument("--inspeccionar", choices=["tokens", "ast"],
                        help="Opcional: Inspecciona los tokens o AST de un archivo.")

    args = parser.parse_args()

    if args.archivo and args.transpilador:
        transpilar_archivo(args.archivo, args.transpilador)
    elif args.archivo and args.inspeccionar:
        inspeccionar_archivo(args.archivo, args.inspeccionar)
    elif not args.archivo:
        ejecutar_cobra_interactivamente()
    else:
        print("Opción inválida. Usa '--help' para más información.")


if __name__ == "__main__":
    main()
