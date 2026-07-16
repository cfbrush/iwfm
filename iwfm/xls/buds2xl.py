# buds2xl.py
# Read information from an IWFM Budget.in file and write output to
# an Excel file (perhaps in future also to csv file or other type of file)
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


def buds2xl(bud_file, type='xlsx', verbose=False):
    ''' buds2xl() - Read IWFM Budget.in file and write output to an Excel
        or csv file

    Parameters
    ----------
    bud_file : string
        IWFM Budget.in file name

    type : string, default='xlsx'
        Output file style

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    nothing

    '''

    import os
    import iwfm
    import iwfm.hdf5 as hdf5
    from iwfm.xls import create_workbook, write_budget_data, save_workbook, close_workbook

    budget_list, factors = iwfm.iwfm_read_bud(bud_file, verbose=verbose)  # read budget file
    nbudget, factlou, unitlou, factarou, unitarou, factvolou, unitvolou, bdt, edt = factors

    if verbose: print(f'   {nbudget} budgets found in {bud_file}')

    for budget in range(nbudget):
        hdffile, outfile, intprnt, nlprint, lprint = budget_list[budget]
        if verbose: print(f'   Processing {hdffile}')

        budget_data   = hdf5.get_budget_data(hdffile,
                                area_conversion_factor=factarou,
                                volume_conversion_factor=factvolou,
                                length_units=unitlou,
                                area_units=unitarou,
                                volume_units=unitvolou,
                                verbose=verbose) # (loc_names, column_headers, loc_values, titles)

        if type=='xlsx':   # default type is Excel
            xlfile = outfile[:outfile.index('.bud')] + '.xlsx'  # Excel file name

            # Create workbook with filename
            workbook = create_workbook(os.path.abspath(xlfile))

            # Write budget data to workbook
            write_budget_data(workbook, budget_data)

            # Save and close workbook
            save_workbook(workbook)
            close_workbook(workbook)

        elif type=='csv':     # for future use?
            pass

        else:
            pass


if __name__ == '__main__':
    ' Run from command line '
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        bud_file = sys.argv[1]

    else:  # ask for file names from terminal
        bud_file = input('IWFM Budget file name: ')
        print('')

    idb.exe_time()  # initialize timer

    buds2xl(bud_file, verbose=verbose)

    idb.exe_time()  # print elapsed time


