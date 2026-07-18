# __init__.py for iwfm.dll package
# Classes, methods and functions to interface with the IWFM DLL
# Copyright (C) 2021-2026 University of California
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

'''Classes, methods and functions to interface with the IWFM DLL.'''

import warnings

warnings.warn(
    "The iwfm.dll module is deprecated and will be removed in a future version. "
    "Use iwfm.hdf5.open_hdf() with HDF5 files for cross-platform access. "
    "Example: hdf = iwfm.hdf5.open_hdf(hdf5_file='GW_Budget.hdf')",
    DeprecationWarning,
    stacklevel=2
)

# -- IWFM DLL methods -------------------------------------
from iwfm.dll.dll_init import dll_init
from iwfm.dll.seek_proc import seek_proc
from iwfm.dll.dll_open import dll_open
from iwfm.dll.date_time import date_time
from iwfm.dll.get_timesteps import get_timesteps
from iwfm.dll.get_timespecs import get_timespecs
from iwfm.dll.get_nnodes import get_nnodes
from iwfm.dll.get_node_ids import get_node_ids
from iwfm.dll.get_node_xy import get_node_xy
from iwfm.dll.get_nelem import get_nelem
from iwfm.dll.get_elem_ids import get_elem_ids
from iwfm.dll.get_elem_nodes import get_elem_nodes

# -- DLL Backend for HDF5 metadata access (deprecated) ----
from iwfm.dll.dll_backend import DllBackend
