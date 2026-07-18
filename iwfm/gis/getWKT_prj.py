# getWKT_prj.py
# Return a WKT string containing projection information
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


def getWKT_prj(epsg_code, verbose=False):
    '''Return a WKT string containing PRJ info for <epsg_code>.

    Parameters
    ----------
    epsg_code : int
        EPSG code

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    output : str
        File name to save info from url
    '''
    from urllib.request import urlopen

    wkt = urlopen(f'http://spatialreference.org/ref/epsg/{epsg_code:0}/prettywkt/')
    ans = f'{wkt.read()}'         # convert bytecode to string

    output = (ans[1:].replace(' ', '').replace('\n', '').replace('\\', '').replace(',n', ','))

    if verbose:
        print(f'  wkt:   {output}')

    return output
