# shp_epsg.py
# Read the projection file of a shapefile and return EPSG value
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


def shp_epsg(filename):
    ''' shp_epsg() - Read the projection file and returns the EPSG value
    
    Parameters
    ----------
    filename : str
        input shapefile name

    Returns
    -------
    EPSG cose : int
    
    '''
    from urllib.parse import urlencode
    from urllib.request import urlopen
    import urllib.error
    import json
    from iwfm.debug.logger_setup import logger

    if filename[-4:] != '.prj':
        filename = f'{filename}.prj'

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            prj_text = f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f'Failed to read projection file {filename}: {e}')
        raise

    q = urlencode({'exact': True, 'error': True, 'mode': 'wkt', 'terms': prj_text})

    try:
        r = urlopen('http://prj2epsg.org/search.json', q.encode())
    except urllib.error.URLError as e:
        logger.error(f'Failed to query prj2epsg.org for {filename}: {e}')
        raise

    try:
        j = json.loads(r.read().decode())
        epsg = int(j['codes'][0]['code'])
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f'Failed to parse EPSG response for {filename}: {e}')
        raise

    logger.debug(f'Determined EPSG {epsg} for {filename}')
    return epsg
