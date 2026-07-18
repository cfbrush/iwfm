# hdf_exceptions.py
# Custom exceptions for the iwfm.hdf5 module
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


'''Custom exceptions for the iwfm.hdf5 module.'''

class HdfError(Exception):
    """Base exception for all HDF5-related errors."""
    pass


class BackendNotAvailableError(HdfError):
    """Raised when a required backend (h5py or DLL) is not available."""
    pass


class DataSourceError(HdfError):
    """Raised when required data is not available from the HDF5 file."""
    pass
