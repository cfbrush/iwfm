# iwfm2shp.py
# Create shapefiles for an IWFM model
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


'''Take the IWFM model main preprocessor file name and a base name for output files, and create node, element, stream node and stream reach shapefiles.'''

def iwfm2shp(main_file, shape_name, epsg=26910, verbose=False):
    '''Take the IWFM model main preprocessor file name and a base name for output files, and create node, element, stream node and stream reach shapefiles.

    Parameters
    ----------
    main_file : str
        IWFM Preprocessor main file name

    shape_name : str
        output shapefiles base name

    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''

    import iwfm
    import iwfm.gis as igis

    pre_files, have_lake = iwfm.iwfm_read_preproc(main_file)
    if verbose:
        print(f'  Read preprocessor file {main_file}')

    elem_ids, elem_nodes, elem_sub = iwfm.iwfm_read_elements(pre_files.elem_file) 
    if verbose:
        print(f'  Read nodes of {len(elem_nodes):,} elements from {pre_files.elem_file}')

    node_coords, node_list, factor = iwfm.iwfm_read_nodes(pre_files.node_file, factor = 1)
    if verbose:
        print(f'  Read coordinates of {len(node_coords):,} nodes from {pre_files.node_file}')

    node_coord_dict = {row[0]: row[1:] for row in node_coords}  # list to dictionary

    node_strat, nlayers = iwfm.iwfm_read_strat(pre_files.strat_file, node_coords)
    if verbose:
        print(f'  Read stratigraphy for {len(node_strat):,} nodes from {pre_files.strat_file}')

    if have_lake:
        n_lake_elems, lakes = iwfm.iwfm_read_lake(pre_files.lake_file)  
        if verbose:
            if len(lakes) > 1:
                print(f'  Read info for {len(lakes):,} lakes from {pre_files.lake_file}')
            elif len(lakes) == 1:
                print(f'  Read info for {len(lakes):,} lake from {pre_files.lake_file}')
    else:
        lakes = None
        if verbose:
            print('  No lakes file')

    reach_list, snodes_list, stnodes_dict, nsnodes, rating_dict = iwfm.iwfm_read_streams(pre_files.stream_file)
    if verbose:
        print(f'  Read info for {len(reach_list):,} stream reaches and {nsnodes:,} stream nodes from {pre_files.stream_file}')

    if verbose:
        print(' ')

    # == Create element shapefile
    igis.elem2shp(elem_ids,elem_nodes,node_coord_dict,elem_sub,lakes,shape_name,epsg=epsg,verbose=verbose)

    # == Create node shapefile
    igis.nodes2shp(node_coords, shape_name,epsg=epsg,verbose=verbose)

    # == Create stream node shapefile
    igis.snodes2shp(nsnodes, snodes_list, node_coords, shape_name,epsg=epsg,verbose=verbose)

    # == Create stream reach shapefile
    igis.reach2shp(reach_list, stnodes_dict, node_coords, shape_name,epsg=epsg,verbose=verbose)

    return 


if __name__ == '__main__':
    ' Run iwfm2shp() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    epsg=26910	# default UTM 10N (CA)

    if len(sys.argv) > 1:  # arguments are listed on the command line
        input_file = sys.argv[1]
        output_basename = sys.argv[2]
        if len(sys.argv) > 3:
       		epsg=int(sys.argv[3]) 
    else:  # ask for file names from terminal
        input_file = input('IWFM Preprocessor main file name: ')
        output_basename = input('Output shapefile basename: ')
        projection = input('Projection EPSG integer value (blank for default UTM 10N): ')
        if len(projection) >1:
        	epsg=int(projection) 

    iwfm.file_test(input_file)

    idb.exe_time()  # initialize timer
    iwfm2shp(input_file, output_basename, epsg, verbose=verbose)

    idb.exe_time()  # print elapsed time
