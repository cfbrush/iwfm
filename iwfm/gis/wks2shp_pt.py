# wks2shp_pt.py
# Reads an Excel workbook and creates a POINT shapefile
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


'''Read an Excel workbook and creates a POINT shapefile.'''

def wks2shp_pt(inwksheet, outshp, sheet_index=0):
    '''Read an Excel workbook and create a POINT shapefile.

    Parameters
    ----------
    inwksheet : str
        Excel workbook name

    outshp : str
        output shapefile name

    sheet_index : int, default=0
        Sheet number in workbook

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If Excel workbook doesn't exist
    IndexError
        If sheet_index is out of range
    ValueError
        If coordinate columns contain invalid data
    '''
    import xlrd
    from iwfm.gis.shp_get_writer import shp_get_writer

    # Validate inputs
    if not isinstance(inwksheet, str):
        raise ValueError(
            f"inwksheet must be a string, got {type(inwksheet).__name__}"
        )
    if not isinstance(outshp, str):
        raise ValueError(
            f"outshp must be a string, got {type(outshp).__name__}"
        )

    try:
        xls = xlrd.open_workbook(inwksheet)  # open Excel workbook
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Excel workbook not found: '{inwksheet}'"
        )

    try:
        sheet = xls.sheet_by_index(sheet_index)  # select worksheet
    except IndexError:
        raise IndexError(
            f"Sheet index {sheet_index} out of range. "
            f"Workbook has {xls.nsheets} sheet(s)"
        )

    # Create shapefile writer with proper error handling
    try:
        w = shp_get_writer(outshp, 'POINT')  # open shapefile writer

        # Move data to shapefile table
        for i in range(sheet.ncols):  # read the header row
            w.field(str(sheet.cell(0, i).value), "C", 40)

        # Process data rows
        for i in range(1, sheet.nrows):
            values = [sheet.cell(i, j).value for j in range(sheet.ncols)]
            w.record(*values)

            # Get lat, lon from last two columns
            try:
                lon = float(values[-2])
                lat = float(values[-1])
            except (ValueError, IndexError) as e:
                raise ValueError(
                    f"Invalid coordinates in row {i+1}: "
                    f"longitude='{values[-2]}', latitude='{values[-1]}'. "
                    f"Coordinates must be numeric"
                ) from e

            w.point(lon, lat)

    finally:
        # Ensure shapefile writer is properly closed
        if 'w' in locals():
            w.close()  # Fixed: Added parentheses to actually call close()
