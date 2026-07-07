# iwfm_read_rz_nr.py
# Read native and riparian data from a file and organize them into lists
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


def iwfm_read_rz_nr(file, verbose=False):
    """iwfm_read_rz_nr() - Read native and riparian data from a file and organize them into lists.

    Parameters
    ----------
    file : str
        The path of the file containing the ponded crop data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------

    crops : list
        A list of crop codes

    params : list
        A list of parameters: [cnnv, cnrv, icetnv, icetrv, istrmrv, ic]

    files : list
        A list of file names: [nr_area_file]

    """
    import iwfm
    import numpy as np
    from iwfm.file_utils import read_next_line_value

    ncrops = 2                                                  # number of crop types (may be variable in future IWFM versions)

    if verbose: print(f"Entered iwfm_read_rz_nr() with {file}")

    iwfm.file_test(file)
    with open(file, encoding='utf-8') as f:
        nr_lines = f.read().splitlines()                        # open and read input file

    nr_area_file, line_index = read_next_line_value(nr_lines, -1)

    fact, line_index = read_next_line_value(nr_lines, line_index)       # root zone depth conversion factor
    fact = float(fact)

    rd_nat, line_index = read_next_line_value(nr_lines, line_index)     # native root zone depth
    rd_nat = float(rd_nat) * fact

    rd_rip, line_index = read_next_line_value(nr_lines, line_index)     # riparian root zone depth
    rd_rip = float(rd_rip) * fact

    # how many elements?
    _, line_index = read_next_line_value(nr_lines, line_index)
    ne = 0
    while (line_index + ne < len(nr_lines) and
           nr_lines[line_index+(ne)].split()[0] != 'C'):
        ne += 1

    if line_index + ne >= len(nr_lines):
        raise ValueError(
            f"'C' marker not found while counting native riparian elements at line {line_index}"
        )

    ne -= 1                                                             # one to convert to zero index

    # read native and riparian parameter table
    params, line_index = iwfm.iwfm_read_param_table_ints(nr_lines, line_index, ne)

    params = np.array(params)

    _, line_index = read_next_line_value(nr_lines, line_index)          # skip to next value line

    # initial condition
    ic, line_index = iwfm.iwfm_read_param_table_floats(nr_lines, line_index, ne)

    ic = np.array(ic)

    crops = ['nat_rip', 'ic']

    files = [nr_area_file]

    params = [params, ic]

    if verbose: print(f"Leaving iwfm_read_rz_nr()")

    return crops, params, files
