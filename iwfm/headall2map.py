# headall2map.py
# Read headall.out file and nodal coordinates file and produce head maps
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


def headall2map(heads_file, pre_file, bnds_file, out_date, basename, label='Heads', units='ft', verbose=False):
    ''' headall2map() - Read headall.out file and stratigraphy file and 
            produce head maps

    Parameters
    ----------
    heads_file : str
        name of headall.out file 
    
    pre_file : str
        name of IWFM Preprocessor main input file

    bnds_file : str
        name of boundary file

    out_date : str
        date to putput (MM/DD?YYYY format)

    basename : str
        basename of output file

    label : str, default='Heads'
        label for colorbar

    units : str, default='ft'
        units for colorbar
    
    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    
    '''
    import os
    import numpy as np
    import iwfm
    import iwfm.plot as iplot

    pre_path, pre_proc = os.path.split(pre_file)
    pre_files, _ = iwfm.iwfm_read_preproc(pre_file)

    node_file = os.path.join(pre_path, pre_files.node_file)
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file)

    strat, nlayers = iwfm.iwfm_read_strat(pre_files.strat_file, node_coords)
    strat = np.array([np.array(i) for i in strat])    # strat to numpy array

    bnds_d = iwfm.file2dict(bnds_file, key_field=0, val_field=1, skip=1, key_type=int, val_type=int)
    bounding_poly = iwfm.bnds2mask(bnds_d, node_coords)

    # -- get heads
    data, layers, dates, nodes = iwfm.headall_read(heads_file)

    # find index of out_date in dates
    if out_date not in dates:
        from iwfm.debug.logger_setup import logger
        logger.error(f'Date {out_date} not found in {heads_file}')
        return
    index = dates.index(out_date)

    # map heads for each layer for out_date
    for layer in range(layers):
        heads = data[index][layer]

        plot_data = []
        for i in range(len(heads)):
            plot_data.append([node_coords[i][1], node_coords[i][2], heads[i]]) 

        #  Produce point map
        image_name = f'{basename}_Layer_{layer+1}_nodes.tiff'        #  Set image file name
        iplot.map_to_nodes(plot_data, bounding_poly, image_name, title=f'Heads for {out_date}, layer {layer+1}',
                           marker_size = 20, label=label, units=units, verbose=verbose )

        #  Produce coutrour lines map
        image_name = f'{basename}_Layer_{layer+1}_contour.tiff'        #  Set image file name
        iplot.map_to_nodes_contour(plot_data, bounding_poly, image_name, title=f'Heads for {out_date}, layer {layer+1}',
                           label=label, units=units, verbose=verbose )
        
        #  Produce filled coutrour map
        image_name = f'{basename}_Layer_{layer+1}_contourf.tiff'        #  Set image file name
        iplot.map_to_nodes_contour(plot_data, bounding_poly, image_name, title=f'Heads for {out_date}, layer {layer+1}',
                           label=label, units=units, contour='filled', verbose=verbose )
        


if __name__ == '__main__':
    ' Run headall2map() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file = sys.argv[1]
        pre_file   = sys.argv[2]
        bnds_file  = sys.argv[3]      # boundary.csv file file
        out_date   = sys.argv[4]
        basename   = sys.argv[5]
    else:  # ask for file names from terminal
        heads_file = input('IWFM Headall file name: ')
        pre_file   = input('IWFM Preprocessor main file name: ')
        bnds_file  = input('Model boundary CSV file name: ')
        out_date   = input('Output date: ')
        basename   = input('Output file rootname: ')

    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)
    iwfm.file_test(bnds_file)

    idb.exe_time()  # initialize timer

    headall2map(heads_file, pre_file, bnds_file, out_date, basename)

    idb.exe_time()  # print elapsed time
