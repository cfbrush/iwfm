# excel_kill.py
# Close Excel application (DEPRECATED)
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

'''Close Excel application.'''

import warnings
from iwfm.debug.logger_setup import logger


def excel_kill(excel):
    """Close Excel application.

    .. deprecated::
        Use :func:`iwfm.xls.close_workbook` instead.

    Parameters
    ----------
    excel : object
        Excel application object.
    """
    warnings.warn(
        "excel_kill() is deprecated. Use close_workbook() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("Deprecated function excel_kill() called - use close_workbook() instead")

    from iwfm.xls import _get_backend_module
    return _get_backend_module().excel_kill(excel)
