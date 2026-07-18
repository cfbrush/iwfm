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


def _read_lu_table(filename, skip, verbose=False):
    '''Read a single-date IWFM land use file.

    Parameters
    ----------
    filename : str
        IWFM land use file name

    skip : int
        number of non-comment data-spec lines to skip after the header
        comment block

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    date : str
        date of the land use data (DSS format)

    table : dict
        key = element ID (int), value = list of land use values (str,
        preserved verbatim from the input file)
    '''
    comments = 'Cc*#'

    with open(filename, encoding='utf-8') as f:
        data = f.read().splitlines()
    if verbose:
        print(f'   Read {len(data):,} lines from {filename}')

    # skip the header comment block, the data-spec lines, and any
    # comments between the data-spec lines and the data
    index = 0
    while data[index][0] in comments:
        index += 1
    index += skip
    while data[index][0] in comments:
        index += 1

    # the first data line contains the date, element ID, and land use values
    line = data[index].split()
    date = line.pop(0)
    table = {}
    table[int(line.pop(0))] = line
    index += 1

    # remaining lines: element ID and land use values
    while index < len(data):
        line = data[index].split()
        if not line:  # skip blank lines
            index += 1
            continue
        if '24:00' in line[0]:
            raise ValueError(
                f'{filename} has more than one time step; '
                'iwfm_lu4scenario() expects single-date land use files'
            )
        table[int(line.pop(0))] = line
        index += 1

    return date, table


def iwfm_lu4scenario(
    out_base_name,
    in_npag_file,
    in_ponded_file,
    in_urban_file,
    in_nvrv_file,
    skip=4,
    npag_cols=20,
    pag_cols=5,
    nvrv_cols=2,
    urban_cols=1,
    verbose=False,
):
    '''Merge four single-date IWFM land use files (non-ponded ag, ponded ag, native/riparian, urban) into one combined scenario land use table, matched by element ID.

    All four input files must contain the same element IDs. Rows are merged
    by element ID and written in ascending element order, so the files need
    not list elements in the same order.

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

    npag_cols : int, default=20
        number of non-ponded ag crop columns (default = C2VSim)

    pag_cols : int, default=5
        number of ponded ag crop columns (default = C2VSim)

    nvrv_cols : int, default=2
        number of native/riparian columns (default = C2VSim)

    urban_cols : int, default=1
        number of urban columns (default = C2VSim)

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    date, npag_table = _read_lu_table(in_npag_file, skip, verbose=verbose)
    _, pag_table = _read_lu_table(in_ponded_file, skip, verbose=verbose)
    _, urb_table = _read_lu_table(in_urban_file, skip, verbose=verbose)
    _, nvrv_table = _read_lu_table(in_nvrv_file, skip, verbose=verbose)

    # -- all four files must cover the same elements
    elems = sorted(npag_table)
    for fname, table in (
        (in_ponded_file, pag_table),
        (in_urban_file, urb_table),
        (in_nvrv_file, nvrv_table),
    ):
        if sorted(table) != elems:
            raise ValueError(
                f'element IDs in {fname} do not match those in {in_npag_file}'
            )

    # -- build one table from the four data sets, one row per element
    sources = (
        (in_npag_file, npag_table, npag_cols),
        (in_ponded_file, pag_table, pag_cols),
        (in_nvrv_file, nvrv_table, nvrv_cols),
        (in_urban_file, urb_table, urban_cols),
    )
    land_use = []
    for elem in elems:
        row = [str(elem)]
        for fname, table, ncols in sources:
            values = table[elem]
            if len(values) < ncols:
                raise ValueError(
                    f'element {elem} in {fname} has {len(values)} values, '
                    f'expected at least {ncols}'
                )
            row.extend(values[:ncols])
        land_use.append(row)

    # -- write to file
    col_names = (
        [f'NPA{i + 1}' for i in range(npag_cols)]
        + [f'PA{i + 1}' for i in range(pag_cols)]
        + (['NV', 'RV'] if nvrv_cols == 2 else
           [f'NVRV{i + 1}' for i in range(nvrv_cols)])
        + (['Urb'] if urban_cols == 1 else
           [f'Urb{i + 1}' for i in range(urban_cols)])
    )
    outFileName = out_base_name + '_Landuse.dat'
    with open(outFileName, 'w', newline='', encoding='utf-8') as outFile:
        outFile.write(f'# Date: {date}\n')
        outFile.write('# Elem\t' + '\t'.join(col_names) + '\n')
        for row in land_use:
            outFile.write('\t'.join(row))
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
        in_urban_file,in_nvrv_file,verbose=verbose)

    idb.exe_time()  # print elapsed time
