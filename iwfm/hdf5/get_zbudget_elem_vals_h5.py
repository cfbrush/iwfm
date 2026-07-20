# get_zbudget_elem_vals_h5.py
# Read IWFM ZBudget element values using h5py (cross-platform alternative to pywfm)
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

'''Read zone budget element values from IWFM HDF5 file using h5py.'''

import sys
import numpy as np
from collections import defaultdict

import h5py

from iwfm.hdf5.hdf5_utils import (
    decode_hdf5_string,
    decode_hdf5_strings,
    generate_timesteps_from_hdf5,
    read_zone_definition,
)


def get_zbudget_elem_vals(zbud_file, zones_file, col_ids,
                          area_conversion_factor=0.0000229568411,
                          area_units='ACRES',
                          volume_conversion_factor=0.0000229568411,
                          volume_units='ACRE-FEET',
                          verbose=False):
    """Read zone budget element values from IWFM HDF5 file using h5py.

    This is a cross-platform alternative to the pywfm-based implementation
    that works on Unix/Linux/macOS without requiring the IWFM DLL.

    Note: Unlike the pywfm version which takes an open zbud object,
    this version takes the file path directly.

    Parameters
    ----------
    zbud_file : str
        Path to IWFM ZBudget HDF file

    zones_file : str
        Path to ZBudget zones file

    col_ids : list of int
        Column indices to retrieve (1-indexed, matching pywfm convention)

    area_conversion_factor : float, default=0.0000229568411
        Area conversion factor

    area_units : str, default='ACRES'
        Area units

    volume_conversion_factor : float, default=0.0000229568411
        Volume conversion factor

    volume_units : str, default='ACRE-FEET'
        Volume units

    verbose : bool, default=False
        Turn command-line output on or off

    Returns
    -------
    dates : list
        Model time steps as date strings

    zone_data : list of lists
        Each inner list: [zone_id, col1_sum, col2_sum, ...]
        First element is zone ID (1-indexed), rest are column sums
    """
    import iwfm

    iwfm.file_test(zbud_file)
    iwfm.file_test(zones_file)

    # Read zone definitions
    zextent, zone_info, element_zones = read_zone_definition(zones_file)

    if verbose:
        print(f"  Reading zone budget element values from: {zbud_file}")
        print(f"  Zones defined: {len(zone_info)}")

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

        # Get component names
        full_data_names = decode_hdf5_strings(f['Attributes/FullDataNames'][:])

        # Get element-to-column mappings
        elem_col_maps = {}
        for layer_idx in range(1, n_layers + 1):
            map_name = f'Layer{layer_idx}_ElemDataColumns'
            if map_name in f['Attributes']:
                elem_col_maps[layer_idx] = f[f'Attributes/{map_name}'][:]

        # Initialize zone data storage for each requested column
        # zone_sums[zone_id][col_idx] = total sum across all timesteps
        zone_sums = defaultdict(lambda: defaultdict(float))

        # Map col_ids to component indices (col_ids are 1-indexed)
        # col_ids correspond to columns in the output DataFrame, which alternates IN/OUT
        # for each component. So col_id 1 = first component IN, 2 = first component OUT, etc.

        # Process data by layer
        for layer_idx in range(1, n_layers + 1):
            layer_name = f'Layer_{layer_idx}'

            if layer_name not in f or layer_idx not in elem_col_maps:
                continue

            if verbose:
                print(f"    Processing {layer_name}...")

            elem_col_map = elem_col_maps[layer_idx]

            # Process each requested column
            for col_list_idx, col_id in enumerate(col_ids):
                # Determine which component and flow direction from col_id
                # col_id is 1-indexed: 1=comp1_in, 2=comp1_out, 3=comp2_in, 4=comp2_out, etc.
                comp_idx = (col_id - 1) // 2
                is_inflow = (col_id - 1) % 2 == 0

                if comp_idx * 2 >= len(full_data_names):
                    continue

                # Find the corresponding component name
                if is_inflow:
                    comp_search = '_Inflow'
                else:
                    comp_search = '_Outflow'

                comp_full_name = None
                comp_name_idx = 0
                for idx, name in enumerate(full_data_names):
                    if comp_search in name:
                        if comp_name_idx == comp_idx:
                            comp_full_name = name
                            comp_data_idx = idx
                            break
                        comp_name_idx += 1

                if comp_full_name is None:
                    continue

                # Get dataset
                dataset_path = f'{layer_name}/{comp_full_name}'
                if dataset_path not in f:
                    continue

                data_array = f[dataset_path][:] * volume_conversion_factor

                # Sum across all timesteps and aggregate to zones
                for elem_idx in range(n_elements):
                    element = elem_idx + 1

                    # Get column index for this element
                    if comp_data_idx < elem_col_map.shape[0] and elem_idx < elem_col_map.shape[1]:
                        data_col = elem_col_map[comp_data_idx, elem_idx]
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

                    # Sum all timesteps for this element
                    if data_col_idx < data_array.shape[1]:
                        total = np.sum(data_array[:, data_col_idx])
                        zone_sums[zone][col_list_idx] += total

    # Build output
    zone_list = sorted(zone_info.keys())

    zone_data = []
    counter = 0
    for zone_id in zone_list:
        if verbose and counter >= 99:
            print(f' {zone_id:,}')
            counter = 0
        else:
            counter += 1

        row = [zone_id]
        for col_idx in range(len(col_ids)):
            row.append(zone_sums[zone_id][col_idx])
        zone_data.append(row)

    if verbose:
        print(f"  Completed processing {len(zone_list)} zones")

    return timesteps, zone_data


if __name__ == '__main__':
    """Run get_zbudget_elem_vals() from command line."""
    import os
    import pickle
    import iwfm
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()


    if len(sys.argv) > 1:
        hdf_file = sys.argv[1]
        zones_file = sys.argv[2]
        out_file = sys.argv[3]
    else:
        hdf_file = input('IWFM Z-Budget file name: ')
        zones_file = input('IWFM Z-Budget Zones file name: ')
        out_file = input('Output file name: ')

    iwfm.file_test(hdf_file)
    iwfm.file_test(zones_file)

    idb.exe_time()

    # Elemental pumping columns in IWFM Groundwater ZBudget HDF file
    col_ids = [9, 21]

    dates, zone_data = get_zbudget_elem_vals(hdf_file, zones_file, col_ids, verbose=verbose)

    pickle_base = os.path.basename(out_file).split('.')[0]
    with open(pickle_base + '.pkl', 'wb') as f_pkl:
        pickle.dump(zone_data, f_pkl)

    with open(out_file, 'w', encoding='utf-8') as f_out:
        f_out.write('ElemID\tElem Pumping\tWell Pumping\n')
        for row in zone_data:
            f_out.write(f'{row[0]}\t{row[1]:.2f}\t{row[2]:.2f}\n')

    idb.exe_time()
