# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Setup paths so Sphinx can find the backend package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BACKEND_SRC = os.path.join(ROOT_DIR, 'backend', 'src')
sys.path.insert(0, BACKEND_SRC)
sys.path.insert(0, ROOT_DIR)

project = 'Proyecto Cobra'
copyright = '2024, Adolfo González Hernández'
author = 'Adolfo González Hernández'
release = '10.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinxcontrib.plantuml',
]

# Evita errores si los paquetes no están instalados
autodoc_mock_imports = ['src', 'tests']

# Habilitar la generación automática de autosummary
autosummary_generate = True

# The master toctree document.
master_doc = 'MANUAL_COBRA'

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# Configuración de catálogos gettext
locale_dirs = ['locale/']
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_css_files = ['custom.css']

# Configuración de PlantUML
plantuml = 'plantuml'
plantuml_output_format = 'png'
