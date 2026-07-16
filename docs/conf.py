# Sphinx configuration for the iwfm package documentation.
# Build: .venv/bin/sphinx-build -b html docs docs/_build/html

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'iwfm'
author = 'Charles Brush'
copyright = '2020-2026, University of California'
release = '0.0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',      # numpy-style docstrings
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# Generate one page per module from the autosummary directives
autosummary_generate = True
autodoc_member_order = 'bysource'

# Optional/lazy dependencies that may not be installed in the docs venv
autodoc_mock_imports = [
    'qgis', 'pywfm', 'geopdf', 'pypest',
    'tabula', 'osmnx', 'laspy', 'folium', 'xlrd', 'pymysql',
    'anthropic',
    'osgeo', 'gdal', 'ogr', 'osr',
    # NOTE: win32com is deliberately NOT mocked — mocking it makes the xls
    # backend selector choose the deprecated win32com path over openpyxl
]

napoleon_numpy_docstring = True
napoleon_google_docstring = False

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
html_title = 'iwfm — IWFM file tools for Python'
