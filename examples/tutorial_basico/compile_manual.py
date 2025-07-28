from typing import List, Optional
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.ast_nodes import NodoValor, NodoImprimir

def procesar_archivo(ruta_archivo: str) -> Optional[str]:
    """
    Procesa un archivo de código fuente y genera su equivalente en Python.
    
    Args:
        ruta_archivo: Ruta al archivo .co a procesar
    
    Returns:
        str: Código Python generado o None si hay error
    """
    try:
        # Leer archivo de forma segura
        with open(ruta_archivo) as f:
            codigo = f.read()
            
        if not codigo.strip():
            raise ValueError("El archivo está vacío")
            
        # Análisis léxico
        lex = Lexer(codigo)
        tokens = lex.analizar_token()
        if not tokens:
            raise ValueError("No se encontraron tokens válidos")
            
        # Parsing
        ast = Parser(tokens).parsear()
        if not ast:
            raise ValueError("No se pudo generar el AST")
            
        # Procesamiento de nodos
        for nodo in ast:
            if isinstance(nodo, NodoImprimir) and isinstance(nodo.expresion, NodoValor):
                val = nodo.expresion.valor
                if isinstance(val, str) and not (val.startswith("'") or val.startswith('"')):
                    nodo.expresion.valor = repr(val)
                    
        # Generación de código
        return TranspiladorPython().generate_code(ast)
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo}")
    except ValueError as e:
        print(f"Error de validación: {str(e)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
    return None

if __name__ == "__main__":
    resultado = procesar_archivo('examples/tutorial_basico/hola_mundo.co')
    if resultado:
        print(resultado)