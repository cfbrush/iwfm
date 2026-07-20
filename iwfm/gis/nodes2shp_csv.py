# nodes2shp_csv.py
# Read csv file of nodes and create a shapefile of the nodes with the node ids
# Copyright (C) 2024 University of California
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

'''Create a shapefile of the nodes with the node ids.'''

def nodes2shp_csv(node_coord_dict, shapename='nodes.shp', epsg=26910, verbose=False):
    '''Create a shapefile of the nodes with the node ids.

    Parameters
    ----------
    node_coord_dict : dict
        Dictionary of node coordinates

    shapename : str, default 'nodes.shp'
        Name of the shapefile to be created

    epsg : int, default 26910
        EPSG code for the shapefile

    verbose : bool, default False
        Print information to the console

    Returns
    -------
    nothing



    '''

    import shapefile
    import pyproj

    # convert node_coord_dict to a list of node ids and coordinates
    node_coords = [(key, value) for key, value in node_coord_dict.items()]

    # Create a new shapefile writer object
    shapename = shapename.replace('.shp', '')  # remove extension if present
    w = shapefile.Writer(shapename, shapeType=shapefile.POINT)
    
    # Define fields
    w.field('node_id', 'N', 10, 0)  # Integer
    w.field('x', 'F', 15, 6)        # Float with 6 decimals
    w.field('y', 'F', 15, 6)        # Float with 6 decimals

    # Write features
    for i in range(len(node_coords)):
        x, y = float(node_coords[i][1][0]), float(node_coords[i][1][1])
        w.point(x, y)  # Add geometry
        w.record(      # Add attributes
            int(node_coords[i][0]),  # node_id
            x,                       # x
            y                        # y
        )
    
    # Write projection file
    with open(f"{shapename}.prj", "w", encoding='utf-8') as prj:
        epsg = f'EPSG:{epsg}'
        prj.write(pyproj.CRS(epsg).to_wkt())
    
    w.close()
    if verbose: print(f'  Wrote shapefile {shapename}.shp')


if __name__ == "__main__":
    ''' Run nodes2shp from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv
    epsg=26910

    if len(sys.argv) > 1:  # arguments are listed on the command line
        node_file_name  = args[1]
    else:  # ask for file names from terminal
        node_file_name  = input('Nodes csv file name: ')

    iwfm.file_test(node_file_name)

    idb.exe_time()                                              # initialize timer

    # Read coarse elements and nodes
    node_ids, node_coord_dict = iwfm.read_nodes_csv(node_file_name)          
    if verbose: print(f'  Read {len(node_ids):,} nodes from {node_file_name}')

    shapename = node_file_name.replace('.csv', '.shp')

    # Wtrite elements to shapefile
    nodes2shp_csv(node_coord_dict, shapename=shapename, epsg=epsg, verbose=verbose)


    idb.exe_time()                                          # print elapsed time
