# __init__.py for iwfm.calib package
# Classes, methods and functions for interactions between IWFM model calibration
# Copyright (C) 2018-2024 University of California
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

# -- PEST functions ---------------------------------------
'''Classes, methods and functions for interactions between IWFM model calibration.'''

from iwfm.calib.read_settings import read_settings
from iwfm.calib.fac2iwfm import fac2iwfm
from iwfm.calib.iwfm2obs import iwfm2obs
from iwfm.calib.real2iwfm import real2iwfm
from iwfm.calib.par2iwfm import par2iwfm
from iwfm.calib.ppk2fac_trans import ppk2fac_trans
from iwfm.calib.stacdep2obs import stacdep2obs
from iwfm.calib.divshort2obs import divshort2obs
from iwfm.calib.iwfm_exe_time import iwfm_exe_time

# -- supporting functions ---------------------------------------
from iwfm.calib.krige import krige
from iwfm.calib.ltbud import ltbud
from iwfm.calib.ltsmp import ltsmp
from iwfm.calib.setrot import setrot
from iwfm.calib.find_nearest_index import find_nearest_index

# -- PEST SMP files ---------------------------------------
from iwfm.calib.smp_read import smp_read
from iwfm.calib.obs_smp import obs_smp
from iwfm.calib.sim_smp import sim_smp
from iwfm.calib.smp_avg import smp_avg
from iwfm.calib.to_smp_ins import to_smp_ins

# -- math functions ---------------------------------------
from iwfm.calib.bias_calc import bias_calc
from iwfm.calib.compare import compare
from iwfm.calib.do_avgonly import do_avgonly
from iwfm.calib.idw import idw
from iwfm.calib.interp_val import interp_val
from iwfm.calib.res_stats import res_stats
from iwfm.calib.rmse_calc import rmse_calc
from iwfm.calib.pest_res_stats import pest_res_stats
from iwfm.calib.sim_equiv import sim_equiv

# -- data functions ---------------------------------------
from iwfm.calib.get_hyd_fname import get_hyd_fname
from iwfm.calib.get_hyd_info import get_hyd_info
from iwfm.calib.get_hyd_names import get_hyd_names
from iwfm.calib.get_obs_hyd import get_obs_hyd
from iwfm.calib.get_sim_hyd import get_sim_hyd
from iwfm.calib.headdiff_hyds import headdiff_hyds
from iwfm.calib.headdiff_read import headdiff_read
from iwfm.calib.hyds_missed import hyds_missed
from iwfm.calib.read_obs_wells import read_obs_wells
from iwfm.calib.sim_4_sites import sim_4_sites
from iwfm.calib.well_pairs_2_obs_list import well_pairs_2_obs_list

# -- file writing functions ---------------------------------------
from iwfm.calib.write_missing import write_missing
from iwfm.calib.write_results import write_results
from iwfm.calib.write_rmse_bias import write_rmse_bias
from iwfm.calib.simout2gw import simout2gw

# -- iwfm file functions (maybe move to an iwfm-specific subfolder)
from iwfm.calib.read_overwrite_file import read_overwrite_file
from iwfm.calib.write_overwrite_file import write_overwrite_file
