# read_overwrite_file.py
# Read IWFM Groundwater Overwrite file
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


def read_overwrite_file(overwrite_file, nnodes, nlay, param_types, verbose=False):
    '''Open and read an IWFM-2015 overwrite file or overwrite template file, and return the number of nodes, the scaling factors, and the parameter values.

         From REAL2IGSM.F90 by Matt Tonkin, with modifications by others

    Parameters
    ----------
    overwrite_file : str
        Overwrite file name

    nnodes : int
        Number of nodes with parameter values

    nlat : int
        Number of model layers

    param_types : list of strs
        Parameter type codes

    verbose : bool, default=False
        Print to screen?

    Returns
    -------
    nwrite : int
        number of parameter lines in overwrite file

    factors : list
        multiplication factors

    ctimes : list of strs
        time steps in DSS format

    parvals_d : dict
        parameter values for each node and layer

    in_lines : list
        each item is one line from the overwrite file
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(overwrite_file)
    with open(overwrite_file, encoding='utf-8') as f:
        in_lines = f.read().splitlines()               # open and read input file

    if not in_lines:
        raise ValueError(f'ERROR: Overwrite file "{overwrite_file}" is empty.\n'
                        f'       This file must contain a valid IWFM overwrite template.\n'
                        f'       Please provide a valid overwrite file or create a template file.')

    nwrite_str, line_index = read_next_line_value(in_lines, -1, column=0, skip_lines=0)

    if line_index >= len(in_lines):
        raise ValueError(f'ERROR: Overwrite file "{overwrite_file}" contains only comments or is improperly formatted.\n'
                        f'       Expected NWRITE value after comment lines but reached end of file.')

    nwrite = int(nwrite_str)                                          # no. of parameter lines

    _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=1)
    factors = [in_lines[line_index].split()[0] for i in range(0,7)]   # scaling factors

    _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=4)

    _, line_index = read_next_line_value(in_lines, line_index - 1, skip_lines=0)

    parvals_d = {}
    for line in in_lines[line_index:]:                                # skip comments
        if line[0] == 'C':
            break
        line = line.split()
        key = f'{line[0]}_{line[1]}'

        temp = {"node": int(line[0]), "layer": int(line[1]), "pkh": float(line[2]), 
                "ps": float(line[3]), "pn": float(line[4]), "pv": float(line[5]), 
                "pl": float(line[6]), "sce": float(line[7]), "sci": float(line[8])}
        parvals_d[key] = temp

    return nwrite, factors, parvals_d, in_lines

