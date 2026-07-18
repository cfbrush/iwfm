# make_prj.py
# Make PRJ file <filename>.prj for epsg cose <epsg_code>
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


'''Make PRJ file <filename>.prj for epsg cose <epsg_code>.'''

def make_prj(filename, epsg_code):
    '''Make projection file <filename>.prj for epsg code <epsg_code>.

    Parameters
    ----------
    filename : str
        input file name

    epsg_code : int
        EPSG code for projection

    Returns
    -------
    nothing
    '''
    from urllib.request import urlopen

    if filename[-4:] != ".prj":
        filename = f"{filename}.prj"
    prj = urlopen(f'http://spatialreference.org/ref/epsg/{epsg_code}/prettywkt/')
    with open(filename, "w", encoding='utf-8') as f:
        f.write(str(prj.read()))
    return
