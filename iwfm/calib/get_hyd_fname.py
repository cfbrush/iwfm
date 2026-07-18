# get_hyd_fname.py
# Get hydrograph file name from IWFM file
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


def get_hyd_fname(ftype,file_dict,debug=0):
    '''Return the hydrograph file name.

    Parameters
    ----------
    ftype : str
        IWFM input file type

    file_dict : dictionary
        information for ftypes

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    hyd_file : str
        hydrograph file name
    '''
    import iwfm.calib as calib

    hyd_file, hyd_names = calib.get_hyd_info(ftype,file_dict)

    return hyd_file
