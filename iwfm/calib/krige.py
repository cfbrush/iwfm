# krige.py 
# Perform spatial interpolation from grid A to grid B using kriging factors.
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

def krige(A, B):
    """ krige() - Perform spatial interpolation using kriging factors from grid A to grid B.

    Parameters
    ----------
    A : list
        List of tuples representing grid A points. Each tuple contains (id, x, y) coordinates.
    
    B : list
        List of tuples representing grid B points. Each tuple contains (id, x, y, value) coordinates.
    
    Returns
    -------
    kriging_factors : list
        List of lists containing kriging factor floats for spatial interpolation.
    """
    import numpy as np
    from scipy.spatial.distance import cdist

    kriging_factors = []

    for a_id, ax, ay in A:
        # Calculate the distances from each point in B to all points in A
        distances = cdist([(ax, ay)], [(bx, by) for _, bx, by, _ in B])
        
        # Compute kriging factors (inverse distance weights) for each point in A
        weights = 1 / distances
        
        # Normalize the weights to sum up to 1
        normalized_weights = weights / np.sum(weights)
        
        # Append the kriging factors for the current point in B to the list
        kriging_factors.append(normalized_weights.tolist()[0])
    from iwfm.debug.logger_setup import logger
    logger.debug(f'krige: computed {len(kriging_factors)} kriging factor sets')
    return kriging_factors


