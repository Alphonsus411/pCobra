import subprocess
from pathlib import Path
import sys

# Configuración
OUTPUT_DIR = Path('frontend/build/pdoc')
SOURCE_DIR = Path('src')

def check_pdoc_installed():
    try:
        subprocess.run(['pdoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    # Verificar si pdoc está instalado
    if not check_pdoc_installed():
        print("Error: pdoc no está instalado. Por favor instálelo con 'pip install pdoc'")
        sys.exit(1)
    
    try:
        # Crear directorio de salida
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Ejecutar pdoc
        subprocess.run([
            'pdoc',
            str(SOURCE_DIR),
            '--output-dir', str(OUTPUT_DIR)
        ], check=True)
        
        print(f"Documentación generada exitosamente en {OUTPUT_DIR}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar pdoc: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()