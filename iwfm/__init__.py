# __init__.py for iwfm package
# Classes and methods to read, write and modify IWFM and IGSM files and
# associated data files
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

# -- dataclass definitions --------------------------------
from iwfm.iwfm_dataclasses import PreprocessorFiles, SimulationFiles, WellInfo
from iwfm.iwfm_dataclasses import RootzoneFiles, GroundwaterFiles

# -- IWFM model class -------------------------------------
from iwfm.iwfm_model import iwfm_model, IWFMModelError
from iwfm.gw_well_lay_elev import gw_well_lay_elev


# -- IWFM model file ---------------------------------------
from iwfm.sim_info import sim_info

# -- IWFM preprocessor files -------------------------------
from iwfm.iwfm_read_preproc import iwfm_read_preproc
from iwfm.iwfm_read_elements import iwfm_read_elements
from iwfm.iwfm_read_nodes import iwfm_read_nodes
from iwfm.iwfm_read_lake import iwfm_read_lake
from iwfm.iwfm_read_streams import iwfm_read_streams
from iwfm.iwfm_read_stream_reaches import iwfm_read_stream_reaches
from iwfm.iwfm_read_strat import iwfm_read_strat
from iwfm.read_elements_csv import read_elements_csv
from iwfm.read_nodes_csv import read_nodes_csv

from iwfm.iwfm_strat_arrays import iwfm_strat_arrays
from iwfm.iwfm_lse import iwfm_lse
from iwfm.iwfm_aquifer_thickness import iwfm_aquifer_thickness
from iwfm.iwfm_aquifer_top import iwfm_aquifer_top
from iwfm.iwfm_aquifer_bottom import iwfm_aquifer_bottom
from iwfm.iwfm_aquitard_thickness import iwfm_aquitard_thickness
from iwfm.iwfm_aquitard_top import iwfm_aquitard_top
from iwfm.iwfm_aquitard_bottom import iwfm_aquitard_bottom
from iwfm.iwfm_boundary_coords import iwfm_boundary_coords

# -- IWFM simulation input files -------------------------------
from iwfm.iwfm_read_et_vals import iwfm_read_et_vals
from iwfm.iwfm_read_precip_vals import iwfm_read_precip_vals
from iwfm.iwfm_read_rz import iwfm_read_rz
from iwfm.iwfm_read_rz_npc import iwfm_read_rz_npc
from iwfm.iwfm_read_rz_pc import iwfm_read_rz_pc
from iwfm.iwfm_read_rz_urban import iwfm_read_rz_urban
from iwfm.iwfm_read_rz_nr import iwfm_read_rz_nr
from iwfm.iwfm_read_uz import iwfm_read_uz
from iwfm.iwfm_read_gw import iwfm_read_gw
from iwfm.iwfm_read_div_areas import iwfm_read_div_areas
from iwfm.iwfm_read_elempump import iwfm_read_elempump

# -- IWFM simulation parameterss -------------------------------
from iwfm.iwfm_read_param_table_ints import iwfm_read_param_table_ints
from iwfm.iwfm_read_param_table_floats import iwfm_read_param_table_floats
from iwfm.iwfm_read_rz_params import iwfm_read_rz_params
from iwfm.iwfm_read_rz_file_names import iwfm_read_rz_file_names
from iwfm.iwfm_read_uz_params import iwfm_read_uz_params
from iwfm.iwfm_read_gw_params import iwfm_read_gw_params

# -- IWFM simulation files --------------------------------
from iwfm.iwfm_read_sim import iwfm_read_sim
from iwfm.simhyds import simhyds
from iwfm.get_gw_params import get_gw_params

# -- IWFM land use methods --------------------------------
from iwfm.iwfm_adj_crops import iwfm_adj_crops
from iwfm.iwfm_lu2sub import iwfm_lu2sub
from iwfm.read_lu_file import read_lu_file
from iwfm.write_lu2file import write_lu2file
from iwfm.lu2tables import lu2tables
from iwfm.lu2csv import lu2csv
from iwfm.refined_lu_factors import refined_lu_factors
from iwfm.iwfm_lu2refined import iwfm_lu2refined
from iwfm.tables2lu import tables2lu

# -- IWFM land use file changes for scenarios -------------
from iwfm.iwfm_lu4scenario import iwfm_lu4scenario
from iwfm.get_change_col import get_change_col
from iwfm.read_lu_change_zones import read_lu_change_zones
from iwfm.read_lu_change_factors import read_lu_change_factors
from iwfm.iwfm_precip_adj import iwfm_precip_adj

# -- igsm file methods ------------------------------------
from iwfm.igsm_read_elements import igsm_read_elements
from iwfm.igsm_read_nodes import igsm_read_nodes
from iwfm.igsm_read_chars import igsm_read_chars
from iwfm.igsm_read_strat import igsm_read_strat
from iwfm.igsm_read_lake import igsm_read_lake
from iwfm.igsm_read_streams import igsm_read_streams

# -- IWFM budget and zbudget files ------------------------
from iwfm.budget_info import budget_info
from iwfm.iwfm_read_bud import iwfm_read_bud
from iwfm.bud2csv import bud2csv
from iwfm.zbudget2csv import zbudget2csv

# -- post-process IWFM results ----------------------------
from iwfm.write_results import write_results
from iwfm.simhyd_obs import simhyd_obs
from iwfm.wdl_meas_stats import wdl_meas_stats
from iwfm.wdl_ts_4_wells import wdl_ts_4_wells
from iwfm.read_hyd_dict import read_hyd_dict
from iwfm.read_sim_hyd import read_sim_hyd
from iwfm.read_sim_hyds import read_sim_hyds

# --- plotting methods --for IWFM output ------------------
from iwfm.read_obs_smp import read_obs_smp
from iwfm.read_sim_wells import read_sim_wells
from iwfm.hyd_diff import hyd_diff
from iwfm.write_smp import write_smp
from iwfm.pdf_combine import pdf_combine
from iwfm.bnds2mask import bnds2mask

# -- post-process headall.out file ------------------------
from iwfm.headall_read import headall_read
from iwfm.headall2csv import headall2csv
from iwfm.headall2dtw import headall2dtw
from iwfm.headall2shp import headall2shp
from iwfm.headall2table import headall2table
from iwfm.headall2ts import headall2ts
from iwfm.headall2surfer import headall2surfer
from iwfm.headall2excel import headall2excel
from iwfm.get_heads_4_date import get_heads_4_date
from iwfm.read_nodes import read_nodes

# -- finite-element methods -------------------------------
from iwfm.elem_poly_coords import elem_poly_coords
from iwfm.elem_poly_coords_wkt import elem_poly_coords_wkt
from iwfm.iwfm_nearest_nodes import iwfm_nearest_nodes
from iwfm.iwfm_nearest_node import iwfm_nearest_node
from iwfm.nearest_node import nearest_node
from iwfm.nearest import nearest
from iwfm.in_element import in_element
from iwfm.get_elem_centroids import get_elem_centroids

# -- text file methods -------------------------------------
from iwfm.write_2_dat import write_2_dat
from iwfm.write_2_csv import write_2_csv
from iwfm.write_2_surfer import write_2_surfer
from iwfm.skip_ahead import skip_ahead
from iwfm.file_utils import read_next_line_value, read_multiple_line_values, read_line_values_to_dict

# -- date and time methods --------------------------------
from iwfm.dss_date import dss_date
from iwfm.index_date import index_date
from iwfm.date_index import date_index
from iwfm.date_util import validate_date_format, safe_parse_date, validate_dss_date_format
from iwfm.Unbuffered import Unbuffered
from iwfm.generate_timesteps import generate_timesteps
from iwfm.generate_datetime_objects import generate_datetime_objects
from iwfm.parse_iwfm_date import parse_iwfm_date

# -- dictionary methods -----------------------------------
from iwfm.file2dict import file2dict
from iwfm.hyd_dict import hyd_dict

# -- DBF methods ------------------------------------------
from iwfm.dbf_open import dbf_open
from iwfm.dbf_print_record import dbf_print_record

# -- PDF methods -- ---------------------------------------
from iwfm.pdf_create import pdf_create
from iwfm.pdf_addpages import pdf_addpages
from iwfm.pdf_setfont import pdf_setfont
from iwfm.pdf_cell import pdf_cell
from iwfm.pdf_addimage import pdf_addimage
from iwfm.pdf_save import pdf_save
from iwfm.pdf2csv import pdf2csv

# -- file system methods ----------------------------------
from iwfm.file_test import file_test
from iwfm.file_missing import file_missing
from iwfm.file_delete import file_delete
from iwfm.file_rename import file_rename
from iwfm.file_2_bak import file_2_bak
from iwfm.file_type_error import file_type_error
from iwfm.file_validate_path import file_validate_path

# -- unit conversion --------------------------------------
from iwfm.cfs2afd import cfs2afd

# -- math -------------------------------------------------
from iwfm.logtrans import logtrans

# -- data file methods ------------------------------------
from iwfm.cdec2monthly import cdec2monthly
from iwfm.vic_2_table import vic_2_table
from iwfm.detaw_2_table import detaw_2_table
from iwfm.dicu2table import dicu2table
from iwfm.write_flows import write_flows

# -- create a submodel ------------------------------------
from iwfm.iwfm_sub_preproc import iwfm_sub_preproc
from iwfm.sub.pp_file import sub_pp_file
from iwfm.sub.pp_node_file import sub_pp_node_file
from iwfm.sub.pp_elem_file import sub_pp_elem_file
from iwfm.sub.pp_lake_file import sub_pp_lake_file
from iwfm.sub.pp_strat_file import sub_pp_strat_file
from iwfm.sub.pp_stream_file import sub_pp_stream_file
from iwfm.get_elem_list import get_elem_list
from iwfm.sub.pp_node_list import sub_pp_node_list
from iwfm.sub.pp_lakes import sub_pp_lakes
from iwfm.sub.pp_streams import sub_pp_streams
from iwfm.get_stream_list_40 import get_stream_list_40
from iwfm.get_stream_list_41 import get_stream_list_41
from iwfm.get_stream_list_42 import get_stream_list_42
from iwfm.get_stream_list_50 import get_stream_list_50
from iwfm.new_pp_files import new_pp_files
new_pp_dict = new_pp_files  # backward compatibility

from iwfm.iwfm_sub_sim import iwfm_sub_sim
from iwfm.iwfm_read_sim_file import iwfm_read_sim_file
from iwfm.sub.sim_file import sub_sim_file
from iwfm.sub.swhed_file import sub_swhed_file
from iwfm.sub.unsat_file import sub_unsat_file
from iwfm.sub.gw_file import sub_gw_file
from iwfm.sub.gw_bc_file import sub_gw_bc_file
from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file
from iwfm.sub.gw_pump_file import sub_gw_pump_file
from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file
from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
from iwfm.sub.gw_td_file import sub_gw_td_file
from iwfm.sub.gw_subs_file import sub_gw_subs_file
from iwfm.sub.streams_file import sub_streams_file
from iwfm.sub.st_inflow_file import sub_st_inflow_file
from iwfm.sub.st_bp_file import sub_st_bp_file
from iwfm.sub.rootzone_file import sub_rootzone_file
from iwfm.sub.rz_npc_file import sub_rz_npc_file
from iwfm.sub.rz_pc_file import sub_rz_pc_file
from iwfm.sub.rz_urban_file import sub_rz_urban_file
from iwfm.sub.rz_nv_file import sub_rz_nv_file
from iwfm.sub.remove_items import sub_remove_items
from iwfm.sub.lu_file import sub_lu_file

from iwfm.new_sim_files import new_sim_files
new_sim_dict = new_sim_files  # backward compatibility

# -- multiprocessing --------------------------------------
from iwfm.multiproc import multiproc

# -- diagnostics module ------------------------------------
from iwfm import diagnostics

# -- other methods -----------------------------------------
from iwfm.meas_bounds import meas_bounds
