# shp_to_utm_pts.py
# Reproject a shapefile to UTM with PyShp
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


'''Reproject a shapefile to UTM with PyShp.'''

def shp_to_utm_pts(shape, outfile, verbose=False):
    '''Reproject a point shapefile to UTM.

    Parameters
    ----------
    shape : PyShp point shapefile

    outfile : str
        output point shapefile name

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    tracks : list
        tracking points
    '''
    import shapefile  # PyShp
    from pyproj import CRS
    from iwfm.gis.latlon_2_utm import latlon_2_utm

    zone = 0

    with shapefile.Writer(outfile, shapeType=shape.shapeType) as w:
        w.fields = shape.fields[1:]  # skip Deletion field
        for s in shape.iterShapeRecords():
            w.record(*s.record)
        for s in shape.iterShapes():  # this reprojects
            lon, lat = s.points[0]
            x, y, zone, band = latlon_2_utm(lat, lon)
            w.point(x, y)

    # the zone variable will tell which UTM zone this shapefile is in
    # (WGS84 UTM north = EPSG 326xx, matching the transform above)
    wkt = CRS.from_epsg(32600 + zone).to_wkt(version='WKT1_ESRI')

    with open(f'{outfile}.prj', 'w', encoding='utf-8') as f:
        f.write(wkt)

    if verbose:
        print(f'  Wrote {outfile}, UTM Zone: {zone}')
    return
