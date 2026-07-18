# __init__.py for iwfm.gis package
# Classes, methods and functions to read, write and modify gis files for IWFM and IGSM files
# Copyright (C) 2018-2026 University of California
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

# -- general methods --------------------------------------
'''Classes, methods and functions to read, write and modify gis files for IWFM and IGSM files.'''

from iwfm.gis.method_fns import method_fns

# -- iwfm methods -----------------------------------------
from iwfm.gis.iwfm2shp import iwfm2shp
from iwfm.gis.elem2shp import elem2shp
from iwfm.gis.nodes2shp import nodes2shp
from iwfm.gis.snodes2shp import snodes2shp
from iwfm.gis.reach2shp import reach2shp
from iwfm.gis.nodal_values2shp import nodal_values2shp
from iwfm.gis.nodal_multivalues2shp import nodal_multivalues2shp
from iwfm.gis.projection import projection
from iwfm.gis.get_boundary_coords import get_boundary_coords
from iwfm.gis.nodes2shp_csv import nodes2shp_csv
from iwfm.gis.elems2shp_csv import elems2shp_csv


# -- GIS and input files -----------------------------------
from iwfm.gis.map_divs2shp import map_divs2shp
from iwfm.gis.map_rchg2shp import map_rchg2shp
from iwfm.gis.map_lu import map_lu
from iwfm.gis.map_elempump import map_elempump
from iwfm.gis.map_elempump2shp import map_elempump2shp


# --- map parameters to shapefiles -------------------------
from iwfm.gis.map_param2shp_nodes import map_param2shp_nodes
from iwfm.gis.map_param2shp_elems import map_param2shp_elems
from iwfm.gis.map_param2shp_rz import map_param2shp_rz
from iwfm.gis.map_param2shp_rz_npc import map_param2shp_rz_npc
from iwfm.gis.map_param2shp_rz_pc import map_param2shp_rz_pc
from iwfm.gis.map_param2shp_rz_urban import map_param2shp_rz_urban
#from iwfm.gis.map_param2shp_natrip import map_param2shp_rz_natrip


# -- igsm methods -----------------------------------------
from iwfm.gis.igsm2shp import igsm2shp
from iwfm.gis.igsm_elem2shp import igsm_elem2shp
from iwfm.gis.elem2boundingpoly import elem2boundingpoly

# -- KML methods ------------------------------------------
from iwfm.gis.kml_points import kml_points

# -- XML methods ------------------------------------------
from iwfm.gis.xml_tracks import xml_tracks
from iwfm.gis.xml_fix import xml_fix

# -- QGIS methods -----------------------------------------
# QGIS is an optional dependency - only import if available
try:
    from iwfm.gis.qgis_init import qgis_init
    from iwfm.gis.qgis_init_paths import qgis_init_paths
    from iwfm.gis.qgis_open_proj import qgis_open_proj
    from iwfm.gis.qgis_layer_names import qgis_layer_names
    from iwfm.gis.qgis_print_geometry import qgis_print_geometry
    from iwfm.gis.qgis_save_project import qgis_save_project
except ImportError:
    # QGIS not available - these functions won't be accessible
    pass

# -- shapefile methods ------------------------------------
from iwfm.gis.shp_get import shp_get
from iwfm.gis.shp_get_PyShp import shp_get_PyShp
from iwfm.gis.shp_type import shp_type
from iwfm.gis.shp_type_txt import shp_type_txt
from iwfm.gis.shp_area import shp_area
from iwfm.gis.shp_bounds import shp_bounds
from iwfm.gis.shp_norec import shp_norec
from iwfm.gis.shp_fields import shp_fields
from iwfm.gis.shp_fields_print import shp_fields_print
from iwfm.gis.shp_getrec import shp_getrec
from iwfm.gis.shp_getrec_lg import shp_getrec_lg
from iwfm.gis.shp_getrow import shp_getrow
from iwfm.gis.shp_getrow_lg import shp_getrow_lg
from iwfm.gis.shp_getcol import shp_getcol
from iwfm.gis.shp_getcol_lg import shp_getcol_lg
from iwfm.gis.shp_fieldnames import shp_fieldnames
from iwfm.gis.shp_getrec_fn import shp_getrec_fn
from iwfm.gis.shp_geomtype import shp_geomtype

from iwfm.gis.shp_get_OGR import shp_get_OGR

from iwfm.gis.shp_driver_type import shp_driver_type
from iwfm.gis.shp_crs import shp_crs

# -- editing shapefiles -----------------------------------
from iwfm.gis.shp_add_field import shp_add_field
from iwfm.gis.shp_to_utm_pts import shp_to_utm_pts
from iwfm.gis.make_prj import make_prj
from iwfm.gis.shp_get_writer import shp_get_writer

# -- raster methods ---------------------------------------
from iwfm.gis.raster_open import raster_open
from iwfm.gis.raster_band2jpeg import raster_band2jpeg
from iwfm.gis.shp2png import shp2png
from iwfm.gis.shp2png_empty import shp2png_empty
from iwfm.gis.shp2png_poly import shp2png_poly

# -- GeoPandas methods ------------------------------------
from iwfm.gis.geop_open import geop_open
from iwfm.gis.geop_plot import geop_plot
from iwfm.gis.geop_saveplot import geop_saveplot

# -- PyMySQL methods --------------------------------------
from iwfm.gis.mysql_create import mysql_create
from iwfm.gis.mysql_conn import mysql_conn
from iwfm.gis.mysql_new_table import mysql_new_table
from iwfm.gis.mysql_commit import mysql_commit
from iwfm.gis.mysql_read import mysql_read
from iwfm.gis.mysql_insert_record import mysql_insert_record

# -- GeoPDF methods ---------------------------------------
from iwfm.gis.geopdf_create import geopdf_create
from iwfm.gis.geopdf_draw_rect_ex import geopdf_draw_rect_ex

# -- OSMnx methods ----------------------------------------
# Open Street Map + NetworkX
from iwfm.gis.osmnx_getData import osmnx_getData
from iwfm.gis.osmnx_street_len import osmnx_street_len

# -- projections ------------------------------------------
from iwfm.gis.distance_sphere import distance_sphere
from iwfm.gis.distance_ellipse import distance_ellipse
from iwfm.gis.bearing import bearing
from iwfm.gis.shp_epsg import shp_epsg
from iwfm.gis.getWKT_prj import getWKT_prj
from iwfm.gis.shp_reproject import shp_reproject
from iwfm.gis.dd2dms import dd2dms
from iwfm.gis.dms2dd import dms2dd

# -- coordinate conversion --------------------------------
from iwfm.gis.utm_2_latlon import utm_2_latlon
from iwfm.gis.latlon_2_utm import latlon_2_utm
from iwfm.gis.utm_2_wgs84 import utm_2_wgs84
from iwfm.gis.wgs84_2_utm import wgs84_2_utm
from iwfm.gis.get_utm_zone import get_utm_zone
from iwfm.gis.is_northern import is_northern

# -- Geocoding --------------------------------------------
from iwfm.gis.geocode import geocode
from iwfm.gis.geocode_json import geocode_json
from iwfm.gis.geocode_wkt import geocode_wkt
from iwfm.gis.geocode_ex import geocode_ex
from iwfm.gis.geocode_mp import geocode_mp

# -- WKT methods ------------------------------------------
from iwfm.gis.shp2wkt import shp2wkt
from iwfm.gis.wk2_getBoundingBox import wk2_getBoundingBox
from iwfm.gis.wkt2poly import wkt2poly

# -- json and geojson methods -----------------------------
from iwfm.gis.json_read import json_read
from iwfm.gis.point2geojson import point2geojson
from iwfm.gis.geojson2shp import geojson2shp

# -- visualizing shapefiles -------------------------------
from iwfm.gis.point_in_poly import point_in_poly
from iwfm.gis.world2screen import world2screen
from iwfm.gis.world2pixel import world2pixel
from iwfm.gis.image2Array import image2Array
from iwfm.gis.density_plot import density_plot
from iwfm.gis.choropleth import choropleth
from iwfm.gis.heatmap import heatmap

# -- spreadsheets -----------------------------------------
from iwfm.gis.wks2shp_pt import wks2shp_pt

# -- GPS Data ---------------------------------------------
from iwfm.gis.nmea_parse import nmea_parse

# -- remote sensing ---------------------------------------
from iwfm.gis.img_swap_bands import img_swap_bands
from iwfm.gis.histogram_array import histogram_array
from iwfm.gis.histogram_draw import histogram_draw
from iwfm.gis.histogram import histogram
from iwfm.gis.stretch import stretch
from iwfm.gis.img_stretch import img_stretch
from iwfm.gis.img_2_array import img_2_array
from iwfm.gis.img_clip import img_clip
from iwfm.gis.img_classify import img_classify
from iwfm.gis.img_threshold import img_threshold
from iwfm.gis.img_extract import img_extract
from iwfm.gis.img_diff import img_diff

# -- Elevation data ---------------------------------------
from iwfm.gis.grid_read import grid_read
from iwfm.gis.grid_write import grid_write
from iwfm.gis.grid_shadedrelief import grid_shadedrelief
from iwfm.gis.grid_contour import grid_contour
from iwfm.gis.contour2png import contour2png
from iwfm.gis.grid2img import grid2img
from iwfm.gis.grid_colorize import grid_colorize
from iwfm.gis.hillshade import hillshade

# -- lidar data -------------------------------------------
from iwfm.gis.las2dem import las2dem
from iwfm.gis.las2shp import las2shp
