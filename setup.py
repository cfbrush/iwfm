# setup.py for iwfm package
# Classes, methods and functions to read, write and modify IWFM and IGSM files
# Copyright (C) 2018-2026 University of California
#-----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#-----------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'IWFM Python package'
LONG_DESCRIPTION = 'Classes, methods and functions to read, write and modify IWFM files'

# Setting up
setup(
        # the name must match the folder name
        name="iwfm", 
        version=VERSION,
        author="Charles Brush",
        author_email="<cfbrush@ucdavis.edu>",
        license='GNU',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires= ['area', 'bs4', 'folium', 'fpdf', 'geocoder',
            'geojson', 'geopandas', 'loguru', 'matplotlib', 'numpy', 'ogr',
            'openpyxl', 'osmnx', 'pandas', 'pathlib', 'pillow', 'pngcanvas',
            'pynmea', 'pypdf2', 'pyshp', 'python_dateutil', 'rasterio',
            'requests', 'scipy', 'statistics', 'typer', 'utm', 'xlrd'
            # add any additional packages that need to be installed along with your package. Eg: 'qgis'
        ],
        entry_points={
            'console_scripts': [
                'iwfm = iwfm.cli.main:run',
            ],
        },
        python_requires='~=3.8',
        
        keywords=['python', 'first package', 'iwfm'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Groundwater Modelers",
            "Programming Language :: Python :: 3.8",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS :: MacOS X",
        ]
    )