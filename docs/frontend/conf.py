import os
import sys
from datetime import datetime

# Validación de directorios base
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

if not os.path.exists(SRC_DIR):
    raise FileNotFoundError(f"El directorio src no existe: {SRC_DIR}")

if not os.path.exists(ROOT_DIR):
    raise FileNotFoundError(f"El directorio raíz no existe: {ROOT_DIR}")

sys.path.append(SRC_DIR)  # Usar append en lugar de insert
sys.path.append(ROOT_DIR)

# Información del proyecto
project = 'Proyecto Cobra'
copyright = f'{datetime.now().year}, Adolfo González Hernández'
author = 'Adolfo González Hernández'
release = '2.0'

# Configuración general
source_encoding = 'utf-8'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinxcontrib.plantuml'
]

# Verificar existencia de PlantUML
import shutil
if not shutil.which('plantuml'):
    raise RuntimeError('PlantUML no está instalado en el sistema')

# Verificar directorios estáticos
static_dir = os.path.join(os.path.dirname(__file__), '_static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

css_file = os.path.join(static_dir, 'custom.css')
if not os.path.exists(css_file):
    print(f"Advertencia: El archivo {css_file} no existe")

# Resto de la configuración
autodoc_mock_imports = ['tests']
autosummary_generate = True
templates_path = ['_templates']
exclude_patterns = []
language = 'es'

locale_dirs = ['locale/']
gettext_compact = False

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_css_files = ['custom.css']

plantuml = 'plantuml'
plantuml_output_format = 'png'