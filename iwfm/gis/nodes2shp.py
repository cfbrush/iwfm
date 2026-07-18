# nodes2shp.py
# Create node shapefiles for an IWFM model
# Copyright (C) 2020-2024 University of California
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


'''Create node shapefiles for an IWFM model.'''

def nodes2shp(node_coords, shape_name, epsg=26910, verbose=False):
    '''Create an IWFM nodes shapefile.

    Parameters
    ----------
    node_coords : list
        node coordinates

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
    import shapefile
    import pyproj

    shapename = f'{shape_name}_Nodes.shp'

    # Create a new shapefile writer for points
    w = shapefile.Writer(shapename, shapeType=shapefile.POINT)
    
    # Define the field for node_id
    w.field('node_id', 'N', 10, 0)
    
    # Write points and their attributes
    for i in range(len(node_coords)):
        x, y = node_coords[i][1], node_coords[i][2]
        w.point(x, y)  # Add geometry
        w.record(node_id=node_coords[i][0])  # Add attributes
    
    # Create .prj file for spatial reference
    with open(f"{shapename[:-4]}.prj", "w", encoding='utf-8') as prj:
        epsg = pyproj.CRS.from_epsg(epsg)
        prj.write(epsg.to_wkt())
    
    # Save and close the shapefile
    w.close()

    if verbose:
        print(f'  Wrote shapefile {shapename}')

    return


def calc_base(node_strat):
    # calculate base altitude for each node
    nlayers = int(len(node_strat[0])/2 - 1)
    base = []
    for i in range(len(node_strat)):
        temp = node_strat[i][1]  # gse
        for j in range(nlayers * 2):
            temp = temp - node_strat[i][j + 2]
        base.append(temp)
    return base
