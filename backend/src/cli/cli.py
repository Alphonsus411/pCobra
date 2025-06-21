import argparse
import logging
import os
import shutil
import subprocess
import sys

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.transpiler.to_python import TranspiladorPython
from src.core.semantic_validator import (
    PrimitivaPeligrosaError,
    ValidadorSemantico,
)

# Ruta donde se almacenan los módulos instalados
MODULES_PATH = os.path.join(os.path.dirname(__file__), "modules")
os.makedirs(MODULES_PATH, exist_ok=True)

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ejecutar_cobra_interactivamente(seguro: bool = False):
    """Ejecuta Cobra en modo interactivo."""
    interpretador = InterpretadorCobra(safe_mode=seguro)
    validador = ValidadorSemantico()

    while True:
        try:
            linea = input("cobra> ").strip()
            if linea in ["salir", "salir()"]:  # Permitir ambas variantes para salir
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
                try:
                    for nodo in ast:
                        nodo.aceptar(validador)
                except PrimitivaPeligrosaError as pe:
                    logging.error(f"Primitiva peligrosa: {pe}")
                    print(f"Error: {pe}")
                    continue
                print("AST generado:")
                print(ast)
                continue
            elif linea:  # Procesar una entrada normal
                tokens = Lexer(linea).tokenizar()
                logging.debug(f"Tokens generados: {tokens}")
                ast = Parser(tokens).parsear()
                logging.debug(f"AST generado: {ast}")
                try:
                    for nodo in ast:
                        nodo.aceptar(validador)
                except PrimitivaPeligrosaError as pe:
                    logging.error(f"Primitiva peligrosa: {pe}")
                    print(f"Error: {pe}")
                    continue
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

            validador = ValidadorSemantico()
            for nodo in ast:
                nodo.aceptar(validador)

            if transpilador == "python":
                transpilador = TranspiladorPython()
            elif transpilador == "js":
                transpilador = TranspiladorJavaScript()
            else:
                raise ValueError("Transpilador no soportado.")

            resultado = transpilador.transpilar(ast)
            print(f"Código generado ({transpilador.__class__.__name__}):")
            print(resultado)
        except PrimitivaPeligrosaError as pe:
            logging.error(f"Primitiva peligrosa: {pe}")
            print(f"Error: {pe}")
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


def formatear_codigo(archivo):
    """Formatea un archivo Cobra usando black si está disponible."""
    try:
        subprocess.run(["black", archivo], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Herramienta de formateo no encontrada. Asegúrate de tener 'black' instalado.")


def generar_documentacion():
    """Genera la documentación HTML usando Sphinx."""
    # Ruta al directorio raíz del proyecto
    raiz = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
    )
    fuente = os.path.join(raiz, "frontend", "docs")
    destino = os.path.join(raiz, "frontend", "build", "html")
    subprocess.run(["sphinx-build", "-b", "html", fuente, destino], check=True)
    print(f"Documentación generada en {destino}")


def ejecutar_archivo(archivo, depurar: bool = False, formatear: bool = False, seguro: bool = False):
    """Ejecuta un script Cobra desde un archivo."""
    if not os.path.exists(archivo):
        print(f"El archivo '{archivo}' no existe")
        return
    if formatear:
        formatear_codigo(archivo)
    if depurar:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.ERROR)

    with open(archivo, "r") as f:
        codigo = f.read()
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    try:
        validador = ValidadorSemantico()
        for nodo in ast:
            nodo.aceptar(validador)
    except PrimitivaPeligrosaError as pe:
        logging.error(f"Primitiva peligrosa: {pe}")
        print(f"Error: {pe}")
        return
    InterpretadorCobra(safe_mode=seguro).ejecutar_ast(ast)


def listar_modulos():
    """Lista los módulos instalados."""
    mods = [f for f in os.listdir(MODULES_PATH) if f.endswith(".cobra")]
    if not mods:
        print("No hay módulos instalados")
    else:
        for m in mods:
            print(m)


def instalar_modulo(ruta):
    """Instala un módulo copiándolo a MODULES_PATH."""
    if not os.path.exists(ruta):
        print(f"No se encontró el módulo {ruta}")
        return
    destino = os.path.join(MODULES_PATH, os.path.basename(ruta))
    shutil.copy(ruta, destino)
    print(f"Módulo instalado en {destino}")


def remover_modulo(nombre):
    """Elimina un módulo instalado."""
    archivo = os.path.join(MODULES_PATH, nombre)
    if os.path.exists(archivo):
        os.remove(archivo)
        print(f"Módulo {nombre} eliminado")
    else:
        print(f"El módulo {nombre} no existe")


def main(argv=None):
    """Punto de entrada principal de la CLI."""
    parser = argparse.ArgumentParser(prog="cobra", description="CLI para Cobra")
    parser.add_argument("--formatear", action="store_true", help="Formatea el archivo antes de procesarlo")
    parser.add_argument("--depurar", action="store_true", help="Muestra mensajes de depuración")
    parser.add_argument("--seguro", action="store_true", help="Ejecuta en modo seguro")

    subparsers = parser.add_subparsers(dest="comando")

    # Subcomando compilar
    comp = subparsers.add_parser("compilar", help="Transpila un archivo")
    comp.add_argument("archivo")
    comp.add_argument("--tipo", choices=["python", "js"], default="python")

    # Subcomando ejecutar
    run = subparsers.add_parser("ejecutar", help="Ejecuta un script Cobra")
    run.add_argument("archivo")

    # Subcomando modulos
    mods = subparsers.add_parser("modulos", help="Gestiona módulos instalados")
    mod_sub = mods.add_subparsers(dest="accion")
    mod_sub.add_parser("listar", help="Lista módulos")
    inst = mod_sub.add_parser("instalar", help="Instala un módulo")
    inst.add_argument("ruta")
    rem = mod_sub.add_parser("remover", help="Elimina un módulo")
    rem.add_argument("nombre")

    # Subcomando docs
    subparsers.add_parser("docs", help="Genera la documentación del proyecto")

    if argv is None:
        if "PYTEST_CURRENT_TEST" in os.environ:
            argv = []
        else:
            argv = sys.argv[1:]

    args, _ = parser.parse_known_args(argv)

    if args.comando == "compilar":
        transpilar_archivo(args.archivo, args.tipo)
    elif args.comando == "ejecutar":
        ejecutar_archivo(
            args.archivo,
            depurar=args.depurar,
            formatear=args.formatear,
            seguro=args.seguro,
        )
    elif args.comando == "modulos":
        if args.accion == "listar":
            listar_modulos()
        elif args.accion == "instalar":
            instalar_modulo(args.ruta)
        elif args.accion == "remover":
            remover_modulo(args.nombre)
        else:
            print("Acción de módulos no reconocida")
    elif args.comando == "docs":
        generar_documentacion()
    else:
        ejecutar_cobra_interactivamente(seguro=args.seguro)


if __name__ == "__main__":
    main()
