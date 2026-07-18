# iwfm_read_rz_params.py 
# Read root zone parameters from a file and organize them into lists
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

'''Read root zone parameters from a file and organize them into lists.'''

def iwfm_read_rz_params(rz_file, verbose=False):
    '''Read root zone parameters from a file and organize them into lists.

    Parameters
    ----------
    rz_file : str
        The path of the file containing the root zone data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    params : list
        A list containing parameter values. It consists of 13 sublists, each representing a different parameter.
    '''

    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"  Entered iwfm_read_rz_params() with {rz_file=}")

    iwfm.file_test(rz_file)
    with open(rz_file, encoding='utf-8') as f:
        rz_lines = f.read().splitlines()                # open and read input file

    factk, line_index = read_next_line_value(rz_lines, -1, skip_lines=18)  # skip four parameters and 15 file names
    factk = float(factk)                                        # K multiplier

    factcp, line_index = read_next_line_value(rz_lines, line_index)
    factcp = float(factcp)                                      # capillary rise multiplier

    tkunit, line_index = read_next_line_value(rz_lines, line_index)  # K time unit

    _, line_index = read_next_line_value(rz_lines, line_index)  # skip to parameter table 

    #  Lists for each parameter
    params = [[], [], [], [], [], [], [], [], [], [], [], [], []]
   
    #  Read the relevant lines of the RootZone.dat file
    lines = rz_lines[line_index:]                        #  The remaining lines contain the parameters

    #  Loop through all of the lines
    for values in lines:
        values = values.split()                         #  Split the line into individual values
        values = values[1:]
        #  Add values to their corresponding parameter's list
        for idx, value in enumerate(values[0:13]):
            if idx == 4:
                value = float(value) * factk
            elif idx == 6:
                value = float(value) * factcp
            params[idx].append(float(value))
    
    if verbose: print("  Leaving iwfm_read_rz_params()")

    return params

