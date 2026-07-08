# iwfm_read_rz_pc.py
# Read ponded crop data from a file and organize them into lists
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


def iwfm_read_rz_pc(file, verbose=False):
    """iwfm_read_rz_pc() - Read ponded crop data from a file and organize them into lists.

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
        A list of parameters: [cn, et, wsp, ip, pd, ad, rf, ru, ic]

    files : list
        A list of file names: [pc_area_file, pc_bd_file, pc_zb_file, pc_rd_file, pc_ms_file, pc_ts_file, pc_md_file]

    """
    import iwfm
    from iwfm.file_utils import read_next_line_value

    npcrops = 5                                                 # number of ponded crop types (may be variable in future IWFM versions)

    if verbose: print(f"Entered iwfm_read_rz_pc() with {file}")

    iwfm.file_test(file)
    with open(file, encoding='utf-8') as f:
        pc_lines = f.read().splitlines()                   # open and read input file

    pc_area_file, line_index = read_next_line_value(pc_lines, -1)

    nbcrop, line_index = read_next_line_value(pc_lines, line_index)
    nbcrop = int(nbcrop)                                        # number of crop-specific budget files to produce

    budfiles = []
    for i in range(nbcrop):
        budfile, line_index = read_next_line_value(pc_lines, line_index)
        budfiles.append(budfile)                                # read budget file names

    pc_bd_file, line_index = read_next_line_value(pc_lines, line_index, skip_lines=nbcrop)  # read crop budget file name

    pc_zb_file, line_index = read_next_line_value(pc_lines, line_index, skip_lines=nbcrop)  # read crop zbudget fractions file name

    fact, line_index = read_next_line_value(pc_lines, line_index)
    fact = float(fact)                                          # root zone depth conversion factor
    rzdepths = []
    for i in range(npcrops):
        rzdepth, line_index = read_next_line_value(pc_lines, line_index)
        rzdepths.append(float(rzdepth) * fact)                  # read root zone depths

    # how many elements?
    _, line_index = read_next_line_value(pc_lines, line_index)
    ne = 0
    while (line_index + ne < len(pc_lines) and
           pc_lines[line_index+(ne)].split()[0] != 'C'):
        ne += 1

    if line_index + ne >= len(pc_lines):
        raise ValueError(
            f"'C' marker not found while counting ponded crop elements at line {line_index}"
        )

    ne -= 1                                                             # one to convert to zero index

    # curve numbers
    cn, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)
    _, line_index = read_next_line_value(pc_lines, line_index)

    # ET
    et, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)
    _, line_index = read_next_line_value(pc_lines, line_index)

    # ag water supply requirement
    wsp, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)
    _, line_index = read_next_line_value(pc_lines, line_index)

    # irrigation period
    ip, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)
    _, line_index = read_next_line_value(pc_lines, line_index)

    # rice and refuge operations input files
    pc_pd_file, line_index = read_next_line_value(pc_lines, line_index)  # read ponding depths file name

    pc_po_file, line_index = read_next_line_value(pc_lines, line_index)  # read ponding operations file name

    pd, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)    # read ponding depth column numbers
    _, line_index = read_next_line_value(pc_lines, line_index)

    ad, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)    # read application depth column numbers
    _, line_index = read_next_line_value(pc_lines, line_index)

    rf, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)    # read return flow depth column numbers
    _, line_index = read_next_line_value(pc_lines, line_index)

    ru, line_index = iwfm.iwfm_read_param_table_ints(pc_lines, line_index, ne)    # read reuse flow depth column numbers
    _, line_index = read_next_line_value(pc_lines, line_index)

    # initial condition
    ic, line_index = iwfm.iwfm_read_param_table_floats(pc_lines, line_index, ne)

    crops = ['ri_n', 'ri_f', 'ri_d', 'rf_sl', 'rf_pr']
    params = [cn, et, wsp, ip, pd, ad, rf, ru, ic]
    files = [pc_area_file, pc_bd_file, pc_zb_file, pc_pd_file, pc_po_file]

    if verbose: print("Leaving iwfm_read_rz_pc()")

    return crops, params, files
