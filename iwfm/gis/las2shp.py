# las2shp.py
# Convert an LAS LIDAR file to a shapefile
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


'''Convert an LAS LIDAR file to a shapefile by creating a 3D triangle mesh using Delaunay Triangulation.'''

def las2shp(source, target, max_edge_length=3, verbose=0):
    '''Convert an LAS LIDAR file to a shapefile by creating a 3D triangle mesh using Delaunay Triangulation.

    Parameters
    ----------
    source : str
        source LIDAR file name

    target : str
        output shapefile name

    max_edge_length : float, default=3
        maximum edge length for triangles (filters out large triangles
        along convex hull which are common artifacts in Delaunay triangulation)

    verbose : int, default=0
        level of CLI printing (0 = none)

    Returns
    -------
    nothing
    '''
    import math
    import time
    import shapefile  # pyshp
    import numpy as np
    from scipy.spatial import Delaunay
    import laspy

    # class Point:
    #  def __init__(self, x, y):
    #      self.px = x
    #      self.py = y
    #  def x(self):
    #      return self.px
    #  def y(self):
    #      return self.py

    # The triangle array holds tuples of 3 point indices used to retrieve the points.
    triangles = None
    las = laspy.read(source)  # Open LIDAR LAS file
    if verbose:
        print('    - Assembling points...')
    points = np.column_stack((las.x, las.y))
    pts = np.array(points)
    if verbose:
        print(f'        len(points): {len(pts)}')
    # print('  points:\n{}'.format(pts))

    if verbose:
        print('    - Composing triangles...')
    # Delaunay Triangulation
    triangles = Delaunay(pts)  # scipy.spatial.Delaunay
    if verbose:
        print(f'        number of triangles: {len(triangles.simplices)}')
    if verbose:
        print('    - Creating shapefile...')

    # extract the Delaunay triangle coordinates to an np.array
    tri = triangles.simplices
    tris = len(tri)

    if verbose:
        print(f'        len(tri): {len(tri)}')
        print(f'        points:\n{tri}')

    # PolygonZ shapefile (x, y, z, m)
    with shapefile.Writer(target, shapefile.POLYGONZ) as w:
        w.field('X1', 'C', '40')
        w.field('X2', 'C', '40')
        w.field('X3', 'C', '40')
        w.field('Y1', 'C', '40')
        w.field('Y2', 'C', '40')
        w.field('Y3', 'C', '40')
        w.field('Z1', 'C', '40')
        w.field('Z2', 'C', '40')
        w.field('Z3', 'C', '40')

        # Loop through shapes and track progress every 10 percent
        last_percent = 0
        count = 0
        # Check segments for large triangles along the convex hull which is a common
        # artifact in Delaunay triangulation
        for i in range(tris):
            t = tri[i]
            if verbose:
                print(f'        t[{i}]: {t}')
            pct = int((i / (tris * 1.0)) * 100.0)
            if pct % 10.0 == 0 and pct > last_percent:
                last_percent = pct
                if verbose:
                    print(f'        {last_percent} % done - Shape {i}/{tris} at {time.asctime()}')
            x1 = las.x[t[0]]
            y1 = las.y[t[0]]
            z1 = las.z[t[0]]
            if verbose:
                print(f'        x1,y1,z1: {x1},{y1},{z1}')
            x2 = las.x[t[1]]
            y2 = las.y[t[1]]
            z2 = las.z[t[1]]
            if verbose:
                print(f'        x2,y2,z2: {x2},{y2},{z2}')
            x3 = las.x[t[2]]
            y3 = las.y[t[2]]
            z3 = las.z[t[2]]
            if verbose:
                print(f'        x3,y3,z3: {x3},{y3},{z3}')
            if math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) > max_edge_length:
                continue
            if math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2) > max_edge_length:
                continue
            if math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2) > max_edge_length:
                continue
            part = [[x1, y1, z1, 0], [x2, y2, z2, 0], [x3, y3, z3, 0]]
            if verbose:
                print(f'        part: {part}\n')
            w.polyz([part])
            w.record(x1, x2, x3, y1, y2, y3, z1, z2, z3)
            count += 1

    if verbose:
        print('    - Saving shapefile...')
        print('    - las2shp() done.')

    return 
