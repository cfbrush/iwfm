# iwfm_read_bud.py
# Read IWFM Budget main file
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

def iwfm_read_bud(bud_file, verbose=False):
    ''' iwfm_read_bud() - Read an IWFM Budget main input file, and 
        return a list of lists with the file information and some settings

    Parameters
    ----------
    but_file : str
        Name of IWFM Budget file

    verbose : bool, default=False
        Turn command-line output on or off
            
     Returns
    -------
    budget_list : list of lists
        Input and output file names, times etc

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(bud_file)
    with open(bud_file, encoding='utf-8') as f:
        bud_lines = f.read().splitlines()

    # read factors and labels
    factlou, line_index = read_next_line_value(bud_lines, -1, column=0)
    factlou = float(factlou)

    unutlou, line_index = read_next_line_value(bud_lines, line_index, column=0)

    factarou, line_index = read_next_line_value(bud_lines, line_index, column=0)
    factarou = float(factarou)

    unitarou, line_index = read_next_line_value(bud_lines, line_index, column=0)

    factvolou, line_index = read_next_line_value(bud_lines, line_index, column=0)
    factvolou = float(factvolou)

    unitvolou, line_index = read_next_line_value(bud_lines, line_index, column=0)

    cache, line_index = read_next_line_value(bud_lines, line_index, column=0)

    # read begin and end dates
    bdt, line_index = read_next_line_value(bud_lines, line_index, column=0)

    edt, line_index = read_next_line_value(bud_lines, line_index, column=0)

    # number of budgets to process
    nbudget, line_index = read_next_line_value(bud_lines, line_index, column=0)
    nbudget = int(nbudget)

    factors = [nbudget, factlou, unutlou, factarou, unitarou, factvolou, unitvolou, bdt, edt]

    budget_list = []
    for b in range(nbudget):
        hdffile, line_index = read_next_line_value(bud_lines, line_index, column=0)

        outfile, line_index = read_next_line_value(bud_lines, line_index, column=0)

        intprnt, line_index = read_next_line_value(bud_lines, line_index, column=0)

        nlprint, line_index = read_next_line_value(bud_lines, line_index, column=0)

        lprint, line_index = read_next_line_value(bud_lines, line_index, column=0)

        budget_list.append([hdffile, outfile, intprnt, nlprint, lprint])

    return budget_list, factors


