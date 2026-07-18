# headall2dtw.py
# Read headall.out file and stratigraphy file and write depth to water with
# one csv file for each model layer
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


def headall2dtw(heads_file, pre_file, output_root, verbose=False):
    '''Read IWFM HeadAll.out file, subtract heads from land surface elevation, and write out as a time series with one csv file for each layer.

    Parameters
    ----------
    heads_file : str
        name of headall.out file 

    pre_file : str
        name of IWFM Preprocessor main input file

    output_root : str
        basename of output file

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing

    Raises
    ------
    FileNotFoundError
        If ``heads_file`` does not exist (checked first, before
        preprocessor parsing). This is the canonical recoverable signal
        for missing heads input.
    FileNotFoundError
        If ``pre_file`` does not exist or its referenced node/strat files
        are missing (raised inside :func:`iwfm.iwfm_read_preproc` →
        :func:`iwfm.file_test`).
    '''
    from pathlib import Path

    import numpy as np
    import iwfm

    heads_path = Path(heads_file)
    if not heads_path.is_file():
        raise FileNotFoundError(f"heads file not found: {heads_file}")

    pre_path = Path(pre_file).parent
    pre_files, _ = iwfm.iwfm_read_preproc(pre_file)

    node_file = str(pre_path / pre_files.node_file)
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file)

    strat_file = str(pre_path / pre_files.strat_file)
    strat, nlayers = iwfm.iwfm_read_strat(strat_file, node_coords)

    elevations = iwfm.iwfm_lse(strat)
    lse = np.asarray([i[1] for i in elevations])

    # -- get heads
    data, layers, dates, nodes = iwfm.headall_read(heads_file)
    heads = np.asarray(data)

    # -- calculate depth from land surface
    # heads has shape (timesteps, layers, nodes)
    # lse has shape (nodes,)
    # Broadcasting creates dtw with shape (timesteps, layers, nodes)
    dtw = lse - heads

    # -- reshape from (timesteps, layers, nodes) to (timesteps * layers, nodes)
    # This flattens the first two dimensions while keeping nodes separate
    timesteps = dtw.shape[0]
    dtw_reshaped = dtw.reshape(timesteps * layers, -1)

    # -- write to csv files
    iwfm.headall2csv(
        np.around(dtw_reshaped, 3),
        layers,
        dates,
        nodes,
        output_root,
        verbose=verbose,
    )
    return


if __name__ == '__main__':
    ' Run headall2dtw() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file = sys.argv[1]
        pre_file = sys.argv[2]
        output_root = sys.argv[3]
    else:  # ask for file names from terminal
        heads_file  = input('IWFM Headall file name: ')
        pre_file    = input('IWFM Preprocessor main file name: ')
        output_root = input('Output file rootname: ')

    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)

    output_file = heads_file.split('.')[0]

    idb.exe_time()  # initialize timer

    headall2dtw(heads_file, pre_file, output_root, verbose=verbose)

    idb.exe_time()  # print elapsed time
