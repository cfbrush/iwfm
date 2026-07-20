# vic_2_table.py
# Extract one column from a VIC file to another file
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


'''Extract one column from a file of VIC gridded climate change factors and writes to a table, with one column for each VIC grid ID and one row for each date.'''

def vic_2_table(factorsFileName, outFileName, col, verbose=False):
    '''Extract one column from a file of VIC gridded climate change factors and writes to a table, with one column for each VIC grid ID and one row for each date.

    Parameters
    ----------
    factorsFileName : str
        VIC factors file name

    outFileName : str
        output file name

    col : int
        number of column to extract

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    import iwfm
    from iwfm.debug.logger_setup import logger

    iwfm.file_test(factorsFileName)
    try:
        with open(factorsFileName, encoding='utf-8') as f:
            factors = f.read().splitlines()  # get climate thance gactors
    except FileNotFoundError:
        logger.error(f'File not found: {factorsFileName}')
        raise
    except PermissionError:
        logger.error(f'Permission denied reading file: {factorsFileName}')
        raise
    except OSError as e:
        logger.error(f'OS error reading file {factorsFileName}: {e}')
        raise
    logger.debug(f'Read {len(factors)} lines from {factorsFileName}')
    if verbose:
        print(f'  Read {len(factors):,} lines from {factorsFileName}')

    VIC_Step = 0
    ID = int(factors[VIC_Step + 1].split(',')[0])
    first = ID
    while ID == first:
        VIC_Step += 1
        ID = int(factors[VIC_Step + 1].split(',')[0])
    VIC_No = int(len(factors) / VIC_Step)
    if verbose:
        print(f'  {VIC_No:,} VIC grid cells, {VIC_Step:,} time steps')

    VIC_dict, VIC_Grid_IDs = {} , []
    j = 1
    for i in range(1, len(factors), VIC_Step):
        temp = factors[i].split(',')
        ID = int(temp[0])
        key, values = ID, j
        VIC_dict[key] = values
        VIC_Grid_IDs.append(ID)
        j += 1

    dates = [] 
    for i in range(0, VIC_Step):
        temp = factors[i + 1].split(',')
        dates.append(temp[1].replace(' 0:00:00', ''))

    # this is messy, but it's a one-off so not (yet) worth the time to make it nice
    factor_array, line = [], 1
    items = factors[line].split(',') 
    while line < len(factors) and len(factors[line]) > 5:
        # build lists for one VIC Grid No
        temp = []
        VIC_this = int(items[0])

        while int(items[0]) == VIC_this:
            temp.append(items[col].replace('000000000000', ''))  
            line += 1  
            if line < len(factors) and len(factors[line]) > 10:
                items = factors[line].split(',')  
            else:
                items[0] = -1  # force loop exit
        factor_array.append(temp)  
    factors = []  # clear memory

    try:
        with open(outFileName, 'w', encoding='utf-8') as out_file:
            if verbose:
                print(f'  Opened {outFileName} for output')

            header = 'Date'
            for i in range(1, max(VIC_dict, key=int)):
                header = header + ',' + str(i)
            out_file.write(f'{header}\n')

            for i in range(0, VIC_Step):
                data = dates[i]
                for j in range(1, max(VIC_dict, key=int)):
                    data = (data + ',' + factor_array[VIC_dict[j] - 1][i])
                out_file.write(f'{data}\n')

            out_file.write('\n')
    except PermissionError:
        logger.error(f'Permission denied writing file: {outFileName}')
        raise
    except OSError as e:
        logger.error(f'OS error writing file {outFileName}: {e}')
        raise
    logger.debug(f'Wrote {VIC_Step} rows to {outFileName}')

    if verbose:
        print(f'  Wrote results to {outFileName}\n')

    return


if __name__ == "__main__":
    ''' Run vic_2_table() from command line '''
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        factorsFileName = sys.argv[1]
        output_file = sys.argv[2]
        col = int(sys.argv[3])
    else:                  # ask for file names from terminal
        factorsFileName = input('  P-ET factor file name: ')
        output_file     = input('  Output file name: ')
        col             = input('  Column to process:   ')

    iwfm.file_test(factorsFileName)

    idb.exe_time()  # initialize timer
    vic_2_table(factorsFileName, output_file, col, verbose=verbose)

    print(f'  Read {factorsFileName} and wrote {output_file}.')  # update cli
    idb.exe_time()  # print elapsed time
