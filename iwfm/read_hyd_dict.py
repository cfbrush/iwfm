# read_hyd_dict.py
# R Read hydrograph info from Groundwater.dat file and build a dictionary of 
# groundwater hydrograph info
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


'''R Read hydrograph info from Groundwater.dat file and build a dictionary of groundwater hydrograph info.'''

from iwfm.debug.logger_setup import logger


def read_hyd_dict(gw_dat_file, verbose=False):
    '''Read hydrograph info from Groundwater.dat file and build a dictionary of groundwater hydrograph info.

    Parameters
    ----------
    gw_dat_file : str
        IWFM Groundwater.dat file name

    verbose : bool, default = False
        If True, print status messages.

    Returns
    -------
    well_dict : dictionary
        key = well name (i.e. state well ID), value = WellInfo instance
    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import WellInfo

    logger.debug(f"Entered read_hyd_dict() with {gw_dat_file}")

    well_dict = {}
    iwfm.file_test(gw_dat_file)
    with open(gw_dat_file, encoding='utf-8') as f:
        gwhyd_info = f.read().splitlines()  # open and read input file

    # skip to NOUTH, number of hydrographs (skip 20 non-comment lines after start)
    nouth_str, line_index = read_next_line_value(gwhyd_info, 0, skip_lines=20)
    nouth = int(nouth_str)

    # skip to first hydrograph (skip 3 lines: NOUTH, FACTXY, GWHYDOUTFL)
    _, line_index = read_next_line_value(gwhyd_info, line_index, skip_lines=2)

    for i in range(0, nouth):
        line = gwhyd_info[line_index].split()
        key = line[5]                  # well name = key
        well_dict[key] = WellInfo(
            column=int(line[0]),
            x=float(line[3]),
            y=float(line[4]),
            layer=int(line[2]),
            name=line[5].lower(),
        )
        line_index += 1

    logger.debug("Leaving read_hyd_dict()")

    return well_dict
