# iwfm_read_rz_npc.py
# Read non-ponded crop data from a file and organize them into lists
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



def iwfm_read_rz_npc(file, verbose=False):
    """iwfm_read_rz_npc() - Read non-ponded crop data from a file and organize them into lists.

    Parameters
    ----------
    file : str
        The path of the file containing the non-ponded crop data.

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------

    crops : list
        A list of crop codes

    params : list
        A list of parameters: [cn, et, wsp, ip, ms, ts, rf, ru, ic]

    files : list
        A list of file names: [npc_area_file, npc_bd_file, npc_zb_file, npc_rd_file, npc_ms_file, npc_ts_file, npc_md_file]

    """
    import iwfm
    from iwfm.file_utils import read_next_line_value

    if verbose: print(f"Entered iwfm_read_rz_npc() with {file}")

    iwfm.file_test(file)
    with open(file, encoding='utf-8') as f:
        npc_lines = f.read().splitlines()                           # open and read input file

    ncrop, line_index = read_next_line_value(npc_lines, -1)         # number of crop types
    ncrop = int(ncrop)

    fldmd, line_index = read_next_line_value(npc_lines, line_index) # soil moisture computation method flag
    fldmd = int(fldmd)

    # read crop codes
    crops = []
    for i in range(ncrop):
        crop, line_index = read_next_line_value(npc_lines, line_index)
        crops.append(crop)

    npc_area_file, line_index = read_next_line_value(npc_lines, line_index)

    nbcrop, line_index = read_next_line_value(npc_lines, line_index)
    nbcrop = int(nbcrop)

    npc_bd_file, line_index = read_next_line_value(npc_lines, line_index, skip_lines=nbcrop)  # crop budget file name

    npc_zb_file, line_index = read_next_line_value(npc_lines, line_index, skip_lines=nbcrop)  # crop zbudget fractions file name

    npc_rd_file, line_index = read_next_line_value(npc_lines, line_index)   # rooting depth fractions file name

    fact, line_index = read_next_line_value(npc_lines, line_index)
    fact = float(fact)

    # read rooting depths
    rd = []
    for i in range(ncrop):
        _, line_index = read_next_line_value(npc_lines, line_index)
        parts = npc_lines[line_index].split()
        rd.append([int(parts[0]), float(parts[1]), int(parts[2])])

    # how many elements?
    _, line_index = read_next_line_value(npc_lines, line_index)
    ne = 0
    while (line_index + ne < len(npc_lines) and
           npc_lines[line_index+(ne)].split()[0] != 'C'):
        ne += 1

    if line_index + ne >= len(npc_lines):
        raise ValueError(
            f"'C' marker not found while counting non-ponded crop elements at line {line_index}"
        )

    ne -= 2                                             # one to convert to zero index, one is extra

    # curve numbers
    cn, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    _, line_index = read_next_line_value(npc_lines, line_index)

    # ET
    et, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    _, line_index = read_next_line_value(npc_lines, line_index)

    # ag water supply requirement
    wsp, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    _, line_index = read_next_line_value(npc_lines, line_index)

    # irrigation period
    ip, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    npc_ms_file, line_index = read_next_line_value(npc_lines, line_index)   # minimum soil moisture file name
    _, line_index = read_next_line_value(npc_lines, line_index)             # skip to ms data

    ms, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    npc_ts_file, line_index = read_next_line_value(npc_lines, line_index)   # target soil moisture file name
    _, line_index = read_next_line_value(npc_lines, line_index)             # skip to tsm data

    tsm, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    _, line_index = read_next_line_value(npc_lines, line_index)

    # return flow fractions
    rf, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    _, line_index = read_next_line_value(npc_lines, line_index)

    # reuse fractions
    ru, line_index = iwfm.iwfm_read_param_table_ints(npc_lines, line_index, ne)
    npc_md_file, line_index = read_next_line_value(npc_lines, line_index)   # minimum deep perc file name
    _, line_index = read_next_line_value(npc_lines, line_index)             # skip to ic data

    # initial condition
    ic, line_index = iwfm.iwfm_read_param_table_floats(npc_lines, line_index, ne)

    params = [cn, et, wsp, ip, ms, tsm, rf, ru, ic]
    files = [npc_area_file, npc_bd_file, npc_zb_file, npc_rd_file, npc_ms_file, npc_ts_file, npc_md_file]

    if verbose: print(f"Leaving iwfm_read_rz_npc()")

    return crops, params, files
