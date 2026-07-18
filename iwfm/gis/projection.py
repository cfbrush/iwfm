# projection.py
# Create .PRJ files for shapefiles
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


'''Create .PRJ files for shapefiles.'''

def projection(shapename, epsg=26910, verbose=False):
    '''Create projection files for shapefiles.

    Parameters
    ----------
    shapename : str
        name of shapefile
    epsg : int, default=26910 (NAD 83 UTM 10, CA)
        EPSG projection

    Returns
    -------
    nothing
    '''

    # -- NAD 83 UTM 10, CA ---------------------------------------------------
    if epsg == 26910:
        prj ='PROJCS["NAD_1983_UTM_Zone_10N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-123.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

    # -- NAD 83 State Plane California V FIPS 0405 Feet -----------------------
    elif epsg == 102645:
        prj ='PROJCS["NAD_1983_CORS96_StatePlane_California_V_FIPS_0405_Ft_US",GEOGCS["GCS_NAD_1983_CORS96",DATUM["D_NAD_1983_CORS96",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",6561666.66666667],PARAMETER["False_Northing",1640416.66666667],PARAMETER["Central_Meridian",-118.0],PARAMETER["Standard_Parallel_1",34.0333333333333],PARAMETER["Standard_Parallel_2",35.4666666666667],PARAMETER["Latitude_Of_Origin",33.5],UNIT["US survey foot",0.304800609601219]]'


    else:   # default epsg == 26910
        prj ='PROJCS["NAD_1983_UTM_Zone_10N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-123.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

    # -- write projection file ------------------------------------------------
    prjname = f'{shapename}.prj'
    with open(prjname, 'w', encoding='utf-8') as prjfile:
        prjfile.write(prj)

    if verbose:
        print(f'  Projection file {prjname} written')
