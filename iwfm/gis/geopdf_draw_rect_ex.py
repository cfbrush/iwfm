# geopdf_draw_rect_ex.py
# Example - draw a rectangle on geopdf canvas
# Copyright (C) 2020-2021 University of California
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


def geopdf_draw_rect_ex(canvas):
    '''Example - draw a rectangle on the geopdf canvas.

    ** EXAMPLE **

    Parameters
    ----------
    canvas : geopdf canvas

    Returns
    -------
    nothing
    '''
    canvas.rect(100, 400, 400, 250, stroke=1)
