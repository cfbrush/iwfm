# latlon_2_utm.py
# Reproject from geographic coordinates to UTM
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


def latlon_2_utm(lat, lon):
    ''' latlon_2_utm() - Reproject from geographic coordinates to UTM
        
    
    Parameters
    ----------
    lat : float
        latitude in decimal degrees

    lon : float
        longitude in decimal degrees

    Returns
    -------
    UTM coordinates: X, Y, Zone Number, Zone Letter

    '''
    import numpy as np
    from pyproj import Transformer
    from iwfm.gis.get_utm_zone import get_utm_zone

    scalar = np.asarray(lat).ndim == 0
    lat_a = np.atleast_1d(np.asarray(lat, dtype=float))
    lon_a = np.atleast_1d(np.asarray(lon, dtype=float))

    # zone and hemisphere from the first point; all points share one zone
    zone = get_utm_zone(lon_a[0])
    epsg = (32700 if lat_a[0] < 0 else 32600) + zone
    x, y = Transformer.from_crs(4326, epsg, always_xy=True).transform(lon_a, lat_a)

    # MGRS latitude band letter: 8-degree bands C..X from 80S to 84N
    bands = 'CDEFGHJKLMNPQRSTUVWX'
    letter = bands[min(max(int((lat_a[0] + 80) // 8), 0), len(bands) - 1)]

    if scalar:
        return float(x[0]), float(y[0]), zone, letter
    return x, y, zone, letter


if __name__ == '__main__':
    ''' Run latlon_2_utm() from command line 
        File format: ID, Latitude, Longitude
    '''
    import sys
    import csv
    import iwfm.debug as idb
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        infile  = sys.argv[1]
        outfile = sys.argv[2]
    else:  # ask for file names from terminal
        infile  = input('Input lat-lon file name: ')
        outfile = input('Output UTM file name: ')

    iwfm.file_test(infile)

    idb.exe_time()  # initialize timer

    # read lat-lon file using csv.reader
    filelines = []
    with open(infile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            filelines.append(row)

    # remove header line
    if not filelines:
        print(f'  Error: {infile} is empty or contains only a header line')
        sys.exit(1)
    header = filelines.pop(0)

    # convert first column to string array and assign to id
    try:
        id = [line[0] for line in filelines]
    except IndexError as e:
        print(f'  Error: {infile} has incomplete rows. Expected format: "ID, Latitude, Longitude" with header line')
        print(f'  Details: {e}')
        sys.exit(1)

    # convert second and third columns to float and assign to lat lon
    try:
        for i in range(len(filelines)):
            filelines[i][1] = float(filelines[i][1])
            filelines[i][2] = float(filelines[i][2])
    except IndexError as e:
        print(f'  Error: {infile} row {i+2} is missing columns. Expected format: "ID, Latitude, Longitude"')
        print(f'  Details: {e}')
        sys.exit(1)
    except ValueError as e:
        print(f'  Error: {infile} row {i+2} has invalid numeric values for Latitude or Longitude')
        print(f'  Details: {e}')
        sys.exit(1)

    # convert second column to float array and assign to lat
    lat = [line[1] for line in filelines]

    # convert third column to float array and assign to lon
    lon = [line[2] for line in filelines]

    # convert lat-lon to UTM
    x, y, zone, letter = latlon_2_utm(lat, lon)

    # write UTM file using csv.writer
    with open(outfile, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['ID', 'X', 'Y', 'Zone', 'Letter'])
        for i in range(len(x)):
            writer.writerow([id[i], x[i], y[i], zone, letter])
    
    
    #np.savetxt(outfile, np.column_stack((id, x, y, zone, letter)), fmt='%d %f %f %d %s')
    
    print(f'  Wrote {len(x)} coordinates to {outfile}.')
    idb.exe_time()  # print elapsed time
