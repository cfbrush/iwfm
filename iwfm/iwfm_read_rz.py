# iwfm_read_rz.py 
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

def iwfm_read_rz(rz_file, verbose=False):
    '''Read an IWFM Rootzone main input file and return a list of the files called.

    Parameters
    ----------
    rz_file : str
        name of existing model rootzone file

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    rz_files : RootzoneFiles
        dataclass of existing model rootzone file names
    '''

    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import RootzoneFiles

    if verbose: print(f"Entered iwfm_read_rz() with {rz_file}")

    iwfm.file_test(rz_file)
    with open(rz_file, encoding='utf-8') as f:
        rz_lines = f.read().splitlines()                # open and read input file

    np_file, line_index = read_next_line_value(rz_lines, -1, skip_lines=4)  # non-ponded ag file

    p_file, line_index = read_next_line_value(rz_lines, line_index)   # ponded ag file

    ur_file, line_index = read_next_line_value(rz_lines, line_index)  # urban file

    nr_file, line_index = read_next_line_value(rz_lines, line_index)  # native and riparian file

    rf_file, line_index = read_next_line_value(rz_lines, line_index)  # return flow file

    ru_file, line_index = read_next_line_value(rz_lines, line_index)  # reuse file

    ir_file, line_index = read_next_line_value(rz_lines, line_index)  # irrigation period file

    if verbose: print("Leaving iwfm_read_rz()")

    return RootzoneFiles(
        np_file=np_file,
        p_file=p_file,
        ur_file=ur_file,
        nr_file=nr_file,
        rf_file=rf_file,
        ru_file=ru_file,
        ir_file=ir_file,
    )
