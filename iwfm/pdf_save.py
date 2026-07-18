# pdf_save.py
# save a PDF instance to a PDF file
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


def pdf_save(pdf, filename):
    '''Save a PDF instance to a PDF file.

    Parameters
    ----------
    pdf : PDF object
        PDF object to be saved

    filename : str
        output file name

    Returns
    -------
    nothing
    '''
    pdf.output(filename, 'F')  # 'F' = to file system
    return
