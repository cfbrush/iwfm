# pdf_addimage.py
# add an image to a PDF instance
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


'''Create a cell in a PDF instance.'''

def pdf_addimage(pdf, image, ux=1, uy=1, width=6.5, height=9):
    '''Create a cell in a PDF instance.

    Parameters
    ----------
    pdf : PDF object
        PDF object to be modified

    image : image object
        image to be added to PDF

    ux : int, default=1
        X location of image

    uy : int, default=1
        Y location of image

    width : float, default=6.5
        image width

    height : float, default=9
        image height

    Returns
    -------
    pdf : PDF object
        modiified PDF object
    '''

    pdf.image(image, x=ux, y=uy, w=width, h=height)
    return pdf
