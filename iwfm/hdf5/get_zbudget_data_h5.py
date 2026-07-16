# get_zbudget_data_h5.py
# Read IWFM ZBudget HDF file using h5py (cross-platform alternative to pywfm)
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

import numpy as np
import pandas as pd
from collections import defaultdict

import h5py

from iwfm.hdf5.hdf5_utils import (
    decode_hdf5_string,
    decode_hdf5_strings,
    generate_timesteps_from_hdf5,
    read_zone_definition,
    get_unit_labels,
)


def get_zbudget_data(zbud_file, zone_file,
                     area_units='ACRES',
                     area_conversion_factor=0.0000229568411,
                     volume_units='AC-FT',
                     volume_conversion_factor=0.0000229568411,
                     logging=False,
                     verbose=False):
    """Read zone budget data from IWFM HDF5 file using h5py.

    This is a cross-platform alternative to the pywfm-based implementation
    that works on Unix/Linux/macOS without requiring the IWFM DLL.

    Parameters
    ----------
    zbud_file : str
        Name of IWFM ZBudget output HDF-formatted file

    zone_file : str
        Name of IWFM ZBudget zone file

    area_units : str, default='ACRES'
        Units for area values

    area_conversion_factor : float, default=0.0000229568411
        Convert areas from model value to report value
        Default: convert from square feet to acres

    volume_units : str, default='AC-FT'
        Units for volume values

    volume_conversion_factor : float, default=0.0000229568411
        Convert volumes from model value to report value
        Default: convert from cubic feet to acre-feet

    logging : bool, default=False
        Turn zbudget logging on or off (ignored in h5py version)

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    zone_names : list
        Zone names

    column_headers : list of lists
        Column headers for each zone

    zone_values : list of pandas.DataFrame
        Values for each zone as DataFrames

    titles : list of tuples
        Title lines for each zone

    zone_list : list
        List of zone IDs

    zone_extent_ids : int
        Zone extent (1=horizontal plane, 0=per-layer)
    """
    import iwfm

    iwfm.file_test(zbud_file)
    iwfm.file_test(zone_file)

    if verbose:
        print(f"  Reading zone budget data from: {zbud_file}")
        print(f"  Using zone definition file: {zone_file}")

    # Read zone definitions
    zextent, zone_info, element_zones = read_zone_definition(zone_file)

    if verbose:
        print(f"    ZEXTENT: {zextent}")
        print(f"    Zones defined: {len(zone_info)}")

    with h5py.File(zbud_file, 'r') as f:
        attrs = f['Attributes'].attrs

        # Get dimensions
        n_elements = attrs.get('SystemData%NElements', attrs.get('nLocations', 1))
        n_timesteps = attrs['NTimeSteps']
        n_layers = attrs.get('SystemData%NLayers', attrs.get('NLayers', 1))

        # Get time step info
        start_date = decode_hdf5_string(attrs['TimeStep%BeginDateAndTime'])
        delta_t = attrs['TimeStep%DeltaT']
        time_unit = decode_hdf5_string(attrs['TimeStep%Unit'])

        # Generate timesteps
        timesteps = generate_timesteps_from_hdf5(start_date, n_timesteps, delta_t, time_unit)

        if verbose:
            print(f"    Elements: {n_elements}, Layers: {n_layers}, Timesteps: {n_timesteps}")

        # Get element areas
        if 'SystemData%ElementAreas' in f['Attributes']:
            elem_areas = f['Attributes/SystemData%ElementAreas'][:] * area_conversion_factor
        elif 'Areas' in f['Attributes']:
            elem_areas = f['Attributes/Areas'][:] * area_conversion_factor
        else:
            elem_areas = np.ones(n_elements) * area_conversion_factor

        # Calculate zone areas
        zone_areas = defaultdict(float)
        for elem_idx in range(n_elements):
            element = elem_idx + 1
            if zextent == 1:
                zone = element_zones.get(element, -99)
                if zone != -99:
                    zone_areas[zone] += elem_areas[elem_idx]
            else:
                for layer in range(1, n_layers + 1):
                    zone = element_zones.get((element, layer), -99)
                    if zone != -99:
                        zone_areas[zone] += elem_areas[elem_idx] / n_layers

        # Get component names from FullDataNames
        full_data_names = decode_hdf5_strings(f['Attributes/FullDataNames'][:])

        # Extract unique base component names (remove _Inflow/Outflow suffixes)
        base_components = []
        for name in full_data_names:
            if '_Inflow' in name:
                base = name.replace('_Inflow (+)', '').strip()
                if base not in base_components:
                    base_components.append(base)

        # Get element-to-column mappings for each layer
        elem_col_maps = {}
        for layer_idx in range(1, n_layers + 1):
            map_name = f'Layer{layer_idx}_ElemDataColumns'
            if map_name in f['Attributes']:
                elem_col_maps[layer_idx] = f[f'Attributes/{map_name}'][:]

        # Initialize zone data storage
        # zone_data[zone_id][component][in/out] = array of shape (n_timesteps,)
        zone_data = defaultdict(lambda: defaultdict(lambda: {
            'in': np.zeros(n_timesteps),
            'out': np.zeros(n_timesteps)
        }))

        # Process data by layer and component
        for layer_idx in range(1, n_layers + 1):
            layer_name = f'Layer_{layer_idx}'

            if layer_name not in f or layer_idx not in elem_col_maps:
                continue

            if verbose:
                print(f"    Processing {layer_name}...")

            elem_col_map = elem_col_maps[layer_idx]

            # Process each component
            for comp_idx, comp_full_name in enumerate(full_data_names):
                # Determine if this is inflow or outflow
                is_inflow = '_Inflow' in comp_full_name or '(+)' in comp_full_name
                flow_dir = 'in' if is_inflow else 'out'

                # Get the component base name
                comp_base = comp_full_name.replace('_Inflow (+)', '').replace('_Outflow (-)', '').strip()

                # Get dataset path
                dataset_path = f'{layer_name}/{comp_full_name}'
                if dataset_path not in f:
                    continue

                data_array = f[dataset_path][:] * volume_conversion_factor

                # Aggregate to zones
                for elem_idx in range(n_elements):
                    element = elem_idx + 1

                    # Get column index for this element
                    if comp_idx < elem_col_map.shape[0] and elem_idx < elem_col_map.shape[1]:
                        data_col = elem_col_map[comp_idx, elem_idx]
                    else:
                        continue

                    if data_col == 0:
                        continue

                    data_col_idx = data_col - 1

                    # Determine zone
                    if zextent == 1:
                        zone = element_zones.get(element, -99)
                    else:
                        zone = element_zones.get((element, layer_idx), -99)

                    if zone == -99:
                        continue

                    # Add to zone total
                    if data_col_idx < data_array.shape[1]:
                        zone_data[zone][comp_base][flow_dir] += data_array[:, data_col_idx]

    # Build output structures
    zone_list = sorted(zone_info.keys())
    zone_names = [zone_info[z] for z in zone_list]
    zone_extent_ids = zextent

    # Build column headers (IN/OUT for each component)
    headers = ['Time']
    for comp in base_components:
        headers.extend([f'{comp}_IN', f'{comp}_OUT'])
    headers.append('Discrepancy')

    # Get unit labels
    area_label, vol_label = get_unit_labels(area_units, volume_units)

    column_headers = []
    zone_values = []
    titles = []

    for zone_id in zone_list:
        zone_name = zone_info[zone_id]
        zone_area = zone_areas.get(zone_id, 0.0)

        if verbose:
            print(f"    Building output for zone {zone_id}: {zone_name}")

        # Column headers for this zone
        column_headers.append(headers)

        # Build DataFrame
        df_data = {'Time': timesteps[:n_timesteps]}

        total_in = np.zeros(n_timesteps)
        total_out = np.zeros(n_timesteps)

        for comp in base_components:
            in_vals = zone_data[zone_id][comp]['in']
            out_vals = zone_data[zone_id][comp]['out']
            df_data[f'{comp}_IN'] = in_vals
            df_data[f'{comp}_OUT'] = out_vals
            total_in += in_vals
            total_out += out_vals

        df_data['Discrepancy'] = total_in - total_out

        df = pd.DataFrame(df_data)
        zone_values.append(df)

        # Build title lines
        title1 = f"GROUNDWATER ZONE BUDGET IN {vol_label} FOR ZONE {zone_id} ({zone_name})"
        title2 = f"ZONE AREA: {zone_area:,.2f} {area_label}"
        title3 = "-" * 80
        titles.append((title1, title2, title3))

    if verbose:
        print(f"  Completed reading {len(zone_list)} zones")

    return zone_names, column_headers, zone_values, titles, zone_list, zone_extent_ids
