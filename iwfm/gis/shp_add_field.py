# shp_add_field.py
# Add a field to a shapefile with PyShp
# Copyright (C) 2020-2024 University of California
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


def shp_add_field(shapefilename, field_name='TEST', type='F', length=8, prec=5):
    '''Add a field to a shapefile with PyShp.

    Parameters
    ----------
    shapefilename : str
        shapefile name

    field_name : str
        field name, default='test'

    type : str, default='F'
        field type

    length : int, default=8
        field length

    prec : int, default=5
        field Precision

    Return
    ------
    nothing
    '''
    import shapefile  # PyShp

    r = shapefile.Reader(shapefilename)
    shapes = r.shapes()
    attributes = r.records()

    with shapefile.Writer(shapefilename, r.shapeType) as w:
        w.fields = list(r.fields)                   # copy the existing fields
        w.field(field_name, type, length, prec)     # add the new field

        for i in range(len(shapes)):
            w.record(*attributes[i])                # copy the existing records
            w.shape(shapes[i])                      # add the new shape
    return 

