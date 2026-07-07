# elem2shp.py
# Create elements shapefile for an IWFM model
# Copyright (C) 2020-2025 University of California
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


def elem2shp(elem_ids, elem_nodes, node_coord_dict, elem_sub, lakes, shape_name,
             epsg=26910, verbose=False):
    ''' elem2shp() - Creates an IWFM element shapefile 

    Parameters
    ----------
    elem_ids : list
        list of element id numbers
    
    elem_nodes : list
        list of elements and associated nodes

    node_coord_dict : dictionary
        key = node_id, values = associated X and Y coordinates
    
    elem_sub : list
        list of elements and associated subregions
    
    lakes : list
        list of lakes and associated elements
    
    shape_name : str
         output shapefiles base name
    
    epsg : int, default=26910 (NAD 83 UTM 10N, CA)
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

    shapename = f'{shape_name}_Elements.shp'

    # Create list of element polygons
    polygons = iwfm.elem_poly_coords(elem_nodes, node_coord_dict)

    # Create a new shapefile writer
    w = shapefile.Writer(shapename, shapeType=shapefile.POLYGON)
    
    # Define fields
    w.field('elem_id', 'N', 10, 0)
    w.field('subregion', 'N', 10, 0)
    w.field('lake_no', 'N', 10, 0)
    
    # Write features
    for i in range(len(polygons)):
        poly = polygons[i]  # Already in the correct format for PyShp
        lake_no = 0
        if lakes:
            for j in range(len(lakes)):
                if lakes[j][1] == i + 1:  # lake on this element
                    lake_no = lakes[j][0]
        
        # Add geometry and attributes
        w.poly([poly])
        w.record(elem_id=elem_ids[i], subregion=elem_sub[i], lake_no=lake_no)
    
    # Create .prj file for spatial reference
    with open(f"{shapename[:-4]}.prj", "w", encoding='utf-8') as prj:
        epsg = pyproj.CRS.from_epsg(epsg)
        prj.write(epsg.to_wkt())
    
    # Save and close the shapefile
    w.close()

    if verbose:
        print(f'  Wrote shapefile {shapename}')
