# snodes2shp.py
# Create stream node shapefiles for an IWFM model
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


'''Create stream node shapefiles for an IWFM model.'''

def snodes2shp(nsnodes, snodes_list, node_coords, shape_name, epsg=26910, verbose=False):
    '''Create an IWFM stream nodes shapefile.

    Parameters
    ----------
    nsnodes : int
        number of stream nodes

    snodes_list : list of lists or dictionary
        if list: each element contains [snode: int, gwnode: int, reach: int]
        if dictionary: key = snode_id, values = [gw_node, subregion, reach, bottom]

    node_coords : list
        stream node coordinates

    shape_name : str
        output shapefile name

    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection code

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    import shapefile
    import pyproj

    shapename = f'{shape_name}_StreamNodes'  # remove .shp extension

    node_coords_dict = {row[0]: row[1:] for row in node_coords}  # list to dictionary

    # Convert snodes_list to list if it's a dictionary
    # Dictionary format: key = snode_id, values = [gw_node, subregion, reach, bottom]
    if isinstance(snodes_list, dict):
        snodes_data = [(snode_id, values[0], values[2]) for snode_id, values in snodes_list.items()]
    else:
        snodes_data = snodes_list

    # Create a new shapefile writer object
    w = shapefile.Writer(shapename, shapeType=shapefile.POINT)

    # Define fields (replaces schema)
    w.field('snode_id', 'N', 10, 0)  # N = numeric, 10 digits, 0 decimals
    w.field('gw_node', 'N', 10, 0)
    w.field('reach', 'N', 10, 0)

    # Write features
    for i in range(nsnodes):
        snode_id, gw_node, reach = snodes_data[i]
        if gw_node != 0:
            x, y = node_coords_dict[gw_node][0], node_coords_dict[gw_node][1]
            w.point(x, y)  # Add geometry
            w.record(snode_id, gw_node, reach)  # Add attributes
    
    # Write projection file
    with open(f"{shapename}.prj", "w", encoding='utf-8') as prj:
        epsg = f'EPSG:{epsg}'
        prj.write(pyproj.CRS(epsg).to_wkt())
    
    w.close()
    if verbose:
        print(f'  Wrote shapefile {shapename}')
    return
