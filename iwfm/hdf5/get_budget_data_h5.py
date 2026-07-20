# get_budget_data_h5.py
# Read IWFM Budget HDF file using h5py (cross-platform alternative to pywfm)
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

'''Read budget data from IWFM HDF5 file using h5py.'''

import pandas as pd

import h5py

from iwfm.hdf5.hdf5_utils import (
    apply_unit_conversion,
    decode_hdf5_string,
    decode_hdf5_strings,
    generate_timesteps_from_hdf5,
    get_unit_labels,
    substitute_title_placeholders,
)


def get_budget_data(bud_file,
                    area_conversion_factor=0.0000229568411,
                    volume_conversion_factor=0.0000229568411,
                    length_units="FEET",
                    area_units="ACRES",
                    volume_units="ACRE-FEET",
                    verbose=False):
    """Read budget data from IWFM HDF5 file using h5py.

    This is a cross-platform alternative to the pywfm-based implementation
    that works on Unix/Linux/macOS without requiring the IWFM DLL.

    Parameters
    ----------
    bud_file : str
        Name of IWFM Budget output HDF-formatted file

    area_conversion_factor : float, default=0.0000229568411
        Convert areas from model value to report value
        Default: convert from square feet to acres

    volume_conversion_factor : float, default=0.0000229568411
        Convert volumes from model value to report value
        Default: convert from cubic feet to acre-feet

    length_units : str, default="FEET"
        Length units for output

    area_units : str, default="ACRES"
        Area units for output

    volume_units : str, default="ACRE-FEET"
        Volume units for output

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    loc_names : list
        Location names

    column_headers : list of lists
        Column headers for each location

    loc_values : list of pandas.DataFrame
        Values for each location as DataFrames with Time column

    titles : list of tuples
        Title lines (3 items) for each location
    """
    import iwfm

    iwfm.file_test(bud_file)

    if verbose:
        print(f"  Reading budget data from: {bud_file}")

    with h5py.File(bud_file, 'r') as f:
        # Get metadata from attributes
        attrs = f['Attributes'].attrs

        n_locations = attrs['nLocations']
        n_timesteps = attrs['NTimeSteps']

        # Get time step info
        start_date = decode_hdf5_string(attrs['TimeStep%BeginDateAndTime'])
        delta_t = attrs['TimeStep%DeltaT']
        time_unit = decode_hdf5_string(attrs['TimeStep%Unit'])

        # Generate timesteps
        timesteps = generate_timesteps_from_hdf5(start_date, n_timesteps, delta_t, time_unit)

        # Get location names
        loc_names = decode_hdf5_strings(f['Attributes/cLocationNames'][:])

        # Get areas and convert
        areas_raw = f['Attributes/Areas'][:]
        areas = areas_raw * area_conversion_factor

        # Get column headers
        full_headers = decode_hdf5_strings(attrs['LocationData1%cFullColumnHeaders'])

        # Get column types for unit conversion
        col_types = attrs['LocationData1%iDataColumnTypes']

        # Get title templates
        title_templates = decode_hdf5_strings(attrs['ASCIIOutput%cTitles'])

        # Get unit labels for title substitution
        area_label, vol_label = get_unit_labels(area_units, volume_units)

        # Process each location
        column_headers = []
        loc_values = []
        titles = []

        for loc_idx in range(n_locations):
            loc_name = loc_names[loc_idx]
            area = areas[loc_idx]

            if verbose:
                print(f"    Processing location {loc_idx + 1}/{n_locations}: {loc_name}")

            # Column headers are the same for all locations (typically)
            column_headers.append(full_headers)

            # Get raw data for this location
            data_raw = f[loc_name][:]

            # Apply unit conversions based on column types
            data_converted = apply_unit_conversion(
                data_raw, col_types,
                area_conversion_factor,
                volume_conversion_factor,
                len_fact=1.0
            )

            # Build DataFrame with Time column
            df = pd.DataFrame(data_converted, columns=full_headers[1:])  # Skip 'Time' header
            df.insert(0, 'Time', timesteps[:n_timesteps])

            loc_values.append(df)

            # Build title lines with substitutions
            loc_titles = []
            for template in title_templates:
                title = substitute_title_placeholders(
                    template, loc_name, area, area_label, vol_label
                )
                loc_titles.append(title)

            titles.append(tuple(loc_titles))

    if verbose:
        print(f"  Completed reading {n_locations} locations")

    return loc_names, column_headers, loc_values, titles
