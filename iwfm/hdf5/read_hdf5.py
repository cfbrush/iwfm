# read_hdf5.py 
# read an hdf5 file
# Copyright (C) 2018-2023 University of California
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

'''Read an HDF5 file.'''

def read_hdf5(filename, verbose=False):
    '''Read an HDF5 file.

    Parameters
    ----------
    filename : str
        name of hdf5 file


    Returns
    -------
    f : h5py.File
        Open in read mode. The caller is responsible for closing it
        (``f.close()`` or use as a context manager).
    '''
    import h5py
    import iwfm

    iwfm.file_test(filename)

    f = h5py.File(filename)

    if verbose:
        print(f'  Opened {filename}')

    return f
