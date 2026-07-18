# __init__.py for iwfm.sub submodule
# Submodel extraction functions for IWFM models
# Copyright (C) 2020-2026 University of California
# =============================================================================

# -- preprocessor submodel files ---
'''Submodel extraction functions for IWFM models.'''

from iwfm.sub.pp_file import sub_pp_file
from iwfm.sub.pp_node_file import sub_pp_node_file
from iwfm.sub.pp_elem_file import sub_pp_elem_file
from iwfm.sub.pp_lake_file import sub_pp_lake_file
from iwfm.sub.pp_strat_file import sub_pp_strat_file
from iwfm.sub.pp_stream_file import sub_pp_stream_file
from iwfm.sub.pp_node_list import sub_pp_node_list
from iwfm.sub.pp_lakes import sub_pp_lakes
from iwfm.sub.pp_streams import sub_pp_streams

# -- simulation submodel files ---
from iwfm.sub.sim_file import sub_sim_file
from iwfm.sub.swhed_file import sub_swhed_file
from iwfm.sub.unsat_file import sub_unsat_file
from iwfm.sub.lake_file import sub_lake_file

# -- groundwater submodel files ---
from iwfm.sub.gw_file import sub_gw_file
from iwfm.sub.gw_bc_file import sub_gw_bc_file
from iwfm.sub.gw_bc_cghd_file import sub_gw_bc_cghd_file
from iwfm.sub.gw_pump_file import sub_gw_pump_file
from iwfm.sub.gw_pump_epump_file import sub_gw_pump_epump_file
from iwfm.sub.gw_pump_well_file import sub_gw_pump_well_file
from iwfm.sub.gw_td_file import sub_gw_td_file
from iwfm.sub.gw_subs_file import sub_gw_subs_file

# -- stream submodel files ---
from iwfm.sub.streams_file import sub_streams_file
from iwfm.sub.st_inflow_file import sub_st_inflow_file
from iwfm.sub.st_bp_file import sub_st_bp_file

# -- rootzone submodel files ---
from iwfm.sub.rootzone_file import sub_rootzone_file
from iwfm.sub.rz_npc_file import sub_rz_npc_file
from iwfm.sub.rz_pc_file import sub_rz_pc_file
from iwfm.sub.rz_urban_file import sub_rz_urban_file
from iwfm.sub.rz_nv_file import sub_rz_nv_file

# -- land use and utilities ---
from iwfm.sub.lu_file import sub_lu_file
from iwfm.sub.remove_items import sub_remove_items
