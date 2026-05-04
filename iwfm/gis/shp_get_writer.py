# shp_get_writer.py
# Get a writer for a shapefile of the same type as the input shapefile
# Copyright (C) 2020-2021 University of California
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


def shp_get_writer(outfile, type):
    ''' shp_get_writer() - Get a writer for a shapefile of the same type
        as the input shapefile

    Parameters
    ----------
    outfile : str
        ouput shapefile name
    
    type : str
        shapefile type

    Returns
    -------
    w : shapefile.Writer
        The caller MUST call ``w.close()`` (or use it as a context
        manager) for the shapefile to be flushed to disk.

    '''
    import shapefile  # PyShp

    return shapefile.Writer(outfile, shapeType=type)
