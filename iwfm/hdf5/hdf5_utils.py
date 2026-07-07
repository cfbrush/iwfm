# hdf5_utils.py
# Shared utility functions for h5py-based HDF5 file access
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
from datetime import datetime, timedelta


def apply_unit_conversion(data, col_types, area_fact, vol_fact, len_fact=1.0):
    """Apply unit conversions based on column data types.

    Parameters
    ----------
    data : numpy.ndarray
        2D array of data values (timesteps x columns)
    col_types : array-like
        Array of column type codes. Index 0 is for time column,
        data columns start at index 1.
        Type codes: 1=volume/flow, 2=area, 3=storage, 4=length
    area_fact : float
        Area conversion factor (e.g., 0.0000229568411 for sq ft to acres)
    vol_fact : float
        Volume conversion factor (e.g., 0.0000229568411 for cu ft to acre-ft)
    len_fact : float, default=1.0
        Length conversion factor

    Returns
    -------
    numpy.ndarray
        Converted data array with same shape as input
    """
    result = np.zeros_like(data, dtype=float)

    for col_idx in range(data.shape[1]):
        # col_types[0] is for time, col_types[col_idx+1] is for data column col_idx
        if col_idx + 1 < len(col_types):
            col_type = col_types[col_idx + 1]
            if col_type == 1 or col_type == 3:  # Volume (flow or storage)
                result[:, col_idx] = data[:, col_idx] * vol_fact
            elif col_type == 2:  # Area
                result[:, col_idx] = data[:, col_idx] * area_fact
            elif col_type == 4:  # Length
                result[:, col_idx] = data[:, col_idx] * len_fact
            else:
                # Default to volume conversion for unknown types
                result[:, col_idx] = data[:, col_idx] * vol_fact
        else:
            # If no type specified, assume volume/flow
            result[:, col_idx] = data[:, col_idx] * vol_fact

    return result


def decode_hdf5_string(value):
    """Decode HDF5 string attribute or dataset value.

    Parameters
    ----------
    value : bytes or str
        String value from HDF5 file

    Returns
    -------
    str
        Decoded and stripped string
    """
    if isinstance(value, bytes):
        return value.decode('utf-8').strip()
    return str(value).strip()


def decode_hdf5_strings(values):
    """Decode array of HDF5 string values.

    Parameters
    ----------
    values : array-like
        Array of string values from HDF5 file

    Returns
    -------
    list
        List of decoded and stripped strings
    """
    return [decode_hdf5_string(v) for v in values]


def parse_iwfm_date(date_str):
    """Parse IWFM date string to datetime object.

    Parameters
    ----------
    date_str : str
        Date string in format 'MM/DD/YYYY_HH:MM' or 'MM/DD/YYYY'

    Returns
    -------
    datetime
        Parsed datetime object
    """
    date_str = decode_hdf5_string(date_str)

    # Handle _24:00 format (end of day)
    if '_24:00' in date_str:
        date_part = date_str.replace('_24:00', '')
        dt = datetime.strptime(date_part, '%m/%d/%Y')
        return dt + timedelta(days=1)
    elif '_' in date_str:
        return datetime.strptime(date_str, '%m/%d/%Y_%H:%M')
    else:
        return datetime.strptime(date_str, '%m/%d/%Y')


def format_iwfm_date(dt):
    """Format datetime as IWFM date string.

    Parameters
    ----------
    dt : datetime
        Datetime object

    Returns
    -------
    str
        Formatted date string 'MM/DD/YYYY_24:00'
    """
    return dt.strftime('%m/%d/%Y_24:00')


def generate_timesteps_from_hdf5(start_date_str, n_timesteps, delta_t, time_unit):
    """Generate list of timestep date strings from HDF5 time specification.

    Parameters
    ----------
    start_date_str : str
        Starting date string from HDF5 file
    n_timesteps : int
        Number of timesteps
    delta_t : float
        Time step delta value
    time_unit : str
        Time unit string (e.g., '1MON', 'DAYS', 'MONTH')

    Returns
    -------
    list
        List of date strings for each timestep
    """
    start_dt = parse_iwfm_date(start_date_str)
    time_unit = decode_hdf5_string(time_unit).upper().strip()

    timesteps = [format_iwfm_date(start_dt)]

    current_dt = start_dt
    for _ in range(n_timesteps - 1):
        if 'MON' in time_unit or 'MONTH' in time_unit:
            # Monthly timestep
            month = current_dt.month + int(delta_t)
            year = current_dt.year
            while month > 12:
                month -= 12
                year += 1
            # Get last day of month
            if month == 12:
                next_month_start = datetime(year + 1, 1, 1)
            else:
                next_month_start = datetime(year, month + 1, 1)
            current_dt = next_month_start - timedelta(days=1)
            current_dt = datetime(current_dt.year, current_dt.month, current_dt.day)
        elif 'DAY' in time_unit:
            current_dt = current_dt + timedelta(days=int(delta_t))
        elif 'YEAR' in time_unit:
            current_dt = datetime(current_dt.year + int(delta_t),
                                  current_dt.month, current_dt.day)
        else:
            # Default to days
            current_dt = current_dt + timedelta(days=int(delta_t))

        timesteps.append(format_iwfm_date(current_dt))

    return timesteps


def read_zone_definition(zone_file):
    """Read IWFM zone definition file.

    Parameters
    ----------
    zone_file : str
        Path to zone definition file

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

    # Find ZEXTENT - first non-comment line
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith(('C', 'c', '*', '#')):
            try:
                zextent = int(line.split()[0])
                break
            except ValueError:
                continue

    if zextent is None:
        raise ValueError("Could not find ZEXTENT value in zone definition file")

    # Find zone names section and element assignments
    reading_zones = False
    reading_elements = False

    for line in lines:
        line_strip = line.strip()

        # Skip comments and empty lines, but check for section headers
        if not line_strip or line_strip.startswith(('C', 'c', '*', '#')):
            upper_line = line_strip.upper()
            if 'ZID' in upper_line and 'ZNAME' in upper_line:
                reading_zones = True
                reading_elements = False
                continue
            elif 'IE' in upper_line and 'ZONE' in upper_line:
                reading_zones = False
                reading_elements = True
                continue
            continue

        # Read zone definitions (ZID ZNAME)
        if reading_zones and not reading_elements:
            parts = line_strip.split(None, 1)
            if len(parts) >= 2:
                try:
                    zone_id = int(parts[0])
                    zone_name = parts[1].strip()
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


def get_unit_labels(area_units, volume_units):
    """Get standardized unit labels for output.

    Parameters
    ----------
    area_units : str
        Area unit string
    volume_units : str
        Volume unit string

    Returns
    -------
    tuple
        (area_label, volume_label)
    """
    vol_upper = volume_units.upper()
    if vol_upper in ['ACFT', 'AC-FT', 'ACRE-FT', 'ACRE-FEET']:
        vol_label = 'AC.FT.'
    elif vol_upper in ['AF']:
        vol_label = 'AF'
    else:
        vol_label = vol_upper

    area_upper = area_units.upper()
    if area_upper in ['AC', 'ACRES']:
        area_label = 'AC'
    else:
        area_label = area_upper

    return area_label, vol_label


def substitute_title_placeholders(title, loc_name, area, area_label, vol_label):
    """Substitute placeholders in title string.

    Parameters
    ----------
    title : str
        Title template string
    loc_name : str
        Location name
    area : float
        Area value
    area_label : str
        Area unit label
    vol_label : str
        Volume unit label

    Returns
    -------
    str
        Title with placeholders replaced
    """
    result = title.replace('@LOCNAME@', loc_name)
    result = result.replace('@AREA@', f'{area:,.2f}')
    result = result.replace('@UNITVL@', vol_label)
    result = result.replace('@UNITAR@', area_label)
    return result
