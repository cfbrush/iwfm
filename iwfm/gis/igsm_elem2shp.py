# igsm_elem2shp.py
# Create an elements shapefile for an IGSM model
# Copyright (C) 2020-2024 University of California
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


'''Create an elements shapefile for an IGSM model.'''

def igsm_elem2shp(elem_nodes,node_coords,elem_char,lake_elems,shape_name,
    epsg=26910,verbose=False):
    '''Create an elements shapefile for an IGSM model.

    Parameters
    ----------
    elem_nodes : list
        list of elements and associated nodes

    node_coords : list
        list of nodes and associated X and Y coordinates

    elem_sub : list
        list of elements and associated subregions

    lake_elems : list
        list of lakes and associated elements

    shape_name : str
        output shapefiles base name

    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    verbose : bool, default=False
        True = command-line output on

    Returns
    -------
    nothing
    '''
    import shapefile
    import pyproj

    import iwfm

    elem_shapename = f'{shape_name}_Elements'  # remove .shp extension

    polygons = iwfm.elem_poly_coords(elem_nodes, node_coords)

    # Create a new shapefile writer object
    w = shapefile.Writer(elem_shapename, shapeType=shapefile.POLYGON)
    
    # Define fields
    w.field('elem_id', 'N', 10, 0)      # Integer
    w.field('raingage', 'N', 10, 0)     # Integer
    w.field('rainfactor', 'F', 6, 3)    # Float with 3 decimals
    w.field('drainnode', 'N', 10, 0)    # Integer
    w.field('subregion', 'N', 10, 0)    # Integer
    w.field('soiltype', 'F', 4, 2)      # Float with 2 decimals
    w.field('lake_no', 'N', 10, 0)      # Integer

    # Write features
    for i in range(len(polygons)):
        lake_no = 0
        for j in range(len(lake_elems)):
            if lake_elems[j][1] == i + 1:  # lake on this element
                lake_no = lake_elems[j][0]
        
        w.poly([polygons[i]])  # Add geometry
        w.record(              # Add attributes
            i + 1,                # elem_id
            elem_char[i][0],      # raingage
            elem_char[i][1],      # rainfactor
            elem_char[i][2],      # drainnode
            elem_char[i][3],      # subregion
            elem_char[i][4],      # soiltype
            lake_no               # lake_no
        )
    
    # Write projection file
    with open(f"{elem_shapename}.prj", "w", encoding='utf-8') as prj:
        epsg = f'EPSG:{epsg}'
        prj.write(pyproj.CRS(epsg).to_wkt())
    
    w.close()
    if verbose:
        print(f'  Wrote shapefile {elem_shapename}.shp')
    return 
