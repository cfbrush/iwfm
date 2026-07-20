# read_obs_smp.py
# Read observations from an smp file (PEST observation file)
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


'''Read the contents of an observed values smp file (PEST observation file) and return as a polars DataFrame or dict.'''

def read_obs_smp(smp_file):
    '''Read the contents of an observed values smp file (PEST observation file) and return as a polars DataFrame or dict.

    Parameters
    ----------
    smp_file : str
        Data file name (PEST-style smp format)
        Format: site_name  MM/DD/YYYY  HH:MM:SS  value

    Returns
    -------
    polars.DataFrame or dict
        If polars is available, returns a sorted DataFrame with columns::

            site_name : str      - observation site identifier
            date      : datetime - observation date
            time      : str      - observation time string (HH:MM:SS)
            obs_value : float    - observed value

        If polars is not available, returns a dict with the same keys,
        each containing a list of values. Sorted by (site_name, date, time).
    '''
    from datetime import datetime

    site_names = []
    dates = []
    times = []
    values = []

    with open(smp_file, encoding='utf-8') as f:
        for line in f:
            line = line.replace("_", " ")
            parts = line.split()
            if len(parts) < 4:
                continue

            try:
                name = parts[0]
                dt = datetime.strptime(parts[1], '%m/%d/%Y')
                tm = parts[2]
                val = float(parts[3])
            except (ValueError, IndexError):
                continue

            site_names.append(name)
            dates.append(dt)
            times.append(tm)
            values.append(val)

    # Try to return polars DataFrame if available, otherwise dict
    try:
        import polars as pl
        df = pl.DataFrame({
            'site_name': site_names,
            'date': dates,
            'time': times,
            'obs_value': values,
        })
        return df.sort(['site_name', 'date', 'time'])
    except ImportError:
        # Sort using indices for dict fallback
        sorted_indices = sorted(
            range(len(site_names)),
            key=lambda i: (site_names[i], dates[i], times[i])
        )
        return {
            'site_name': [site_names[i] for i in sorted_indices],
            'date': [dates[i] for i in sorted_indices],
            'time': [times[i] for i in sorted_indices],
            'obs_value': [values[i] for i in sorted_indices],
        }
