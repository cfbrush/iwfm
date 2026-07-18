# do_avgonly.py
# Calculate average
# Copyright 2020-2026 University of California
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

'''Calculate average.'''

import numpy as np


def do_avgonly(smp_in, ins_lines, pcf_lines):
    smp_out = smp_in

    # Calculate average values for each node in each layer
    smp_out[:, 3:] = np.mean(smp_out[:, 3:], axis=1).reshape(-1, 1)

    return smp_out, ins_lines, pcf_lines
