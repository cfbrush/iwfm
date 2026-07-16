Installation
============

Install the package in editable mode from the top-level ``iwfm`` project
directory (the one containing ``pyproject.toml``):

.. code-block:: bash

   python -m pip install -e .

The ``-e`` flag lets you edit source files while using the package; Python
recompiles changed files at execution time.

Python 3.8+ is supported.

Optional extras
---------------

Several feature areas need optional dependencies, grouped as extras in
``pyproject.toml``:

================  ==============================================================
Extra             Enables
================  ==============================================================
``gdal``          osgeo raster/vector utilities (needs a matching system libgdal)
``mysql``         MySQL export
``llm``           LLM-supervised PEST calibration (``iwfm.diagnostics``)
``win-excel``     Excel COM automation on Windows
``pdf-tables``    PDF table extraction (needs a Java runtime)
``osm``           OpenStreetMap street networks
``lidar``         LIDAR LAS files
``webmap``        interactive HTML maps
``xls-legacy``    pre-2007 ``.xls`` workbooks
``test``          pytest, pytest-cov, ruff
``docs``          Sphinx documentation build
================  ==============================================================

For example:

.. code-block:: bash

   python -m pip install -e ".[gdal,test]"

GDAL note (macOS)
-----------------

The ``osgeo`` bindings need a system ``libgdal`` matching the pip version:

.. code-block:: bash

   PATH="/opt/homebrew/opt/gdal/bin:$PATH" pip install "gdal==$(gdal-config --version)"

Running the tests
-----------------

From the ``iwfm`` project directory (running from the repository root breaks
``import iwfm`` — the outer project folder shadows the installed package):

.. code-block:: bash

   .venv/bin/python -m pytest tests/
