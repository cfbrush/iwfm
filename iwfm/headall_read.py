# headall_read.py
# Read headall.out file and return as lists
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


from iwfm.debug.logger_setup import logger


def headall_read(input_file, skip=5, verbose=False):
    ''' headall_read() - Reads an IWFM HeadAll.out file and returns
        the data as floats, with lists of dates and model nodes and
        the number of model layers

    Parameters
    ----------
    input_file : str
        IWFM HeadAll.out file name
    
    skip : int, default=5
        number of header lines

    verbose: bool, default=False
        True = command-line output on

    Returns
    -------
    data : list
        heads from headall file
    
    layers : int
        number of model layers
    
    dates : list
        simulation time step dates corresponding to data rows
    
    nodes : list
        model nodes corresponding to data columns

    '''

    try:
        with open(input_file, encoding='utf-8') as f:
            file_lines = f.read().splitlines()
    except FileNotFoundError:
        logger.error(f'File not found: {input_file}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {input_file}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {input_file}: {e}')
        raise
    logger.debug(f'Read {len(file_lines)} lines from {input_file}')

    line = skip
    nodes = file_lines[line].split()  
    nodes.pop(0)  
    nodes.pop(0)  
    logger.debug(f'nodes[0:4]: {nodes[:5]}')

    line += 1
    layers = 1
    while file_lines[line + layers][0] == ' ':
        layers += 1
    logger.debug(f'{layers=}')

    data, dates = [], []

    layer, temp = 0, []
    while line < len(file_lines):
        in_list = file_lines[line].split()  
        if layer == 0:
            date = in_list.pop(0)
            dates.append(date[:10])
        temp.append([float(item) for item in in_list])
        line += 1
        layer += 1
        if layer == layers:
            layer = 0
            data.append(temp)
            temp = []
    return data, layers, dates, nodes

if __name__ == '__main__':
    ' Run headall_read() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    args = sys.argv[1:]  # get command line arguments
    if len(sys.argv) > 1:  # arguments are listed on the command line
        heads_file, output_root = args
    else:  # ask for file names from terminal
        heads_file  = input('IWFM Headall file name: ')
        output_root = input('Output file rootname: ')

    iwfm.file_test(heads_file)

    idb.exe_time()  # initialize timer

    data, layers, dates, nodes = iwfm.headall_read(heads_file)

    idb.exe_time()  # print elapsed time

    print(f' Read {len(dates)} time steps with {layers} layers and {nodes} nodes.')
