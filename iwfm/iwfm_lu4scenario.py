# iwfm_lu4scenario.py
# Modify IWFM land use files for a scenario
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


def iwfm_lu4scenario(
    out_base_name,
    in_npag_file,
    in_ponded_file,
    in_urban_file,
    in_nvrv_file,
    skip=4,
    verbose=False,
):
    ''' iwfm_lu4scenario() - Modify IWFM land use files for a scenario

    TODO:
      Each land use file is done in series. Can this be replaced with a function that
        does one land use file, and use the function for each land use file?

    Parameters
    ----------
    out_base_name : str
        output files base name
    
    in_npag_file : str
        input Non-Ponded Ag Area file name
    
    in_ponded_file : str
        input Ponded Ag Area File name
    
    in_urban_file : str
        input Urban Area file name
    
    in_nvrv_file : str
        input Native and Riparian Area input file name
    
    skip : int, default=4
        number of non-comment lines to skip in each file (header)
    
    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing

    '''
    comments = 'Cc*#'

    # -- Non-Ponded Area file
    with open(in_npag_file, encoding='utf-8') as f:
        npag_data = f.read().splitlines()
    if verbose:
        print(f'   Read {len(npag_data):,} lines from {in_npag_file}')

    npag_index = 0
    while any((c in comments) for c in npag_data[npag_index][0]): 
        npag_index += 1
    for i in range(0, skip):  # skip data spec rows
        npag_index += 1
    while any((c in comments) for c in npag_data[npag_index][0]):
        npag_index += 1

    # -- compile the data from the file 
    # the first line contains the date, elemeno, and land use data
    line = npag_data[npag_index].split()
    date = line.pop(0)
    elem = line.pop(0)
    npag_table = []
    npag_table.append(line)
    npag_index += 1
    npag_cols = len(line)  # including elem_no column
    # do the remaining lines
    while npag_index < len(npag_data):
        line = npag_data[npag_index].split()
        elem = line.pop(0)
        npag_table.append(line)
        npag_index += 1

    # -- Ponded Area file
    with open(in_ponded_file, encoding='utf-8') as f:
        pag_data = f.read().splitlines() 
    if verbose:
        print(f'   Read {len(pag_data):,} lines from {in_ponded_file}')

    pag_index = 0
    while any((c in comments) for c in pag_data[pag_index][0]):
        pag_index += 1
    for i in range(0, skip):  # skip data spec rows
        pag_index += 1
    while any((c in comments) for c in pag_data[pag_index][0]):
        pag_index += 1

    # -- compile the data from the file 
    # the first line contains the date, elemeno, and land use data
    line = pag_data[pag_index].split()
    date = line.pop(0)
    elem = line.pop(0)
    pag_table = []
    pag_table.append(line)
    pag_index += 1
    pag_cols = len(line)  # including elem_no column
    # do the remaining lines
    while pag_index < len(pag_data):
        line = pag_data[pag_index].split()
        elem = line.pop(0)
        pag_table.append(line)
        pag_index += 1

    # -- Urban Area file
    with open(in_urban_file, encoding='utf-8') as f:
        urb_data = f.read().splitlines() 
    if verbose:
        print(f'   Read {len(urb_data):,} lines from {in_urban_file}')

    urb_index = 0
    while any((c in comments) for c in urb_data[urb_index][0]):
        urb_index += 1
    for i in range(0, skip):  # skip data spec rows
        urb_index += 1
    while any((c in comments) for c in urb_data[urb_index][0]):
        urb_index += 1

    # -- compile the data from the file 
    # the first line contains the date, elemeno, and land use data
    line = urb_data[urb_index].split()
    date = line.pop(0)
    elem = line.pop(0)
    urb_table = []
    urb_table.append(line)
    urb_index += 1
    urb_cols = len(line)  # including elem_no column
    # do the remaining lines
    while urb_index < len(urb_data):
        line = urb_data[urb_index].split()
        elem = line.pop(0)
        urb_table.append(line)
        urb_index += 1

    # -- Native and Riparian Area file
    with open(in_nvrv_file, encoding='utf-8') as f:
        nvrv_data = f.read().splitlines()
    if verbose:
        print(f'   Read {len(nvrv_data):,} lines from {in_nvrv_file}')

    nvrv_index = 0
    while any((c in comments) for c in nvrv_data[nvrv_index][0]):
        nvrv_index += 1
    for i in range(0, skip):  # skip data spec rows
        nvrv_index += 1
    while any((c in comments) for c in nvrv_data[nvrv_index][0]):
        nvrv_index += 1

    # -- compile the data from the file 
    # the first line contains the date, elemeno, and land use data
    line = nvrv_data[nvrv_index].split()
    date = line.pop(0)
    elem = line.pop(0)
    nvrv_table = []
    nvrv_table.append(line)
    nvrv_index += 1
    nvrv_cols = len(line)  # including elem_no column
    # do the remaining lines
    while nvrv_index < len(nvrv_data):
        line = nvrv_data[nvrv_index].split()
        elem = line.pop(0)
        nvrv_table.append(line)
        nvrv_index += 1

    # -- build one table from the four data sets
    import itertools

    land_use = []
    for i in range(0, len(npag_table)):
        npag = npag_table[i][0:20]
        pag = pag_table[i]
        urb = urb_table[i][0]
        nvrv = nvrv_table[i]
        x = []
        x.append([str(i + 1)])
        x.append(npag_table[i][0:20])
        x.append(pag_table[i][0:5])
        x.append(nvrv_table[i][0:2])
        y = list(itertools.chain.from_iterable(x))
        y.append(urb_table[i][0])
        land_use.append(y)

    # -- write to file
    outFileName = out_base_name + '_Landuse.dat'
    with open(outFileName, 'w', newline='', encoding='utf-8') as outFile:
        outFile.write(f'# Date: {date}\n')
        outFile.write(
            '# Elem\tNPA1\tNPA2\tNPA3\tNPA4\tNPA5\tNPA6\tNPA7\tNPA8\tNPA9\tNPA10\tNPA11\tNPA12\tNPA13\tNPA14\tNPA15\tNPA16\tNPA17\tNPA18\tNPA19\tNPA20\tPA1\tPA2\tPA3\tPA4\tPA5\tNV\tRV\tUrb\n'
        )
        for i in range(0, len(npag_table)):
            outFile.write('\t'.join(land_use[i]))
            outFile.write('\n')
    if verbose:
        print(f'   Wrote land use data for {date} to {outFileName}')
    return

if __name__ == '__main__':
    ' Run iwfm_lu4scenario() from command line '
    import sys
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        out_base_name = sys.argv[1]
        in_npag_file = sys.argv[2]
        in_ponded_file = sys.argv[3]
        in_urban_file = sys.argv[4]
        in_nvrv_file = sys.argv[5]
    else:  # ask for file names from terminal
        out_base_name  = input('Output file basename: ')
        in_npag_file   = input('IWFM Non-Ponded Ag file name: ')
        in_ponded_file = input('IWFM Pondes Ag file name: ')
        in_urban_file  = input('IWFM Urban file name: ')
        in_nvrv_file   = input('IWFM Native file name: ')

    iwfm.file_test(in_nvrv_file)
    iwfm.file_test(in_npag_file)
    iwfm.file_test(in_ponded_file)
    iwfm.file_test(in_urban_file)

    idb.exe_time()  # initialize timer
    iwfm_lu4scenario(out_base_name,in_npag_file,in_ponded_file,
        in_urban_file,in_nvrv_file,verbose=False)

    idb.exe_time()  # print elapsed time
