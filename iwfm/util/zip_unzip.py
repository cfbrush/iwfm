# zip_unzip.py
# unzip a zip file
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


'''Unzip a zip file.'''

def zip_unzip(filename, verbose=False):
    '''Unzip a zipfile.

    Parameters
    ----------
    filename : str
        Zip file

    verbose : bool, default=False
        True = command-line output on

    Return
    ------
    nothing
    '''
    import zipfile

    with open(filename, 'rb') as zip:
        zipList = zipfile.ZipFile(zip)
        for name in zipList.namelist():
            # Skip directories (they end with '/')
            if name.endswith('/'):
                continue
            with open(name, 'wb') as out:
                out.write(zipList.read(name))
    if verbose:
        print(f'  Unzipped \'{filename}\' ') 

