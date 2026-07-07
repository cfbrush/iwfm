# nmea_parse.py
# Reads a GIS waypoint file and writes lat-lon values
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

# NMEA sentence types carrying a position, and the 0-based field index
# of the latitude value (longitude value is two fields later)
_NMEA_LAT_FIELD = {'GGA': 2, 'RMC': 3, 'GLL': 1}


def nmea_parse(infile):
    ''' nmea_parse() - Read a GIS waypoint file and write lat-lon values

    Parameters
    ----------
    infile : str
        waypoint file name (NMEA 0183 sentences)

    Returns
    -------
    nothing

    '''
    with open(infile, encoding='ascii', errors='replace') as nmea_file:
        for line in nmea_file:
            line = line.strip()
            if not line.startswith('$') or ',' not in line:
                continue
            fields = line.split('*')[0].split(',')
            sentence = fields[0][-3:]  # e.g. $GPGGA -> GGA
            idx = _NMEA_LAT_FIELD.get(sentence)
            if idx is None or len(fields) <= idx + 3:
                continue
            lat, lat_dir = fields[idx], fields[idx + 1]
            lon, lon_dir = fields[idx + 2], fields[idx + 3]
            if lat and lon:
                print(f'    Lat/Lon: ({lat} {lat_dir}, {lon} {lon_dir})')
    return
