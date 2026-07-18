# hdf2zbud_gw.py
# Convert IWFM Groundwater Zone Budget HDF5 file to text format
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

from iwfm.debug.logger_setup import logger, setup_debug_logger
from iwfm.hdf5.zbud_gw_core import read_zone_definition, zbud_gw_aggregate  # noqa: F401  (read_zone_definition re-exported for compatibility)


def hdf2zbud_gw(hdf_file, zone_file, output_file,
                area_fact=0.000022957, area_units='AC',
                vol_fact=0.000022957, vol_units='ACFT',
                verbose=False, debug=False):
    '''Convert IWFM Groundwater Zone Budget HDF5 file to text format.

    Reading and zone aggregation are shared with hdf2zxlsx_gw via
    zbud_gw_core.zbud_gw_aggregate(); this function only formats the
    fixed-width text output.

    Parameters
    ----------
    hdf_file : str
        Path to input HDF5 zone budget file
    zone_file : str
        Path to zone definition file
    output_file : str
        Path to output text file
    area_fact : float
        Area conversion factor (default: sq ft to acres)
    area_units : str
        Area units for output
    vol_fact : float
        Volume conversion factor (default: cu ft to acre-ft)
    vol_units : str
        Volume units for output
    verbose : bool
        Print progress messages
    debug : bool, default=False
        Enable debug output (more detailed than verbose)
    '''
    import iwfm

    # Configure loguru logger for debug mode
    if debug:
        setup_debug_logger()  # Auto-detects script name

    z = zbud_gw_aggregate(hdf_file, zone_file,
                          area_fact=area_fact, vol_fact=vol_fact,
                          verbose=verbose, debug=debug)

    zone_info, zone_areas = z.zone_info, z.zone_areas
    full_headers, zone_data = z.full_headers, z.zone_data
    n_timesteps, descriptor = z.n_timesteps, z.descriptor

    # Generate time steps (includes the start date as first step)
    timesteps = [z.start_date] + iwfm.generate_timesteps(
        z.start_date, n_timesteps - 1, z.delta_t, z.time_unit)

    # Write output file
    if debug:
        logger.debug(f"Writing output: {output_file}")

    # Determine unit labels
    if vol_units.upper() in ['ACFT', 'AC-FT', 'ACRE-FT', 'ACRE-FEET']:
        vol_label = 'AF'
    else:
        vol_label = vol_units.upper()

    if area_units.upper() in ['AC', 'ACRES']:
        area_label = 'AC'
    else:
        area_label = area_units.upper()

    with open(output_file, 'w', encoding='utf-8') as out:
        # Write zone budgets
        for zone_id in sorted(zone_data.keys()):
            zone_name = zone_info.get(zone_id, f'Zone{zone_id}')
            zone_area = zone_areas.get(zone_id, 0.0)

            if debug:
                logger.debug(f"Writing zone {zone_id}: {zone_name}")
                logger.debug(f"Zone area: {zone_area:,.2f} {area_units}")

            # Write header
            descriptor_line = f"{descriptor:^240}\n"
            title_line = f"GROUNDWATER ZONE BUDGET IN {vol_label} FOR ZONE {zone_id} ({zone_name})".ljust(240) + "\n"
            area_line = f"ZONE AREA: {zone_area:,.2f} {area_label}".ljust(240) + "\n"

            out.write(descriptor_line)
            out.write(title_line)
            out.write(area_line)
            out.write('-' * 500 + '\n')

            # Write column headers (IN/OUT for each component)
            # Row 1: Component names centered over each pair of IN/OUT columns (30 chars each)
            # Row 2: IN and OUT labels (15 chars each)
            # Row 3: (+) and (-) symbols (15 chars each)

            # Row 1: Component names
            row1 = ' ' * 17  # Space for Time column
            for header in full_headers:
                row1 += f"{header:^30}"
            row1 += f"{'Discrepancy':^15}{'Absolute':^15}\n"

            # Row 2: IN/OUT labels
            row2 = f"{'Time':>17}"
            for _ in full_headers:
                row2 += f"{'IN':>15}{'OUT':>15}"
            row2 += f"{'':>15}{'   Storage':<15}\n"

            # Row 3: (+)/(-) symbols
            row3 = ' ' * 17  # Space for Time column
            for _ in full_headers:
                row3 += f"{'(+)':>15}{'(-)':>15}"
            row3 += f"{'(=)':>12}{'':>18}\n"

            out.write(row1)
            out.write(row2)
            out.write(row3)
            out.write('-' * 500 + '\n')

            # Write data rows
            for time_idx in range(n_timesteps):
                row_parts = [f"{timesteps[time_idx]:>17}"]

                total_in = 0.0
                total_out = 0.0

                for col_idx in range(len(full_headers)):
                    in_val = zone_data[zone_id][col_idx]['in'][time_idx]
                    out_val = zone_data[zone_id][col_idx]['out'][time_idx]

                    row_parts.append(f"{in_val:>15.2f}")
                    row_parts.append(f"{out_val:>15.2f}")

                    total_in += in_val
                    total_out += out_val

                # Calculate discrepancy
                discrepancy = total_in - total_out

                # Try to get absolute storage from GW Storage component
                abs_storage = 0.0
                for col_idx, header in enumerate(full_headers):
                    if 'Storage' in header or 'STORAGE' in header:
                        # Storage is cumulative: IN - OUT
                        abs_storage = zone_data[zone_id][col_idx]['in'][time_idx] - zone_data[zone_id][col_idx]['out'][time_idx]
                        break

                row_parts.append(f"{discrepancy:>13.2f}")
                row_parts.append(f"{abs_storage:>15.2f}")

                out.write(''.join(row_parts) + '\n')

            out.write('\n\n')

    if verbose:
        print(f"  Output written to: {output_file}")


if __name__ == '__main__':
    import argparse
    import iwfm.debug as idb

    parser = argparse.ArgumentParser(
        description='Convert IWFM Groundwater Zone Budget HDF5 to text format',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('hdf_file', help='Input HDF5 zone budget file')
    parser.add_argument('zone_file', help='Zone definition file (.dat)')
    parser.add_argument('output_file', help='Output text file (.bud)')

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

    idb.exe_time()  # initialize timer

    hdf2zbud_gw(args.hdf_file, args.zone_file, args.output_file,
                area_fact=args.area_fact, area_units=args.area_units,
                vol_fact=args.vol_fact, vol_units=args.vol_units,
                verbose=not args.quiet, debug=args.debug)

    idb.exe_time()  # print execution time
