# iwfm_sub_sim.py  - Read in a list of element pairs for a submodel.
# Use existing model Elements, Nodes, Stream specification and stratigraphy files
# to produce new preprocessor files for the submodel and a list of model node pairs
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


'''Read in a list of element pairs for a submodel.'''

from iwfm.debug.logger_setup import logger


def iwfm_sub_sim(in_sim_file, elem_pairs_file, out_base_name, verbose=False, debug=False):
    '''Read in a list of element pairs for a submodel.

    Use existing model Elements, Nodes, Stream specification and stratigraphy files to produce new preprocessor files for the submodel and a list of model node pairs

    Parameters
    ----------
    in_sim_file : str
        name of existing simulation main input file

    elem_pairs_file : str
        name of file listing elements of existing nmodel and submodel

    out_base_name : str
        root of submodel output file names

    verbose : bool, default=False
        turn command-line output on or off

    debug : bool, default=False
        turn debugging output on or off

    Returns
    -------
    nothing

    Notes
    -----
    Run :func:`iwfm.iwfm_sub_preproc` first — it writes the
    ``<out_base_name>_*.bin`` pickle files this function reads (elements,
    nodes, element nodes, node coordinates, stream nodes, submodel stream
    nodes). A FileNotFoundError naming the missing pickles is raised
    otherwise.
    '''
    import iwfm
    import iwfm.gis as gis
    import pickle
    from pathlib import Path

    # -- get list of file names from preprocessor input file
    sim_files, have_lake = iwfm.iwfm_read_sim_file(in_sim_file)
    if verbose:
        print(f'  Read simulation file {in_sim_file}')

    # -- resolve relative paths in sim_files to absolute paths
    sim_base_path = Path(in_sim_file).resolve().parent
    for key in sim_files:
        if isinstance(sim_files[key], str) and key.endswith('_file'):
            # Convert Windows backslashes and resolve relative to simulation file directory
            sim_files[key] = str(sim_base_path / sim_files[key].replace('\\', '/'))

    # -- verify that required input files exist
    import os
    missing_files = []
    # unsat_file is optional: IDC-based models (e.g. SVSim) have none
    required_files = ['gw_file', 'swshed_file']

    for key in required_files:
        if key not in sim_files:
            missing_files.append(f'  - {key}: Not specified in simulation input file')
        elif not os.path.exists(sim_files[key]):
            missing_files.append(f'  - {key}: {sim_files[key]}')

    if missing_files:
        missing_list = '\n'.join(missing_files)
        message = (
            f'Required input file(s) not found:\n{missing_list}\n'
            f'Please check:\n'
            f'  1. The simulation input file contains correct file paths\n'
            f'  2. All referenced files exist at the specified locations\n'
            f'  3. File paths are correct relative to the simulation input file location\n'
            f'Simulation file location: {sim_base_path}'
        )
        logger.error(message)
        raise FileNotFoundError(message)

    # -- create list of new file names
    sim_files_new = iwfm.new_sim_files(out_base_name)

    # Check that the required pickle files (written by iwfm_sub_preproc) exist
    pickle_files = [
        (out_base_name + '_elems.bin', 'elements'),
        (out_base_name + '_nodes.bin', 'nodes'),
        (out_base_name + '_elemnodes.bin', 'element nodes'),
        (out_base_name + '_node_coords.bin', 'node coordinates'),
        (out_base_name + '_snodes.bin', 'stream nodes'),
        (out_base_name + '_sub_snodes.bin', 'submodel stream nodes')
    ]

    missing_pickle_files = []
    for filepath, description in pickle_files:
        if not os.path.exists(filepath):
            missing_pickle_files.append(f'  - {description}: {filepath}')

    if have_lake:
        lake_file = out_base_name + '_lakes.bin'
        if not os.path.exists(lake_file):
            missing_pickle_files.append(f'  - lake information: {lake_file}')

    if missing_pickle_files:
        missing_list = '\n'.join(missing_pickle_files)
        message = (
            f'Required preprocessed data file(s) not found:\n{missing_list}\n'
            f'These binary files contain preprocessed model data and must be\n'
            f'generated before running this script. Please run the preprocessing\n'
            f'step that creates these files first.\n'
            f'Expected base name: {out_base_name}'
        )
        logger.error(message)
        raise FileNotFoundError(message)

    # read information from previous dump
    try:
        with open(out_base_name + '_elems.bin', 'rb') as f:
            elem_list = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_elems.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_elems.bin')

    try:
        with open(out_base_name + '_nodes.bin', 'rb') as f:
            node_list = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_nodes.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_nodes.bin')

    try:
        with open(out_base_name + '_elemnodes.bin', 'rb') as f:
            elem_nodes = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_elemnodes.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_elemnodes.bin')

    try:
        with open(out_base_name + '_node_coords.bin', 'rb') as f:
            node_coords = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_node_coords.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_node_coords.bin')

    try:
        with open(out_base_name + '_snodes.bin', 'rb') as f:
            snode_dict = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_snodes.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_snodes.bin')

    try:
        with open(out_base_name + '_sub_snodes.bin', 'rb') as f:
            sub_snodes = pickle.load(f)
    except (pickle.UnpicklingError, OSError) as e:
        logger.error(f'Failed to load pickle file {out_base_name}_sub_snodes.bin: {e}')
        raise
    logger.debug(f'Loaded pickle file {out_base_name}_sub_snodes.bin')

    if verbose:
        print('  Read model elements, nodes, node coordinates and stream nodes')

    if have_lake:
        try:
            with open(out_base_name + '_lakes.bin', 'rb') as f:
                lake_info = pickle.load(f)
        except (pickle.UnpicklingError, OSError) as e:
            logger.error(f'Failed to load pickle file {out_base_name}_lakes.bin: {e}')
            raise
        logger.debug(f'Loaded pickle file {out_base_name}_lakes.bin')
        if verbose:
            print('  Read model lakes')

    # -- create bounding polygon
    bounding_poly = gis.elem2boundingpoly(elem_nodes, node_coords)

    # -- create submodel Small Watersheds file
    iwfm.sub_swhed_file(sim_files.swshed_file, sim_files_new.swshed_file, node_list, snode_dict, verbose)

    # -- create submodel Unsaturated Zone file
    if sim_files.unsat_file and os.path.exists(sim_files.unsat_file):
        iwfm.sub_unsat_file(sim_files.unsat_file, sim_files_new.unsat_file, elem_list, verbose)
    elif verbose:
        print('  No unsaturated zone file (IDC-based model); skipped')

    # -- process submodel Groundwater files
    iwfm.sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly, sim_base_path, verbose=verbose)

    # -- process submodel Streams file
    iwfm.sub_streams_file(sim_files, sim_files_new, elem_list, sub_snodes, sim_base_path, verbose)

    # -- process submodel Rootzone file
    iwfm.sub_rootzone_file(sim_files, sim_files_new, elem_list, sub_snodes, sim_base_path, verbose)

    # -- process submodel Lake file
    # the original model may have lakes but the submodel may contain none
    sub_has_lake = have_lake and len(lake_info) > 0
    if sub_has_lake:
        iwfm.sub_lake_file(sim_files, sim_files_new, lake_info, verbose=verbose)

    if verbose:
        print(" ")


    # -- write new simulation main input file
    iwfm.sub_sim_file(in_sim_file, sim_files_new, sub_has_lake)
    if verbose:
        print(f'  Wrote submodel simulation file {sim_files_new.sim_name}')

    return  # ================================================================
    return


if __name__ == "__main__":
    ''' Run iwfm_sub_sim() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:              # arguments are listed on the command line
        in_sim_file = sys.argv[1]      # old model simulaiton.in file
        elem_pairs_file = sys.argv[2]  # file with element pairs
        out_base_name = sys.argv[3]    # output file base name
    else:  # ask for file names from terminal
        in_sim_file     = input('Existing IWFM Simulation.in file: ')
        elem_pairs_file = input('Element pairs file: ')
        out_base_name   = input('Output file base name: ')

    # == test that the input files exist
    iwfm.file_test(in_sim_file)
    iwfm.file_test(elem_pairs_file)

    idb.exe_time()  # initialize timer
    iwfm_sub_sim(in_sim_file, elem_pairs_file, out_base_name, verbose=verbose)

    if verbose:
        print(' ')
        print(
            f'  Created submodel {out_base_name} simulation files from {in_sim_file}.'
        )  # update cli
    idb.exe_time()  # print elapsed time
