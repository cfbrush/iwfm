# hdf2xlsx_lw.py
# Convert IWFM Land & Water Use Budget HDF5 file to Excel workbook
# Copyright (C) 2026 University of California
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

import os


def hdf2xlsx_lw(hdf_file, output_file,
             len_fact=1.0, len_units='FEET',
             area_fact=0.000022957, area_units='AC',
             vol_fact=0.000022957, vol_units='ACFT',
             verbose=False, debug=False):
    """
    Convert IWFM Land & Water Use Budget HDF5 file to Excel workbook

    Parameters
    ----------
    hdf_file : str
        Path to input HDF5 file
    output_file : str
        Path to output Excel file (.xlsx)
    len_fact : float, default=1.0
        Length conversion factor (multiplier)
    len_units : str, default='FEET'
        Length units for output
    area_fact : float, default=0.000022957
        Area conversion factor (sq ft to acres: 0.0000229568411)
    area_units : str, default='AC'
        Area units for output (AC for acres)
    vol_fact : float, default=0.000022957
        Volume conversion factor (cu ft to acre-ft: 0.0000229568411)
    vol_units : str, default='ACFT'
        Volume units for output (ACFT for acre-feet)
    verbose : bool, default=False
        Print progress messages
    debug : bool, default=False
        Enable debug output

    Notes
    -----
    Creates an Excel workbook with:
    - Sheet1 (empty)
    - One sheet per location with budget data

    Default conversion factors:
    - Length: 1.0 (no conversion, stays in feet)
    - Area: 0.000022957 (square feet to acres, exact: 1/43560 = 0.0000229568411)
    - Volume: 0.000022957 (cubic feet to acre-feet, exact: 1/43560 = 0.0000229568411)
    """
    from iwfm.hdf5.hdf2xlsx_core import hdf2xlsx_core

    return hdf2xlsx_core(hdf_file, output_file,
                         budget_title='LAND AND WATER USE BUDGET', area_title='SUBREGION AREA',
                         len_fact=len_fact, len_units=len_units,
                         area_fact=area_fact, area_units=area_units,
                         vol_fact=vol_fact, vol_units=vol_units,
                         verbose=verbose, debug=debug)


if __name__ == '__main__':
    import argparse
    import iwfm.debug as idb

    parser = argparse.ArgumentParser(
        description='Convert IWFM Land & Water Use Budget HDF5 file to Excel workbook',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults (converts to acres and acre-feet)
  python hdf2xlsx_lw.py "C2VSimFG_L&WU_Budget.hdf" output.xlsx

  # Specify custom conversion factors
  python hdf2xlsx_lw.py input.hdf output.xlsx --area-fact 0.000022957 --vol-fact 0.000022957

  # Use different units
  python hdf2xlsx_lw.py input.hdf output.xlsx --area-units "hectares" --vol-units "cubic meters"

Default conversion factors:
  Length: 1.0 (no conversion, stays in feet)
  Area: 0.000022957 (sq ft to acres, exact: 1/43560)
  Volume: 0.000022957 (cu ft to acre-ft, exact: 1/43560)
        """)

    parser.add_argument('hdf_file', nargs='?', help='Input HDF5 budget file')
    parser.add_argument('output_file', nargs='?', help='Output Excel file (default: input.xlsx)')

    parser.add_argument('--len-fact', type=float, default=1.0,
                        help='Length conversion factor (default: 1.0)')
    parser.add_argument('--len-units', type=str, default='FEET',
                        help='Length units for output (default: FEET)')

    parser.add_argument('--area-fact', type=float, default=0.000022957,
                        help='Area conversion factor (default: 0.000022957 for sq ft to acres)')
    parser.add_argument('--area-units', type=str, default='AC',
                        help='Area units for output (default: AC)')

    parser.add_argument('--vol-fact', type=float, default=0.000022957,
                        help='Volume conversion factor (default: 0.000022957 for cu ft to acre-ft)')
    parser.add_argument('--vol-units', type=str, default='ACFT',
                        help='Volume units for output (default: ACFT)')

    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')

    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Get file names
    if args.hdf_file:
        hdf_file = args.hdf_file
        if args.output_file:
            output_file = args.output_file
        else:
            # Default: replace .hdf with .xlsx
            base_name = os.path.splitext(hdf_file)[0]
            output_file = f"{base_name}.xlsx"
    else:
        # Interactive mode
        print("IWFM Land & Water Use Budget HDF5 to Excel Converter")
        hdf_file = input('  Enter Land & Water Use HDF5 budget file name: ')
        output_file = input('  Enter output Excel file name: ')

    idb.exe_time()  # initialize timer

    # Convert the file
    hdf2xlsx_lw(hdf_file, output_file,
             len_fact=args.len_fact, len_units=args.len_units,
             area_fact=args.area_fact, area_units=args.area_units,
             vol_fact=args.vol_fact, vol_units=args.vol_units,
             verbose=not args.quiet, debug=args.debug)


    idb.exe_time()  # print execution time
