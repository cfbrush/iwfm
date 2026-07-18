# __init__.py for iwfm.plot package
# Classes, methods and functions for plotting IWFM parameters, results, etc
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


'''Classes, methods and functions for plotting IWFM parameters, results, etc.'''

from iwfm.plot.draw_plot import draw_plot
from iwfm.plot.histogram import histogram
from iwfm.plot.overlay_histograms import overlay_histograms

from iwfm.plot.get_XYvalues import get_XYvalues
from iwfm.plot.flip_y import flip_y

from iwfm.plot.data_to_color import data_to_color
from iwfm.plot.contour_levels import contour_levels

from iwfm.plot.get_maxs import get_maxs
from iwfm.plot.get_mins import get_mins

from iwfm.plot.simhyd_obs import simhyd_obs

from iwfm.plot.head_hydrographs import read_hyd_info
from iwfm.plot.head_hydrographs import read_obs_heads
from iwfm.plot.head_hydrographs import plot_head_hydrograph
from iwfm.plot.head_hydrographs import plot_all_hydrographs
from iwfm.plot.head_hydrographs import extract_sim_dates
from iwfm.plot.head_hydrographs import extract_sim_column

from iwfm.plot.map_to_nodes import map_to_nodes
from iwfm.plot.map_to_nodes_png import map_to_nodes_png
from iwfm.plot.map_to_nodes_contour import map_to_nodes_contour

from iwfm.plot.map_params_gw import map_params_gw
from iwfm.plot.map_params_rz import map_params_rz
from iwfm.plot.map_params_rz_npc import map_params_rz_npc
from iwfm.plot.map_params_rz_nr import map_params_rz_nr
from iwfm.plot.map_params_rz_pc import map_params_rz_pc
from iwfm.plot.map_params_rz_urban import map_params_rz_urban


