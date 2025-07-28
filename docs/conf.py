# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime
from pathlib import Path

def ensure_dir_exists(path):
    """Asegura que el directorio existe, creándolo si es necesario."""
    Path(path).mkdir(parents=True, exist_ok=True)

# Verificar y crear directorios necesarios
for directory in ['_static', '_templates', 'locale']:
    ensure_dir_exists(directory)

# Setup paths so Sphinx can find the backend package
ROOT_DIR = Path(__file__).parent.parent.absolute()
BACKEND_SRC = ROOT_DIR / 'backend' / 'src'

# Verificar que el directorio backend/src existe
if not BACKEND_SRC.exists():
    raise FileNotFoundError(f"El directorio {BACKEND_SRC} no existe")

sys.path.insert(0, str(BACKEND_SRC))
sys.path.insert(0, str(ROOT_DIR))

# -- Project information -----------------------------------------------------
project = 'Proyecto Cobra'
copyright = f'{datetime.now().year}, Adolfo González Hernández'
author = 'Adolfo González Hernández'
release = '10.0.6'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinxcontrib.plantuml',
    'sphinx_rtd_theme',  # Añadido explícitamente como extensión
]

# Mock imports más específicos para evitar conflictos
autodoc_mock_imports = [
    'backend.src',
    'backend.tests',
]

# Habilitar la generación automática de autosummary
autosummary_generate = True

# The master toctree document (cambiado a minúsculas)
master_doc = 'manual_cobra'

# Verificar que el archivo principal existe
if not (ROOT_DIR / 'docs' / f'{master_doc}.rst').exists():
    raise FileNotFoundError(f"El archivo {master_doc}.rst no existe")

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# Configuración de catálogos gettext
locale_dirs = ['locale/']
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Verificar que custom.css existe antes de incluirlo
custom_css = Path('_static/custom.css')
if custom_css.exists():
    html_css_files = ['custom.css']
else:
    print(f"Advertencia: {custom_css} no existe")
    html_css_files = []

# Configuración de PlantUML
plantuml = 'plantuml'
plantuml_output_format = 'png'

# Verificar que PlantUML está instalado
import shutil
if not shutil.which(plantuml):
    print("Advertencia: PlantUML no está instalado en el sistema")

# Habilitar todos los TODOs
todo_include_todos = True

# Configuración adicional de autodoc
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
    'undoc-members': True
}