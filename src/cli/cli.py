import argparse
import logging
from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.transpiler.to_python import TranspiladorPython
import os

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def ejecutar_cobra_interactivamente():
    """Ejecuta Cobra en modo interactivo."""
    print("Bienvenido a la interfaz interactiva de Cobra. Escribe 'salir' o 'salir()' para salir.")
    print("Comandos especiales: 'tokens' y 'ast' para inspección avanzada.")
    interpretador = InterpretadorCobra()

    while True:
        try:
            linea = input("cobra> ").strip()
            if linea in ["salir", "salir()"]:  # Permitir ambas variantes para salir
                print("Saliendo de la interfaz interactiva.")
                break
            elif linea == "tokens":
                tokens = Lexer(linea).tokenizar()
                print("Tokens generados:")
                for token in tokens:
                    print(token)
                continue
            elif linea == "ast":
                tokens = Lexer(linea).tokenizar()
                ast = Parser(tokens).parsear()
                print("AST generado:")
                print(ast)
                continue
            elif linea:  # Procesar una entrada normal
                tokens = Lexer(linea).tokenizar()
                logging.debug(f"Tokens generados: {tokens}")
                ast = Parser(tokens).parsear()
                logging.debug(f"AST generado: {ast}")
                interpretador.ejecutar_ast(ast)
        except SyntaxError as se:
            logging.error(f"Error de sintaxis: {se}")
            print(f"Error procesando la entrada: {se}")
        except RuntimeError as re:
            logging.error(f"Error crítico: {re}")
            print(f"Error crítico: {re}")
        except Exception as e:
            logging.error(f"Error general procesando la entrada: {e}")
            print(f"Error procesando la entrada: {e}")


def transpilar_archivo(archivo, transpilador):
    """Transpila un archivo Cobra a Python o JavaScript."""
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
            print(f"Código generado ({transpilador.__class__.__name__}):")
            print(resultado)
        except SyntaxError as se:
            logging.error(f"Error de sintaxis durante la transpilación: {se}")
            print(f"Error durante la transpilación: {se}")
        except Exception as e:
            logging.error(f"Error general durante la transpilación: {e}")
            print(f"Error durante la transpilación: {e}")


def inspeccionar_archivo(archivo, modo):
    """Inspecciona un archivo Cobra generando tokens o un AST."""
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
        except SyntaxError as se:
            logging.error(f"Error de sintaxis durante la inspección: {se}")
            print(f"Error durante la inspección: {se}")
        except Exception as e:
            logging.error(f"Error general durante la inspección: {e}")
            print(f"Error durante la inspección: {e}")


def main():
    """Punto de entrada principal de la CLI."""
    parser = argparse.ArgumentParser(description="CLI para Cobra")
    parser.add_argument("archivo", nargs="?", help="Archivo con código Cobra para ejecutar o transpilar")
    parser.add_argument("--transpilador", choices=["python", "js"],
                        help="Opcional: Transpila el archivo a Python o JavaScript.")
    parser.add_argument("--inspeccionar", choices=["tokens", "ast"],
                        help="Opcional: Inspecciona los tokens o AST de un archivo.")

    args, _ = parser.parse_known_args()

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
