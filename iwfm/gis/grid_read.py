# grid_read.py
# Reads an ASCII Grid file
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


'''Read an ASCII Grid file.'''

def grid_read(infile):
    '''Read an ASCII Grid file.

    Parameters
    ----------
    infile : str
        ASCII Grid file name

    Returns
    -------
    header : str
        information about ASCII Grid array

    myArray : ASCII Grid array
    '''
    import numpy as np
    from iwfm.debug.logger_setup import logger

    skiprows = 6
    header = ''
    try:
        with open(infile, 'r', encoding='utf-8') as f:
            for _ in range(skiprows):
                header += f.readline()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f'Failed to read header from grid file {infile}: {e}')
        raise

    try:
        myArray = np.loadtxt(infile, skiprows=skiprows)
    except (ValueError, OSError) as e:
        logger.error(f'Failed to load grid data from {infile}: {e}')
        raise

    logger.debug(f'Read grid file {infile}, array shape {myArray.shape}')
    return header, myArray
