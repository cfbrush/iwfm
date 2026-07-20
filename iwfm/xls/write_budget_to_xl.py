# write_budget_to_xl.py
# Write IWFM Budget data to an Excel workbook (DEPRECATED)
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

'''Write IWFM Budget data to an Excel workbook.'''

import warnings
from iwfm.debug.logger_setup import logger


def write_budget_to_xl(wb, budget_data):
    """Write IWFM Budget data to an Excel workbook.

    .. deprecated::
        Use :func:`iwfm.xls.write_budget_data` instead.

    Parameters
    ----------
    wb : object
        Excel workbook object.
    budget_data : list
        List containing [loc_names, column_headers, loc_values, titles].
    """
    warnings.warn(
        "write_budget_to_xl() is deprecated. Use write_budget_data() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("Deprecated function write_budget_to_xl() called - use write_budget_data() instead")

    from iwfm.xls import _get_backend_module
    return _get_backend_module().write_budget_data(wb, budget_data)
