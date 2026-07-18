# iwfm_aquitard_bottom.py
# extract aquitard bottom from IWFM stratigraphy information
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


def iwfm_aquitard_bottom(strat):
    '''Extract aquitard bottom from IWFM stratigraphy information.

    Parameters
    ----------
    strat : list
        stratigraphy for each model node

    Returns
    -------
    aquitard_bot : list
        wquitard bottom altitude for each model layer and node
    '''
    import iwfm

    (
        aquitard_thick,
        aquifer_thick,
        aquitard_top,
        aquitard_bot,
        aquifer_top,
        aquifer_bot,
    ) = iwfm.iwfm_strat_arrays(strat)
    return aquitard_bot
