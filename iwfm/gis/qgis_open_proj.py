# qgis_open_proj.py
# Open QGIS project
# Copyright (C) 2020-2021 University of California
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
    ''' qgis_open_proj() - Open a QGIS project

    ** INCOMPLETE **
    
    Parameters
    ----------
    filename : str
        input shapefile name

    verbose : bool, default=False
        turn command-line output on or off

    debug : int, default=0
        0 no CLI debug logging 
        1 debug logging via print statements
        debug statements and parameter should be removed after completion

    Returns
    -------
    project : qgis object
        QGIS project

    '''
    import os
    import qgis.core as qcore

    if debug:
        print(f'  Opening QGIS project {filename}')  

    # check for the project file
    if not os.path.isfile(os.path.join(os.getcwd(), filename)):
        import sys
        from iwfm.debug.logger_setup import logger
        logger.error(f'Could not find {os.path.join(os.getcwd(), filename)}; exiting.')
        sys.exit()

    #  # for QGIS standalone app, bridge to sync loaded project with canvas
    #  bridge = QgsLayerTreeMapCanvasBridge(project.layerTreeRoot(), canvas)
    #  # NameError: name 'QgsLayerTreeMapCanvasBridge' is not defined

    #  apparently python 2 / QGIS2 way:
    #  project = qutil.QFile(filename)

    project = qcore.QgsProject.instance()  # instantiate

    # fill instantiated project (file name, not full path)
    project.read(filename)
    if verbose:
        print(f'  Opened QGIS project {filename}')
    if debug:
        print(f'  => project:    {project}')
        print(f'  => filename(): \'{project.fileName()}\'')
        print(f'  => title:      \'{project.title()}\'')
        print(f'  => layers:     {project.count()}')
        print('  ----------------------------')
    return project
