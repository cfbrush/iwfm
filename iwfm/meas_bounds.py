# meas_bounds.py
# Determine the earliest and latest measurement dates in a SMP observation file
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


def meas_bounds(gwhyd_obs):
    ''' meas_bounds() - Determine the earliest and latest measurement dates
        in a SMP-format groundwater head observation file.

    Parameters
    ----------
    gwhyd_obs : str
        SMP observation file name. Each data line has the form:
            ``<well_name>  <MM/DD/YYYY>  <HH:MM:SS>  <head_obs>``
        e.g. ``11N19W05Q001S  01/28/1987  00:00:00  108.530``.
        Blank lines and lines whose date column does not parse as
        ``MM/DD/YYYY`` are silently skipped.

    Returns
    -------
    earliest : datetime.datetime or None
        Earliest measurement date in the file. ``None`` if the file
        contains no parseable data lines.

    latest : datetime.datetime or None
        Latest measurement date in the file. ``None`` if the file
        contains no parseable data lines.

    Raises
    ------
    SystemExit
        If ``gwhyd_obs`` does not exist (raised via :func:`iwfm.file_test`
        → :func:`iwfm.file_missing`).

    '''
    from datetime import datetime
    import iwfm

    iwfm.file_test(gwhyd_obs)

    earliest = None
    latest = None
    with open(gwhyd_obs) as f:
        for line in f:
            tokens = line.split()
            if len(tokens) < 2:
                continue
            try:
                date = datetime.strptime(tokens[1], '%m/%d/%Y')
            except ValueError:
                continue
            if earliest is None or date < earliest:
                earliest = date
            if latest is None or date > latest:
                latest = date

    return earliest, latest
