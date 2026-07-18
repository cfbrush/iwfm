# iwfm_sub_preproc.py 
# Read in a list of element pairs for a submodel. Use existing model Elements, 
# Nodes, Stream specification and stratigraphy files to produce new 
# preprocessor files for the submodel and a list of model node pairs
# Copyright (C) 2018-2026 University of California
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


'''Read in a list of element pairs for a submodel.

Use existing model Elements, Nodes, Stream specification and stratigraphy files to produce new preprocessor files for the submodel and a list of model node pairs.
'''

def iwfm_sub_preproc(
    in_pp_file, elem_pairs_file, out_base_name, verbose=False):
    '''Read in the Preprocessor main file of a model and a list of element pairs for a submodel.

    Use existing model Elements, Nodes, Stream specification, Lake and Stratigraphy files to produce new preprocessor files for the submodel, and pickle files of submodel nodes, stream nodes and lakes

    Parameters
    ----------
    in_pp_file : str
        name of existing preprocessor main input file

    elem_pairs_file : str
        name of file listing elements of existing nmodel and submodel

    out_base_name : str
        root of submodel output file names

    verbose : bool, default=False
        turn command-line output on or off

    Returns
    -------
    pre_files_new : PreprocessorFiles
        PreprocessorFiles dataclass of submodel preprocessor file names

    sub_elem_list : ints
        list of existing model elements in submodel

    new_srs : ints
        list of existing model subregions in submodel

    elem_dict : dict
        dictionary existing model element to submodel element

    sub_node_list : ints
        list of existing model nodes in submodel

    snode_dict : ints
        list of existing model stream nodes in submodel

    lake_info : list
        description of each lake in the submodel
    '''
    import iwfm
    import pickle
    import polars as pl
    from iwfm.debug.logger_setup import logger

    # -- get list of file names from preprocessor input file
    pre_files, have_lake = iwfm.iwfm_read_preproc(in_pp_file)
    if verbose:
        print(f'  Read preprocessor file {in_pp_file}')

    # -- create list of new file names
    pre_files_new = iwfm.new_pp_files(out_base_name)

    # -- read submodel elements
    sub_elem_list, new_srs, elem_dict, rev_elem_dict = iwfm.get_elem_list(elem_pairs_file)
    try:
        with open(out_base_name + '_elems.bin', 'wb') as f:
            pickle.dump(sub_elem_list, f)  # dump sub_elem_list to file
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_elems.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_elems.bin')
    if verbose:
        print(f'  Read submodel element pairs file {elem_pairs_file}')

    # -- determine submodel nodes
    sub_node_list = iwfm.sub_pp_node_list(pre_files.elem_file, sub_elem_list)
    try:
        with open(out_base_name + '_nodes.bin', 'wb') as f:
            pickle.dump(sub_node_list, f)  # dump sub_node_list to file
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_nodes.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_nodes.bin')
    if verbose:
        print('  Compiled list of submodel nodes')

    # -- get submodel node coordinates
    node_coord, node_list, factor = iwfm.iwfm_read_nodes(pre_files.node_file)

    i = 0
    while i < len(node_coord):
        if node_coord[i][0] not in sub_node_list:
            del(node_coord[i])
        else:
            i += 1

    try:
        with open(out_base_name + '_node_coords.bin', 'wb') as f:
            pickle.dump(node_coord, f)  # dump node_coords to file
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_node_coords.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_node_coords.bin')
    if verbose:
        print('  Compiled list of submodel nodal coordinates')

    # -- determine submodel stream nodes
    reach_info, snode_dict, rattab_dict, rating_header, stream_aq, sub_snodes = iwfm.sub_pp_streams(
        pre_files.stream_file, sub_node_list
    )

    # dump sub_nodes to file
    try:
        with open(out_base_name + '_sub_snodes.bin', 'wb') as f:
            pickle.dump(sub_snodes, f)
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_sub_snodes.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_sub_snodes.bin')

    # dump snode_dict to file
    try:
        with open(out_base_name + '_snodes.bin', 'wb') as f:
            pickle.dump(snode_dict, f)
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_snodes.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_snodes.bin')

    if verbose:
        print('  Compiled list of submodel stream nodes')

    # -- determine submodel lakes
    if have_lake:
        lake_info, have_lake = iwfm.sub_pp_lakes(pre_files.lake_file, sub_elem_list)
        # dump lake_info to file
        try:
            with open(out_base_name + '_lakes.bin', 'wb') as f:
                pickle.dump(lake_info, f)
        except (PermissionError, OSError) as e:
            logger.error(f'Failed to write pickle file {out_base_name}_lakes.bin: {e}')
            raise
        logger.debug(f'Wrote pickle file {out_base_name}_lakes.bin')
        if have_lake and verbose:
            print('  Compiled list of submodel lakes')

    # create polars dataframe for submodel and write to parquet
    df = pl.DataFrame(
        {
            'node_id':  [row[0] for row in node_coord],
            'easting':  [row[1] for row in node_coord],
            'northing': [row[2] for row in node_coord],
        }
    )
    try:
        df.write_parquet(out_base_name + '_df.parquet')
    except OSError as e:
        logger.error(f'Failed to write parquet file {out_base_name}_df.parquet: {e}')
        raise
    logger.debug(f'Wrote parquet file {out_base_name}_df.parquet')

    if verbose:
        print(' ')

    # -- write new node file
    iwfm.sub_pp_node_file(pre_files.node_file, pre_files_new.node_file, sub_node_list)
    if verbose:
        print(f'  Wrote submodel node file {pre_files_new.node_file}')

    # -- write new element file
    elem_nodes = iwfm.sub_pp_elem_file(
        pre_files.elem_file, pre_files_new.elem_file, sub_elem_list, new_srs
    )
    try:
        with open(out_base_name + '_elemnodes.bin', 'wb') as f:
            pickle.dump(elem_nodes, f)
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write pickle file {out_base_name}_elemnodes.bin: {e}')
        raise
    logger.debug(f'Wrote pickle file {out_base_name}_elemnodes.bin')
    if verbose:
        print(f'  Wrote submodel element file {pre_files_new.elem_file}')

    # -- write new stratigraphy file
    iwfm.sub_pp_strat_file(
        pre_files.strat_file, pre_files_new.strat_file, sub_node_list
    )
    if verbose:
        print(f'  Wrote submodel stratigraphy file {pre_files_new.strat_file}')

    # -- write new stream specification file
    iwfm.sub_pp_stream_file(
        pre_files.stream_file,
        pre_files_new.stream_file,
        snode_dict,
        reach_info,
        rattab_dict,
        rating_header,
        stream_aq,
    )
    if verbose:
        print(f'  Wrote submodel stream specification file {pre_files_new.stream_file}')

    # -- write new lake file
    if have_lake:
        iwfm.sub_pp_lake_file(
            pre_files.lake_file, pre_files_new.lake_file, lake_info
        )
        if verbose:
            print(
                f'  Wrote submodel lake specification file {pre_files_new.lake_file}'
            )

    # -- write new preprocesor main input file
    iwfm.sub_pp_file(in_pp_file, pre_files, pre_files_new, have_lake)
    if verbose:
        print(f'  Wrote submodel preprocessor file {pre_files_new.prename}')

    if not have_lake:
        lake_info=[]
    logger.info(f'Completed submodel preprocessing for {out_base_name}')
    return pre_files_new, sub_elem_list, new_srs, elem_dict, sub_node_list, snode_dict, lake_info
    

if __name__ == "__main__":
    ''' Run iwfm_sub_preproc() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:  # arguments are listed on the command line
        in_pp_file = sys.argv[1]       # in: old model preprocessor.in file
        elem_pairs_file = sys.argv[2]  # in: file with element pairs
        out_base_name = sys.argv[3]    # output file base name
    else:  # ask for file names from terminal
        in_pp_file      = input('Existing IWFM Preprocessor.in file: ')
        elem_pairs_file = input('Element pairs file: ')
        out_base_name   = input('Output file base name: ')

    # == test that the input files exist
    iwfm.file_test(in_pp_file)
    iwfm.file_test(elem_pairs_file)

    idb.exe_time()  # initialize timer
    iwfm_sub_preproc(in_pp_file, elem_pairs_file, out_base_name, verbose=verbose)

    if verbose:
        print(' ')
        print(f'  Created submodel {out_base_name} preprocessor files from {in_pp_file}')
    idb.exe_time()  # print elapsed time


