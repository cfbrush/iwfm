# kml_points.py
# get point coords from KML file
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


def kml_points(filename, verbose=False):
    ''' kml_points() - Get point coordinates from a KML file

    Parameters
    ----------
    filename : str
        name to save info from url
    
    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    points :  llist
        point coordinates

    '''
    from xml.dom import minidom  # python -m pip install xml

    kml = minidom.parse(filename)
    Placemarks = kml.getElementsByTagName('Placemark')
    if verbose:
        print(f'  Retrieved {len(Placemarks):,} placemarks from \'{filename}\' ')
        print('Point\tCoordinates')

    points = []
    for i in range(len(Placemarks)):
        coordinates = Placemarks[i].getElementsByTagName('coordinates')
        point = coordinates[0].firstChild.data.split(',')
        points.append(point)
        if verbose > 0:
            print(f' {i} \t{point}')

    return points
