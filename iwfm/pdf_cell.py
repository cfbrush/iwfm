# pdf_cell.py
# create a cell in a PDF instance
# Copyright (C) 2020-2021 Hydrolytics LLC
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


def pdf_cell(pdf, h=6, w=2, t='', b=0, a='C'):
    """ pdf_cell() - Create a cell in a PDF instance

    Parameters:
      pdf             (PDF):  PDF object
      h               (int):  Cell height
      w               (int):  Cell width
      t               (str):  Text contents (default = none)
      b               (int):  Border thickness (default = none)
      a               (str):  Alignment (default = center)

    Returns:
      pdf             (PDF):   PDF object
    """

    pdf.cell(h, w, t, border=b, align=a)
    return pdf