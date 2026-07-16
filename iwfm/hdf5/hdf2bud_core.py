# hdf2bud_core.py
# Convert an IWFM Budget HDF5 file to IWFM text-budget format
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
import numpy as np
import h5py

from iwfm.debug.logger_setup import logger, setup_debug_logger


def hdf2bud_core(hdf_file, output_file,
            len_fact=1.0, len_units='FEET',
            area_fact=0.000022957, area_units='AC',
            vol_fact=0.000022957, vol_units='ACFT',
            verbose=False, debug=False):
    """
    Convert an IWFM Budget HDF5 file to IWFM text-budget format.

    Shared engine for all budget types (groundwater, stream, land & water
    use, root zone, unsaturated zone, small watersheds, stream nodes,
    diversions). The per-type hdf2bud_* functions delegate here.

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

        # Get location names and areas (if available)
        location_names = [name.decode('utf-8').strip() for name in f['Attributes/cLocationNames'][:]]
        # Areas are optional (not present in Stream budgets, for example)
        if 'Areas' in f['Attributes']:
            areas_raw = f['Attributes/Areas'][:]
            areas = areas_raw * area_conversion
        else:
            areas = [0.0] * n_locations  # Placeholder when areas not available

        # Get column header information
        l1_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L1_cColumnHeaders']]
        l2_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L2_cColumnHeaders']]
        l3_headers = [h.decode('utf-8').strip() for h in attrs['LocationData1%L3_cColumnHeaders']]
        col_widths = attrs['LocationData1%iColWidth']
        col_types = attrs['LocationData1%iDataColumnTypes']

        # Get title template
        title_lines = [t.decode('utf-8') for t in attrs['ASCIIOutput%cTitles']]

        # Write output file
        with open(output_file, 'w', encoding='utf-8') as out:
            # Process each location
            for loc_idx in range(n_locations):
                loc_name = location_names[loc_idx]
                area = areas[loc_idx]

                if debug:
                    logger.debug(f"Location {loc_idx+1}/{n_locations}: {loc_name}")

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
                for headers in (l1_headers, l2_headers, l3_headers):
                    header_parts = []
                    for h, w in zip(headers, col_widths):
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
