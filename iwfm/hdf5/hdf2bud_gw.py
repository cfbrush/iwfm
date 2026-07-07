#!/usr/bin/env python
# hdf2bud.py
# Convert IWFM Budget HDF5 file to text format
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

import sys
import os
import numpy as np

import h5py

from iwfm.debug.logger_setup import logger, setup_debug_logger


def hdf2bud_gw(hdf_file, output_file,
            len_fact=1.0, len_units='FEET',
            area_fact=0.000022957, area_units='AC',
            vol_fact=0.000022957, vol_units='ACFT',
            verbose=False, debug=False):
    """
    Convert IWFM Budget HDF5 file to text format

    Parameters
    ----------
    hdf_file : str
        Path to input HDF5 file
    output_file : str
        Path to output text file
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
    Default conversion factors:
    - Length: 1.0 (no conversion, stays in feet)
    - Area: 0.000022957 (square feet to acres, exact: 1/43560 = 0.0000229568411)
    - Volume: 0.000022957 (cubic feet to acre-feet, exact: 1/43560 = 0.0000229568411)
    """
    import iwfm

    # Configure loguru logger for debug mode
    if debug:
        setup_debug_logger()  # Auto-detects script name

    if not os.path.exists(hdf_file):
        raise FileNotFoundError(f"File '{hdf_file}' not found")

    if debug:
        logger.debug(f"Opening HDF5 file: {hdf_file}")
        logger.debug(f"Output file: {output_file}")
        logger.debug("Conversion factors:")
        logger.debug(f"  Length: {len_fact} ({len_units})")
        logger.debug(f"  Area: {area_fact} ({area_units})")
        logger.debug(f"  Volume: {vol_fact} ({vol_units})")

    # Conversion factors from model units to output units
    # Model uses square feet and cubic feet by default
    area_conversion = area_fact
    volume_conversion = vol_fact
    length_conversion = len_fact

    with h5py.File(hdf_file, 'r') as f:
        # Get metadata
        attrs = f['Attributes'].attrs

        # Get basic info
        n_locations = attrs['nLocations']
        n_timesteps = attrs['NTimeSteps']
        n_areas = attrs['NAreas']

        # Get time step info
        start_date = attrs['TimeStep%BeginDateAndTime'].decode('utf-8')
        delta_t = attrs['TimeStep%DeltaT']
        time_unit = attrs['TimeStep%Unit'].decode('utf-8')

        if debug:
            logger.debug(f"Locations: {n_locations=}")
            logger.debug(f"Areas: {n_areas=}")
            logger.debug(f"Time steps: {n_timesteps=}")
            logger.debug(f"Start date: {start_date=}")
            logger.debug(f"Time Unit: {time_unit=}")
            logger.debug(f"Delta t: {delta_t=}")

        # Generate time steps (includes the start date as first step)
        timesteps = [start_date] + iwfm.generate_timesteps(start_date, n_timesteps-1, delta_t, time_unit)

        # Get location names and areas
        location_names = [name.decode('utf-8').strip() for name in f['Attributes/cLocationNames'][:]]
        areas_raw = f['Attributes/Areas'][:]
        # Convert areas from sq ft to acres
        areas = areas_raw * area_conversion

        # Get column header information
        l1_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L1_cColumnHeaders']]
        l2_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L2_cColumnHeaders']]
        l3_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L3_cColumnHeaders']]
        full_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%cFullColumnHeaders']]
        col_widths = attrs['LocationData1%iColWidth']
        col_types = attrs['LocationData1%iDataColumnTypes']

        # Get title template
        title_lines = [t.decode('utf-8') for t in attrs['ASCIIOutput%cTitles']]

        # Get descriptor
        descriptor = attrs['Descriptor'].decode('utf-8')

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as out:
            # Process each location
            for loc_idx in range(n_locations):
                loc_name = location_names[loc_idx]
                area = areas[loc_idx]

                if debug:
                    logger.debug(f"Processing location {loc_idx+1}/{n_locations}: {loc_name}")

                # Get data for this location
                data_raw = f[loc_name][:]

                # Convert data based on column type
                # Column types: 1=volume/flow, 2=area, 3=volume stored (storage, discrepancy), 4=length
                # col_types array includes time column (index 0), so data columns start at index 1
                # All volume types (1 and 3) need conversion from cu ft to output volume units
                data = np.zeros_like(data_raw)
                for col_idx in range(data_raw.shape[1]):
                    # col_types[0] is for time, col_types[1] is for first data column, etc.
                    if col_idx + 1 < len(col_types):
                        col_type = col_types[col_idx + 1]
                        if col_type == 1 or col_type == 3:  # Volume (flow or storage) - convert cu ft to output units
                            data[:, col_idx] = data_raw[:, col_idx] * volume_conversion
                        elif col_type == 2:  # Area - convert sq ft to output units
                            data[:, col_idx] = data_raw[:, col_idx] * area_conversion
                        elif col_type == 4:  # Length - convert using length factor
                            data[:, col_idx] = data_raw[:, col_idx] * length_conversion
                        else:
                            data[:, col_idx] = data_raw[:, col_idx]
                    else:
                        # If no type specified, assume volume/flow
                        data[:, col_idx] = data_raw[:, col_idx] * volume_conversion

                # Determine output unit labels
                if vol_units.upper() in ['ACFT', 'AC-FT', 'ACRE-FT', 'ACRE-FEET']:
                    vol_label = 'AC.FT.'
                elif vol_units.upper() in ['AF']:
                    vol_label = 'AF'
                elif vol_units.upper() in ['CFS', 'FT3']:
                    vol_label = vol_units.upper()
                else:
                    vol_label = vol_units.upper()

                if area_units.upper() in ['AC', 'ACRES']:
                    area_label = 'AC'
                else:
                    area_label = area_units.upper()

                # Write title lines with substitutions
                for title in title_lines:
                    # Substitute placeholders
                    title_out = title.replace('@LOCNAME@', loc_name)
                    title_out = title_out.replace('@AREA@', f'{area:,.2f}')
                    title_out = title_out.replace('@UNITVL@', vol_label)
                    title_out = title_out.replace('@UNITAR@', area_label)
                    out.write(title_out + '\n')

                # Write column headers (3 lines)
                # Line 1
                header_parts = []
                for i, (h, w) in enumerate(zip(l1_headers, col_widths)):
                    header_parts.append(h.rjust(w))
                out.write(' '.join(header_parts) + '\n')

                # Line 2
                header_parts = []
                for i, (h, w) in enumerate(zip(l2_headers, col_widths)):
                    header_parts.append(h.rjust(w))
                out.write(' '.join(header_parts) + '\n')

                # Line 3
                header_parts = []
                for i, (h, w) in enumerate(zip(l3_headers, col_widths)):
                    header_parts.append(h.rjust(w))
                out.write(' '.join(header_parts) + '\n')

                # Write separator line
                out.write('-' * 242 + '\n')

                # Write data rows
                for time_idx in range(n_timesteps):
                    row_data = data[time_idx, :]

                    # Format row
                    parts = [timesteps[time_idx].rjust(col_widths[0])]
                    for val, width in zip(row_data, col_widths[1:]):
                        parts.append(f'{val:>{width}.1f}')

                    out.write(' '.join(parts) + '\n')

                # Add blank line between locations (except after last one)
                if loc_idx < n_locations - 1:
                    out.write('\n' * 3)

    if verbose:
        print(f"  Output written to: {output_file}")


if __name__ == '__main__':
    import argparse
    import iwfm.debug as idb

    parser = argparse.ArgumentParser(
        description='Convert IWFM Budget HDF5 file to text format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults (converts to acres and acre-feet)
  python hdf2bud.py C2VSimFG_GW_Budget.hdf output.txt

  # Specify custom conversion factors
  python hdf2bud.py input.hdf output.txt --area-fact 0.000022957 --vol-fact 0.000022957

  # Use different units
  python hdf2bud.py input.hdf output.txt --area-units "hectares" --vol-units "cubic meters"

Default conversion factors:
  Length: 1.0 (no conversion, stays in feet)
  Area: 0.000022957 (sq ft to acres, exact: 1/43560)
  Volume: 0.000022957 (cu ft to acre-ft, exact: 1/43560)
        """)

    parser.add_argument('hdf_file', nargs='?', help='Input HDF5 budget file')
    parser.add_argument('output_file', nargs='?', help='Output text file (default: input_from_hdf.txt)')

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
            # Default: replace .hdf with .txt
            base_name = os.path.splitext(hdf_file)[0]
            output_file = f"{base_name}.bud"
    else:
        # Interactive mode
        print("IWFM Budget HDF5 to Text Converter")
        hdf_file = input('  Enter HDF5 budget file name: ')
        output_file = input('  Enter output text file name: ')

    idb.exe_time()  # initialize timer

    # Convert the file
    hdf2bud_gw(hdf_file, output_file,
            len_fact=args.len_fact, len_units=args.len_units,
            area_fact=args.area_fact, area_units=args.area_units,
            vol_fact=args.vol_fact, vol_units=args.vol_units,
            verbose=not args.quiet, debug=args.debug)

    idb.exe_time()  # print execution time
