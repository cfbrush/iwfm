# zbud_gw_core.py
# Shared read/aggregate engine for IWFM groundwater zone-budget HDF5 files
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

import os
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import h5py

from iwfm.debug.logger_setup import logger, setup_debug_logger


def read_zone_definition(zone_file):
    """
    Read zone definition file

    Returns
    -------
    zextent : int
        1 = zones defined for horizontal plane (all layers)
        0 = different zones for each layer
    zone_info : dict
        {zone_id: zone_name}
    element_zones : dict
        if zextent==1: {element: zone}
        if zextent==0: {(element, layer): zone}
    """
    zone_info = {}
    element_zones = {}
    zextent = None

    with open(zone_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find ZEXTENT
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith('C'):
            try:
                zextent = int(line.split()[0])
                break
            except ValueError:
                continue

    if zextent is None:
        raise ValueError("Could not find ZEXTENT value in zone definition file")

    # Find zone names section
    reading_zones = False
    reading_elements = False

    for line in lines:
        line_strip = line.strip()

        # Skip comments and empty lines
        if not line_strip or line_strip.startswith('C'):
            # Check for section headers in comments
            if 'ZID' in line_strip and 'ZNAME' in line_strip:
                reading_zones = True
                reading_elements = False
                continue
            elif 'IE' in line_strip and 'ZONE' in line_strip:
                reading_zones = False
                reading_elements = True
                continue
            continue

        # Read zone definitions
        if reading_zones and not reading_elements:
            parts = line_strip.split(None, 1)
            if len(parts) >= 2:
                try:
                    zone_id = int(parts[0])
                    zone_name = parts[1]
                    zone_info[zone_id] = zone_name
                except ValueError:
                    pass

        # Read element-zone assignments
        elif reading_elements:
            parts = line_strip.split()
            if len(parts) >= 2:
                try:
                    element = int(parts[0])
                    if zextent == 1:
                        # Format: IE ZONE
                        zone = int(parts[1])
                        element_zones[element] = zone
                    else:
                        # Format: IE LAYER ZONE
                        if len(parts) >= 3:
                            layer = int(parts[1])
                            zone = int(parts[2])
                            element_zones[(element, layer)] = zone
                except ValueError:
                    pass

    return zextent, zone_info, element_zones


@dataclass
class ZBudgetData:
    """Aggregated zone-budget data returned by zbud_gw_aggregate().

    Attributes
    ----------
    zextent : int
        1 = horizontal zones, 0 = per-layer zones
    zone_info : dict
        {zone_id: zone_name}
    zone_areas : dict
        {zone_id: area in output units}
    full_headers : list
        component base names in output column order
    zone_data : dict
        zone_data[zone_id][col_idx]['in'|'out'] = ndarray (n_timesteps,)
        in output volume units
    n_timesteps : int
    start_date : str
        first time step in DSS format
    delta_t : int
        time step length
    time_unit : str
        time step unit (e.g. '1MON')
    descriptor : str
        budget descriptor from the HDF5 file
    """
    zextent: int
    zone_info: dict
    zone_areas: dict
    full_headers: list
    zone_data: dict
    n_timesteps: int
    start_date: str
    delta_t: int
    time_unit: str
    descriptor: str


def zbud_gw_aggregate(hdf_file, zone_file,
                      area_fact=0.000022957, vol_fact=0.000022957,
                      verbose=False, debug=False):
    """
    Read an IWFM groundwater zone-budget HDF5 file and aggregate the raw
    per-element, per-layer component data into per-zone in/out time series.

    Shared engine for hdf2zbud_gw (text output) and hdf2zxlsx_gw (Excel
    output). Zone-budget HDF5 files hold raw element data in Layer_N groups
    (one dataset per component, '_Inflow (+)' / '_Outflow (-)' suffixes)
    plus LayerN_ElemDataColumns element-to-column maps; the zone
    aggregation is done here, driven by a user-supplied zone definition
    file (see read_zone_definition).

    Parameters
    ----------
    hdf_file : str
        Path to input HDF5 zone budget file
    zone_file : str
        Path to zone definition file
    area_fact : float, default=0.000022957
        Area conversion factor (default: sq ft to acres)
    vol_fact : float, default=0.000022957
        Volume conversion factor (default: cu ft to acre-ft)
    verbose : bool, default=False
        Print progress messages
    debug : bool, default=False
        Enable debug output

    Returns
    -------
    ZBudgetData
    """
    # Configure loguru logger for debug mode
    if debug:
        setup_debug_logger()  # Auto-detects script name

    if not os.path.exists(hdf_file):
        raise FileNotFoundError(f"HDF5 file '{hdf_file}' not found")

    if not os.path.exists(zone_file):
        raise FileNotFoundError(f"Zone definition file '{zone_file}' not found")

    if debug:
        logger.debug(f"Reading zone definition: {zone_file}")

    # Read zone definitions
    zextent, zone_info, element_zones = read_zone_definition(zone_file)

    if debug:
        logger.debug(f"ZEXTENT: {zextent}")
        logger.debug(f"Zones defined: {len(zone_info)}")
        logger.debug(f"Element assignments: {len(element_zones)}")
        logger.debug(f"Reading HDF5 file: {hdf_file}")

    with h5py.File(hdf_file, 'r') as f:
        # Get metadata
        attrs = f['Attributes'].attrs

        n_elements = attrs.get('SystemData%NElements', attrs.get('nLocations', 1))
        n_timesteps = attrs['NTimeSteps']
        n_layers = attrs.get('SystemData%NLayers', attrs.get('NLayers', 1))

        # Get time step info
        start_date = attrs['TimeStep%BeginDateAndTime'].decode('utf-8')
        delta_t = attrs['TimeStep%DeltaT']
        time_unit = attrs['TimeStep%Unit'].decode('utf-8')

        # Get descriptor
        descriptor = attrs.get('Descriptor', b'IWFM Groundwater Zone Budget').decode('utf-8')

        # Build column headers from component names in Layer_1
        # Component names are like "GW Storage_Inflow (+)", "GW Storage_Outflow (-)"
        # We want just the base name "GW Storage"
        component_names_raw = list(f['Layer_1'].keys())

        # Filter out non-data items
        component_names_raw = [c for c in component_names_raw
                               if c not in ['FaceFlows', 'Storage', 'VerticalFlows']]

        # Extract unique base component names
        full_headers = []
        for comp_name in component_names_raw:
            if '_Inflow' in comp_name:
                base_name = comp_name.replace('_Inflow (+)', '').strip()
                if base_name not in full_headers:
                    full_headers.append(base_name)

        # Sort to match expected order (Storage first, then alphabetically)
        priority_order = ['GW Storage', 'Streams', 'Tile Drains', 'Subsidence',
                         'Deep Percolation', 'Constrained General Head BC',
                         'Small Watershed Baseflow', 'Small Watershed Percolation',
                         'Diversion Recoverable Loss', 'Bypass Recoverable Loss',
                         'Pumping by Element', 'Pumping by Well', 'Root Water Uptake']

        # Sort headers by priority, then alphabetically
        sorted_headers = []
        for pheader in priority_order:
            if pheader in full_headers:
                sorted_headers.append(pheader)
                full_headers.remove(pheader)

        # Add remaining headers alphabetically
        sorted_headers.extend(sorted(full_headers))
        full_headers = sorted_headers

        if debug:
            logger.debug(f"Elements: {n_elements=}")
            logger.debug(f"Layers: {n_layers=}")
            logger.debug(f"Time steps: {n_timesteps=}")
            logger.debug(f"Start date: {start_date=}")
            logger.debug(f"Time Unit: {time_unit=}")
            logger.debug(f"Delta t: {delta_t=}")

        # Get element areas (if available)
        zone_areas = defaultdict(float)
        if 'SystemData%ElementAreas' in f['Attributes']:
            elem_areas = f['Attributes/SystemData%ElementAreas'][:] * area_fact
        elif 'Areas' in f['Attributes']:
            elem_areas = f['Attributes/Areas'][:] * area_fact
        else:
            elem_areas = None

        if elem_areas is not None:
            # Calculate zone areas
            for elem_idx in range(n_elements):
                element = elem_idx + 1  # Elements are 1-indexed
                if zextent == 1:
                    zone = element_zones.get(element, -99)
                    if zone != -99:
                        zone_areas[zone] += elem_areas[elem_idx]
                else:
                    # For layer-specific zones, divide area by number of layers
                    for layer in range(1, n_layers + 1):
                        zone = element_zones.get((element, layer), -99)
                        if zone != -99:
                            zone_areas[zone] += elem_areas[elem_idx] / n_layers

        # Get element-to-column mappings for each layer
        # These arrays tell us which column in each component dataset corresponds to each element
        elem_col_maps = {}
        for layer_idx in range(1, n_layers + 1):
            map_name = f'Layer{layer_idx}_ElemDataColumns'
            if map_name in f['Attributes']:
                elem_col_maps[layer_idx] = f[f'Attributes/{map_name}'][:]
            else:
                if verbose:
                    print(f"  Warning: {map_name} not found in attributes")

        # Get component names mapping
        full_comp_names = [n.decode('utf-8').strip() for n in f['Attributes/FullDataNames'][:]]

        if debug:
            logger.debug(f"Component mappings loaded: {len(full_comp_names)} components")

        # Initialize zone data storage
        # zone_data[zone_id][col_idx][in/out] = array of shape (n_timesteps,)
        zone_data = defaultdict(lambda: defaultdict(lambda: {'in': np.zeros(n_timesteps),
                                                             'out': np.zeros(n_timesteps)}))

        # Process data by layer and component
        for layer_idx in range(1, n_layers + 1):
            layer_name = f'Layer_{layer_idx}'

            if layer_name not in f or layer_idx not in elem_col_maps:
                if verbose:
                    print(f"  Warning: {layer_name} or mapping not found")
                continue

            if debug:
                logger.debug(f"Processing {layer_name}...")

            elem_col_map = elem_col_maps[layer_idx]

            # Process each component
            for comp_idx, comp_full_name in enumerate(full_comp_names):
                # Determine if this is inflow or outflow
                is_inflow = '_Inflow' in comp_full_name or '(+)' in comp_full_name
                flow_dir = 'in' if is_inflow else 'out'

                # Get the component base name
                comp_base = comp_full_name.replace('_Inflow (+)', '').replace('_Outflow (-)', '').strip()

                # Find matching header column index
                col_idx = None
                for i, header in enumerate(full_headers):
                    if comp_base == header:
                        col_idx = i
                        break

                if col_idx is None:
                    continue

                # Get data array: shape (n_timesteps, n_data_cols)
                dataset_path = f'{layer_name}/{comp_full_name}'
                if dataset_path not in f:
                    continue

                data_array = f[dataset_path][:]

                # Apply unit conversion (all zone budget values are volumes)
                data_array = data_array * vol_fact

                # Aggregate to zones using the element-to-column mapping
                for elem_idx in range(n_elements):
                    element = elem_idx + 1  # Elements are 1-indexed

                    # Get the column index for this element in this component's dataset
                    data_col = elem_col_map[comp_idx, elem_idx]

                    if data_col == 0:
                        # This element doesn't have data for this component
                        continue

                    # Convert from 1-based to 0-based index
                    data_col_idx = data_col - 1

                    # Determine which zone this element belongs to
                    if zextent == 1:
                        # Same zone for all layers
                        zone = element_zones.get(element, -99)
                    else:
                        # Different zones per layer
                        zone = element_zones.get((element, layer_idx), -99)

                    if zone == -99:
                        continue  # Skip elements not in any zone

                    # Add this element's data to the zone total
                    zone_data[zone][col_idx][flow_dir] += data_array[:, data_col_idx]

        if debug:
            logger.debug(f"Aggregation complete for {len(zone_data)} zones")

    return ZBudgetData(
        zextent=zextent,
        zone_info=zone_info,
        zone_areas=dict(zone_areas),
        full_headers=full_headers,
        zone_data=zone_data,
        n_timesteps=n_timesteps,
        start_date=start_date,
        delta_t=delta_t,
        time_unit=time_unit,
        descriptor=descriptor,
    )
