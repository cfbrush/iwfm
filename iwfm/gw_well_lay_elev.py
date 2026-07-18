# gw_well_lay_elev.py
# Find layer elevations for each observation well
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


'''Find layer elevations for each observation well.'''

def gw_well_lay_elev(d_wellinfo, elem_nodes_d, node_xy_d, strat, verbose=False):
    '''Find aquifer and aquitard layer elevations at each well by inverse-distance weighting from the nodes of the element containing the well.

    Parameters
    ----------
    d_wellinfo : dict
        key = well name, value = list with [0] = well x, [1] = well y,
        [4] = ID of the element containing the well (other entries are
        carried through unchanged)

    elem_nodes_d : dict
        key = element ID, value = list of the element's node IDs
        (0 entries for triangles are skipped)

    node_xy_d : dict
        key = node ID, value = (x, y) coordinates

    strat : list
        nodal stratigraphy from iwfm_read_strat: one row per node as
        [node_id, lse, aquitard_thick_1, aquifer_thick_1, ...]

    verbose : bool, default=False, optional
        True = command-line output on

    Returns
    -------
    new_d_wellinfo : dict
        key = well name, value = the input list with two entries appended:
        the element's node IDs, and [aquifer_top, aquifer_bot,
        aquitard_top, aquitard_bot], each a list of nlayers elevations
        interpolated to the well location
    '''
    import iwfm
    from iwfm.calib.idw import idw

    if verbose:
        print('  Computing layer elevations at wells')

    (
        aquitard_thick,
        aquifer_thick,
        aquitard_top,
        aquitard_bot,
        aquifer_top,
        aquifer_bot,
    ) = iwfm.iwfm_strat_arrays(strat)
    nlayers = len(aquifer_top[0])

    # stratigraphy arrays are in strat row order; map node ID -> row
    node_row = {int(row[0]): i for i, row in enumerate(strat)}

    new_d_wellinfo = {}
    for key, old_value in d_wellinfo.items():
        x = old_value[0]                        # well x coordinate
        y = old_value[1]                        # well y coordinate
        elem = old_value[4]                     # element containing well

        e_nodes = [n for n in elem_nodes_d[elem] if n > 0]
        nodexy = [node_xy_d[n] for n in e_nodes]
        rows = [node_row[n] for n in e_nodes]

        well_elevs = []
        for surface in (aquifer_top, aquifer_bot, aquitard_top, aquitard_bot):
            elevations = [surface[r] for r in rows]
            well_elevs.append(idw(x, y, elem, e_nodes, nlayers, nodexy, elevations))

        new_value = list(old_value)
        new_value.append(e_nodes)
        new_value.append(well_elevs)
        new_d_wellinfo[key] = new_value

        if verbose:
            print(f'    {key}: layer elevations computed from element {elem}')

    return new_d_wellinfo
