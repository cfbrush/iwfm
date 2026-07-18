# iwfm_read_precip_vals.py 
# Read precipition values from a file and organize them into lists
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

'''Read precipition values from a file and organize them into lists.'''

def iwfm_read_precip_vals(precip_file, verbose=False):
    '''Read precipitation values from a file and organize them into lists.

    Parameters
    ----------
    precip_file : str
        The path of the file containing the precipitation data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------

    params : list
        A list of precipitation values
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value

    iwfm.file_test(precip_file)
    with open(precip_file, encoding='utf-8') as f:
        pr_lines = f.read().splitlines()                                # open and read input file

    nrain, line_index = read_next_line_value(pr_lines, -1)              # number of columns
    nrain = int(nrain)

    factrn, line_index = read_next_line_value(pr_lines, line_index)     # conversion factor
    factrn = float(factrn)

    nsprn, line_index = read_next_line_value(pr_lines, line_index)      # number of timesteps to update et data
    nsprn = int(nsprn)

    nfqrn, line_index = read_next_line_value(pr_lines, line_index)      # repetition frequency of et data
    nfqrn = int(nfqrn)

    dssfl, line_index = read_next_line_value(pr_lines, line_index)      # dss file name

    _, line_index = read_next_line_value(pr_lines, line_index)          # skip to first data line

    # precipitation data
    precip = []
    while line_index < len(pr_lines) and len(pr_lines[line_index]) > 10:
        t = pr_lines[line_index].split()
        for i in range(1, nrain):
            t[i] = float(t[i])
        precip.append(t)
        line_index += 1

    return precip
