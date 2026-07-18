# iwfm_strat_arrays.py
# parse IWFM stratigraphy information into arrays
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


def iwfm_strat_arrays(strat):
    '''Read IWFM nodal stratigraphy information into individual arrays.

    Parameters
    ----------
    strat : list
        stratigraphy information

    Returns
    -------
    aquitard_thick : list
        aquitard thickness by model layer and node

    aquifer_thick : list
        aquifer thickness by model layer and node

    aquitard_top : list
        aquitard top altitude by model layer and node

    aquitard_bot : list
        aquitard bottom altitude by model layer and node

    aquifer_top : list
        aquifer top altitude by model layer and node

    aquifer_bot : list
        aquifer bottom altitude by model layer and node
    '''
    nlayers = (len(strat[0]) - 2) // 2

    aquitard_thick = []  # initialize arrays
    aquifer_thick = []
    aquitard_top = []
    aquitard_bot = []
    aquifer_top = []
    aquifer_bot = []

    for i in range(0, len(strat)):  # cycle through stratigraphy of each node
        Tthick,Athick,AttElev,AtbElev,AqtElev,AqbElev  = [],[],[],[],[],[]

        lse = float(strat[i][1])
        depth = 0

        for j in range(0, nlayers):
            AttElev.append(lse - depth)

            t = strat[i][2 + 2 * j]
            Tthick.append(t)
            depth += t
            AtbElev.append(lse - depth)
            AqtElev.append(lse - depth)

            a = strat[i][2 + 2 * j + 1]
            Athick.append(a)
            depth += a
            AqbElev.append(lse - depth)

        aquitard_thick.append(Tthick)
        aquifer_thick.append(Athick)
        aquitard_top.append(AttElev)
        aquitard_bot.append(AtbElev)
        aquifer_top.append(AqtElev)
        aquifer_bot.append(AqbElev)  

    return (
        aquitard_thick,
        aquifer_thick,
        aquitard_top,
        aquitard_bot,
        aquifer_top,
        aquifer_bot,
    )
