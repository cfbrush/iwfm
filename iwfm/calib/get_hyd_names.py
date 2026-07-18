# get_hyd_names.py
# Get hydrograph names from IWFM input file
# Copyright (C) 2020-2023 University of California
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


'''Get hydrograph names from IWFM input file.'''

def get_hyd_names(ftype,file_dict,verbose=False):
    '''Return hydrograph names.

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
    hyd_names : list
        hydrograph names
    '''
    import iwfm.calib as calib

    if verbose: print(f'\n  Reading {ftype} Main File {file_dict[ftype][0]}')

    hyd_file, hyd_names = calib.get_hyd_info(ftype,file_dict)

    if verbose: print(f'    Read {len(hyd_names)} {ftype.lower()} hydrograph locations')

    return hyd_names
