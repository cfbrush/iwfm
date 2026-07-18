# iwfm_read_et_vals.py 
# Read evapotranspiration values from a file and organize them into lists
# Copyright (C) 2023-2026 University of California
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

def read_param_table_ints(file_lines, line_index, lines):
    '''Read a table of integer parameters from a file and organize them into lists.

    Parameters
    ----------
    file_lines : list
        File contents as list of lines

    line_index : int
        The index of the line to start reading from.

    lines : int
        The number of lines to read.

    Returns
    -------

    params : list
        A list of parameters
    '''


    params = []
    if int(file_lines[line_index].split()[0]) == 0:                  # one set of parameter values for all elements
        params = [int(e) for e in file_lines[line_index].split()]
    else:
        for i in range(lines):
            t = [int(e) for e in file_lines[line_index].split()]
            params.append(t)
            line_index += 1

    return params, line_index

def read_param_table_floats(file_lines, line_index, lines):
    '''Read a table of integer parameters from a file and organize them into lists.

    Parameters
    ----------
    file_lines : list
        File contents as list of lines

    line_index : int
        The index of the line to start reading from.

    lines : int
        The number of lines to read.

    Returns
    -------

    params : list
        A list of parameters
    '''

    from iwfm.file_utils import read_next_line_value

    params = []
    if int(file_lines[line_index].split()[0]) == 0:                  # one set of parameter values for all elements
        params = [float(e) for e in file_lines[line_index].split()]
        params[0] = int(params[0])
        _, line_index = read_next_line_value(file_lines, line_index, column=0)  # skip to next value line
    else:
        for i in range(lines):
            t = [float(e) for e in file_lines[line_index].split()]
#            print(f' *** {t=}')
            t[0] = int(t[0])
            params.append(t)
            line_index += 1                                         # skip to next line
    line_index -= 1

    return params, line_index


def iwfm_read_et_vals(et_file, verbose=False):
    '''Read evapotranspiration values from a file and organize them into lists.

    Parameters
    ----------
    et_file : str
        The path of the file containing the evapotranspiration data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------

    params : list
        A list of evapotranspiration values
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(et_file)
    with open(et_file, encoding='utf-8') as f:
        et_lines = f.read().splitlines()                   # open and read input file

    nevap, line_index = read_next_line_value(et_lines, -1, column=0)  # skip to next value line
    nevap = int(nevap)                                          # number of columns

    factet, line_index = read_next_line_value(et_lines, line_index, column=0)  # skip to next value line
    factet = float(factet)                                      # conversion factor

    nspet, line_index = read_next_line_value(et_lines, line_index, column=0)  # skip to next value line
    nspet = int(nspet)                                          # number of timesteps to update et data

    nfqet, line_index = read_next_line_value(et_lines, line_index, column=0)  # skip to next value line
    nfqet = int(nfqet)                                          # repetition requency of et data

    dssfl, line_index = read_next_line_value(et_lines, line_index, column=0)  # skip to next value line
                                                                # dss file name

    _, line_index = read_next_line_value(et_lines, line_index, column=0)  # skip to next value line

    # evapotranspiration data
    et = []
    while line_index < len(et_lines) and len(et_lines[line_index]) > 10:
        t = et_lines[line_index].split()
        for i in range(1,nevap):
            t[i] = float(t[i])
        et.append(t)
        line_index += 1

    params = et

    return params
