# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import os

# Obtener la ruta absoluta del archivo actual
# ruta_archivo = os.path.abspath(__file__)

# Obtener la ruta del directorio donde se encuentra el archivo
# ruta_directorio = os.path.dirname(ruta_archivo)

# print(f"La ruta del archivo es: {ruta_archivo}")
# print(f"La ruta del directorio del proyecto es: {ruta_directorio}")

sys.path.insert(0, 'C:\\Users\\user\\Documents\\pCobra\\source')


project = 'Proyecto Cobra'
copyright = '2024, Adolfo González Hernández'
author = 'Adolfo González Hernández'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo'
              ]

# Habilitar la generación automática de autosummary
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []

language = 'Python'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_css_files = ['custom.css']
