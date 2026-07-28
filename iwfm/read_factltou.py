# read_factltou.py
# Read the FACTLTOU head-output scale factor from an IWFM groundwater file
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


'''Read the FACTLTOU head-output scale factor from an IWFM groundwater file.'''

def read_factltou(gw_file):
    '''Read the FACTLTOU head-output scale factor from an IWFM groundwater file.

    IWFM multiplies simulated groundwater heads by FACTLTOU before printing
    them to the hydrograph output file. A model calibrated with FACTLTOU > 1
    (to preserve more significant digits through the fixed-decimal print
    format) writes scaled heads, so readers of the hydrograph file must
    divide by this factor to recover heads in model units.

    Parameters
    ----------
    gw_file : str
        IWFM groundwater main file name

    Returns
    -------
    factltou : float
        FACTLTOU value, or 1.0 if the file cannot be read or has no
        non-comment FACTLTOU line
    '''
    try:
        for line in open(gw_file, encoding='latin-1', errors='ignore'):
            if 'FACTLTOU' in line and not line.lstrip().startswith('C'):
                return float(line.split()[0])
    except Exception:
        pass
    return 1.0
