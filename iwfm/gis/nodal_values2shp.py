# nodal_values2shp.py
# Create node shapefile for an IWFM model with a value for each node
# Copyright (C) 2020-2023 University of California
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


'''Create node shapefile for an IWFM model with a value for each node.'''

def nodal_values2shp(node_coords, values, values_name, shape_name, epsg=26910, verbose=False):
    '''Create node shapefile for an IWFM model with a value for each node.

    Parameters
    ----------
    node_coords : list
        node id and coordinates: [[node_id, x, y], ...]

    values : list
        values for each node

    values_name : str
        name of values

    shape_name : str
        output file name

    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    import iwfm.gis as igis
    import shapefile

    shapename = f'{shape_name}_Nodal_{values_name}'

    with shapefile.Writer(shapename+'.shp', shapeType=shapefile.POINT) as w:
        w.field('node_id', 'N', 10, 0)
        w.field(values_name, 'N', 10, 4)
        w.autoBalance = 1
        for i in range(len(node_coords)):
            x, y = node_coords[i][1],node_coords[i][2]
            w.point(x,y)
            w.record(node_coords[i][0], values[i])

    # write PRJ file
    igis.projection(shapename, epsg=epsg, verbose=verbose)

    if verbose: print(f'  Wrote shapefile {shapename}')



