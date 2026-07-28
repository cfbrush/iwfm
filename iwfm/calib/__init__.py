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

# Submodules are imported lazily (PEP 562): each function lives in a module of
# the same name and is only imported on first attribute access. This keeps
# `python -m iwfm.calib.<tool>` from triggering runpy's "found in sys.modules"
# RuntimeWarning and avoids importing the whole package up front.

_lazy_names = (
    # -- PEST functions ---------------------------------------
    'read_settings',
    'fac2iwfm',
    'iwfm2obs',
    'real2iwfm',
    'par2iwfm',
    'ppk2fac_trans',
    'stacdep2obs',
    'divshort2obs',
    'iwfm_exe_time',
    # -- supporting functions ---------------------------------
    'krige',
    'ltbud',
    'ltsmp',
    'setrot',
    'find_nearest_index',
    # -- PEST SMP files ---------------------------------------
    'smp_read',
    'obs_smp',
    'sim_smp',
    'smp_avg',
    'to_smp_ins',
    # -- math functions ---------------------------------------
    'bias_calc',
    'compare',
    'do_avgonly',
    'idw',
    'interp_val',
    'res_stats',
    'rmse_calc',
    'pest_res_stats',
    'sim_equiv',
    # -- data functions ---------------------------------------
    'get_hyd_fname',
    'get_hyd_info',
    'get_hyd_names',
    'get_obs_hyd',
    'get_sim_hyd',
    'headdiff_hyds',
    'headdiff_read',
    'hyds_missed',
    'read_obs_wells',
    'rei_residual_clusters',
    'sim_4_sites',
    'well_pairs_2_obs_list',
    # -- file writing functions -------------------------------
    'write_missing',
    'write_results',
    'write_rmse_bias',
    'simout2gw',
    # -- iwfm file functions (maybe move to an iwfm-specific subfolder)
    'read_overwrite_file',
    'write_overwrite_file',
)

__all__ = list(_lazy_names)


def __getattr__(name):
    if name in _lazy_names:
        from importlib import import_module
        func = getattr(import_module(f'iwfm.calib.{name}'), name)
        globals()[name] = func  # cache so __getattr__ only runs once per name
        return func
    raise AttributeError(f"module 'iwfm.calib' has no attribute '{name}'")


def __dir__():
    return sorted(set(globals()) | set(_lazy_names))
