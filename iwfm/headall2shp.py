# headall2shp.py
# Read headall.out file and nodal coordinates file and create shapefiles of heads
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


'''Read headall.out file and nodal coordinates file and create shapefiles of heads.'''

def headall2shp(heads_file, pre_file, out_date, basename, label='Heads', units='ft', epsg=26910, verbose=True):
    '''Read headall.out file and stratigraphy file and produce head maps.

    Parameters
    ----------
    heads_file : str
        name of headall.out file 

    pre_file : str
        name of IWFM Preprocessor main input file

    out_date : str
        date to putput (MM/DD?YYYY format)

    basename : str
        basename of output file

    label : str, default='Heads'
        label for colorbar

    units : str, default='ft'
        units for colorbar

    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    import os
    import iwfm
    import iwfm.gis as igis

    pre_path, pre_proc = os.path.split(pre_file)
    pre_files, _ = iwfm.iwfm_read_preproc(pre_file)

    node_file = os.path.join(pre_path, pre_files.node_file)
    node_coords, node_list, factor = iwfm.iwfm_read_nodes(node_file)

    # -- get heads
    data, layers, dates, nodes = iwfm.headall_read(heads_file)

    # find index of out_date in dates
    if out_date not in dates:
        from iwfm.debug.logger_setup import logger
        logger.error(f'Date {out_date} not found in {heads_file}')
        return
    index = dates.index(out_date)

    # -- coordinates
    coords = []
    for i in range(len(node_coords)):
        coords.append([node_coords[i][1], node_coords[i][2]]) 

    # get head values for all layers
    heads = []
    for layer in range(layers):
        heads.append(data[index][layer])

    # -- write shapefiles
    out_date_text = out_date.replace('/', '_')
    shape_name = f'{basename}_{out_date_text}'        #  Set shapefile name
    igis.nodal_multivalues2shp(node_coords, heads, layers, label, shape_name, epsg=epsg, verbose=verbose)

        


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
        out_date   = sys.argv[3]
        basename   = sys.argv[4]
    else:  # ask for file names from terminal
        heads_file = input('IWFM Headall file name: ')
        pre_file   = input('IWFM Preprocessor main file name: ')
        out_date   = input('Output date: ')
        basename   = input('Output file rootname: ')

    iwfm.file_test(heads_file)
    iwfm.file_test(pre_file)

    idb.exe_time()  # initialize timer

    headall2shp(heads_file, pre_file, out_date, basename, verbose=verbose)

    idb.exe_time()  # print elapsed time
