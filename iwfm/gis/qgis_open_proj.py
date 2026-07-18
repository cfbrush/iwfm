# qgis_open_proj.py
# Open QGIS project
# Copyright (C) 2020-2026 University of California
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------


def qgis_open_proj(filename, verbose=False, debug=0):
    '''Open a QGIS project.

    Must be run inside a QGIS Python environment (the qgis package is not
    pip-installable).

    Parameters
    ----------
    filename : str
        QGIS project file name

    verbose : bool, default=False
        turn command-line output on or off

    debug : int, default=0
        1 = print debug information about the opened project

    Returns
    -------
    project : qgis.core.QgsProject
        QGIS project

    Raises
    ------
    FileNotFoundError
        if the project file does not exist
    ValueError
        if QGIS cannot read the project file
    '''
    import os
    import qgis.core as qcore

    if debug:
        print(f'  Opening QGIS project {filename}')

    # check for the project file
    if not os.path.isfile(os.path.join(os.getcwd(), filename)):
        raise FileNotFoundError(f'Could not find {os.path.join(os.getcwd(), filename)}')

    project = qcore.QgsProject.instance()  # instantiate

    # fill instantiated project (file name, not full path)
    if not project.read(filename):
        raise ValueError(f'QGIS could not read project file {filename}')
    if verbose:
        print(f'  Opened QGIS project {filename}')
    if debug:
        print(f'  => project:    {project}')
        print(f'  => filename(): \'{project.fileName()}\'')
        print(f'  => title:      \'{project.title()}\'')
        print(f'  => layers:     {project.count()}')
        print('  ----------------------------')
    return project
