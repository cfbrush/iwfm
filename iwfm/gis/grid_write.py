# grid_write.py
# Writes an ASCII Grid file
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


def grid_write(outfile, array, xllcorner=277750.0, yllcorner=6122250.0, 
    cellsize=1.0, nodata=-9999):
    ''' grid_write() - Write an ASCII Grid file
    
    Parameters
    ----------
    outfile : str
        output ASCII Grid file name
    
    array : ASCII Grid array
    
    xllcorner : float, default=277750.0
        x value of lower left corner
    
    yllcorner : float, default=6122250.0
        y value of lower left corner
     
    cellsize : float, default=1.0
        call dimensions
    
    nodata : int, default=-9999
        value for cells with no data

    Returns
    -------
    nothing
    
    '''
    import numpy as np
    from iwfm.debug.logger_setup import logger

    header =  f'ncols {array.shape[1]}\n'
    header += f'nrows {array.shape[0]}\n'
    header += f'xllcorner {round(xllcorner, 1)}\n'
    header += f'yllcorner {round(yllcorner, 1)}\n'
    header += f'cellsize {round(cellsize, 1)}\n'
    header += f'NODATA_value {nodata}\n'
    try:
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(header)
            np.savetxt(f, array, fmt='%1.2f')
    except (PermissionError, OSError) as e:
        logger.error(f'Failed to write grid file {outfile}: {e}')
        raise
    logger.debug(f'Wrote grid file {outfile}')
    return
