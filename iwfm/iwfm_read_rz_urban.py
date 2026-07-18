# iwfm_read_rz_urban.py
# Read urban parameter data from a file and organize them into lists
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

'''Read urban parameter data from a file and organize them into lists.'''

def iwfm_read_rz_urban(file, verbose=False):
    '''Read urban land use data from a file and organize them into lists.

    Parameters
    ----------
    file : str
        The path of the file containing the urban land use data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------

    crops : list
        A list of crop codes

    params : list
        A list of parameters: [perv, cnurb, icpopul, icwtruse, fracdm, iceturb, icrtfurb, icrufurb, icurbspec, ic]

    files : list
        A list of file names: [ur_area_file, ur_pop_file, ur_wtr_file, ur_spec_file]
    '''
    import iwfm
    import numpy as np
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered iwfm_read_rz_urban() with {file}")

    iwfm.file_test(file)
    with open(file, encoding='utf-8') as f:
        ur_lines = f.read().splitlines()                   # open and read input file

    ur_area_file, line_index = read_next_line_value(ur_lines, -1)

    factf, line_index = read_next_line_value(ur_lines, line_index)
    factf = float(factf)                                        # root zone depth conversion factor

    rooturb, line_index = read_next_line_value(ur_lines, line_index)
    rooturb = float(rooturb) * factf                            # urban root zone depth

    ur_pop_file, line_index = read_next_line_value(ur_lines, line_index)

    ur_wtr_file, line_index = read_next_line_value(ur_lines, line_index)

    ur_spec_file, line_index = read_next_line_value(ur_lines, line_index)

    # how many elements?
    _, line_index = read_next_line_value(ur_lines, line_index)
    n_elems = 0
    while (line_index + n_elems < len(ur_lines) and
           ur_lines[line_index+(n_elems)].split()[0] != 'C'):
        n_elems += 1

    if line_index + n_elems >= len(ur_lines):
        raise ValueError(
            f"'C' marker not found while counting urban elements at line {line_index}"
        )

    n_elems -= 1                                                # subtract one to convert to zero index

    # parameters = ['perv','cnurb','icpopul', 'icwtruse', 'fracdm', 'iceturb', ,icrtfurb', 'icrufurb', 'icurbspec.']
    params, line_index = iwfm.iwfm_read_param_table_floats(ur_lines, line_index, n_elems)

    params = np.array(params)

    _, line_index = read_next_line_value(ur_lines, line_index)  # skip to next value line

    # initial condition
    ic, line_index = iwfm.iwfm_read_param_table_floats(ur_lines, line_index, n_elems)

    ic = np.array(ic)

    crops = ['urban', 'ic']

    files = [ur_area_file, ur_pop_file, ur_wtr_file, ur_spec_file]

    params = [params, ic]

    if verbose: print("Leaving iwfm_read_rz_urban()")

    return crops, params, files
