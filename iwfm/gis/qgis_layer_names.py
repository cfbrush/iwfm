# qgis_layer_names.py
# QGIS project layer names
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


'''Get a list of QGIS project layer names and paths.'''

def qgis_layer_names(project):
    '''Get a list of QGIS project layer names and paths.

    Parameters
    ----------
    project : qcore.QgsProject.instance() object

    Return
    ------
    layer_names : list
        project layer names

    layer_paths : list
        paths to layer files
    '''
    layer_names = [layer.name() for layer in project.layerTreeRoot().children()]
    layer_paths = [layer.source() for layer in project.mapLayers().values()]
    return layer_names, layer_paths
