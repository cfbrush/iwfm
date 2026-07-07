# hyd_dict.py
# Read Groundwater.dat file and return dictionary of well info
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


def hyd_dict(gwhyd_info_file):
    ''' hyd_dict() - Read hydrograph info from Groundwater.dat file and build
        a dictionary of groundwater hydrograph info

    Parameters
    ----------
    gwhyd_info_file : str
        IWFM Groundwaer.dat file name

    Returns
    -------
    well_dict : dictionary
        key = well name (i.e. state well ID), value = WellInfo instance

    '''
    import iwfm
    from iwfm.file_utils import read_next_line_value
    from iwfm.iwfm_dataclasses import WellInfo

    well_dict = {}
    iwfm.file_test(gwhyd_info_file)
    with open(gwhyd_info_file, encoding='utf-8') as f:
        gwhyd_info = f.read().splitlines()  # open and read input file

    # skip to NOUTH, number of hydrographs (skip 20 non-comment lines after start)
    nouth_str, line_index = read_next_line_value(gwhyd_info, 0, column=0, skip_lines=20)
    nouth = int(nouth_str)

    # skip to first hydrograph (skip 3 lines: NOUTH, FACTXY, GWHYDOUTFL)
    _, line_index = read_next_line_value(gwhyd_info, line_index, column=0, skip_lines=2)

    for _ in range(nouth):
        line = gwhyd_info[line_index].split()

        # Handle both HYDTYP formats:
        # HYDTYP=0 (X-Y coordinates): 6 fields [ID, HYDTYP, LAYER, X, Y, NAME]
        # HYDTYP=1 (node number): 5 fields [ID, HYDTYP, LAYER, NODE, NAME]
        if len(line) >= 6:
            # HYDTYP=0 format with X-Y coordinates
            well_name = line[5].lower()
            well_dict[well_name] = WellInfo(
                column=int(line[0]),
                x=float(line[3]),
                y=float(line[4]),
                layer=int(line[2]),
                name=well_name,
            )
        else:
            # HYDTYP=1 format with node number
            well_name = line[4].lower()
            well_dict[well_name] = WellInfo(
                column=int(line[0]),
                x=0.0,
                y=0.0,
                layer=int(line[2]),
                name=well_name,
            )

        line_index += 1
    return well_dict
