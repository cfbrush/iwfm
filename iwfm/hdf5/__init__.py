# __init__.py for iwfm.hdf5 package
# Classes, methods and functions to read, write and modify IWFM HDF5 output files
# Uses h5py for cross-platform HDF5 access (Unix/Linux/macOS/Windows)
# pywfm fallback is DEPRECATED and will be removed in a future version
# Copyright (C) 2018-2026 University of California
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

'''Classes, methods and functions to read, write and modify IWFM HDF5 output files.

Uses h5py for cross-platform HDF5 access (Unix/Linux/macOS/Windows). The
pywfm fallback is DEPRECATED and will be removed in a future version.
'''

import warnings

# -- HDF5 metadata access ---------------------------------
from iwfm.hdf5.hdf_metadata import HdfReader, open_hdf
from iwfm.hdf5.hdf_metadata_base import HdfMetadata, HdfBackend
from iwfm.hdf5.hdf_exceptions import HdfError, BackendNotAvailableError, DataSourceError

# -- general methods --------------------------------------
from iwfm.hdf5.read_hdf5 import read_hdf5

# -- budget data methods (h5py required, pywfm fallback DEPRECATED) -
try:
    from iwfm.hdf5.get_budget_data_h5 import get_budget_data
except ImportError:
    warnings.warn(
        "h5py not available, falling back to deprecated pywfm implementation. "
        "Install h5py for cross-platform support: pip install h5py",
        DeprecationWarning
    )
    from iwfm.hdf5.get_budget_data_pywfm import get_budget_data

try:
    from iwfm.hdf5.get_zbudget_data_h5 import get_zbudget_data
except ImportError:
    warnings.warn(
        "h5py not available, falling back to deprecated pywfm implementation. "
        "Install h5py for cross-platform support: pip install h5py",
        DeprecationWarning
    )
    from iwfm.hdf5.get_zbudget_data_pywfm import get_zbudget_data

try:
    from iwfm.hdf5.get_zbudget_elem_vals_h5 import get_zbudget_elem_vals
except ImportError:
    warnings.warn(
        "h5py not available, falling back to deprecated pywfm implementation. "
        "Install h5py for cross-platform support: pip install h5py",
        DeprecationWarning
    )
    from iwfm.hdf5.get_zbudget_elem_vals_pywfm import get_zbudget_elem_vals

# -- utility functions ------------------------------------
from iwfm.hdf5.hdf5_utils import (
    apply_unit_conversion,
    decode_hdf5_string,
    decode_hdf5_strings,
    generate_timesteps_from_hdf5,
    read_zone_definition,
    get_unit_labels,
    substitute_title_placeholders,
)

# -- CSV export methods -----------------------------------
from iwfm.hdf5.hdfbud2csv import hdfbud2csv
from iwfm.hdf5.cropbud2csv import cropbud2csv

# -- HDF to text budget methods ---------------------------
from iwfm.hdf5.hdf2bud_diversions import hdf2bud_diversions
from iwfm.hdf5.hdf2bud_gw import hdf2bud_gw
from iwfm.hdf5.hdf2bud_lw import hdf2bud_lw
from iwfm.hdf5.hdf2bud_rz import hdf2bud_rz
from iwfm.hdf5.hdf2bud_stream import hdf2bud_stream
from iwfm.hdf5.hdf2bud_swat import hdf2bud_swat
from iwfm.hdf5.hdf2bud_unsat import hdf2bud_unsat

# -- HDF to Excel methods ---------------------------------
from iwfm.hdf5.hdf2xlsx_diversions import hdf2xlsx_diversions
from iwfm.hdf5.hdf2xlsx_gw import hdf2xlsx_gw
from iwfm.hdf5.hdf2xlsx_lw import hdf2xlsx_lw
from iwfm.hdf5.hdf2xlsx_rz import hdf2xlsx_rz
from iwfm.hdf5.hdf2xlsx_stream import hdf2xlsx_stream
from iwfm.hdf5.hdf2xlsx_swat import hdf2xlsx_swat
from iwfm.hdf5.hdf2xlsx_unsat import hdf2xlsx_unsat

# -- Zone budget methods ----------------------------------
from iwfm.hdf5.zbud_gw_core import zbud_gw_aggregate, ZBudgetData
from iwfm.hdf5.hdf2zbud_gw import hdf2zbud_gw
from iwfm.hdf5.hdf2zxlsx_gw import hdf2zxlsx_gw

# -- print methods (for debugging) ------------------------
from iwfm.hdf5.print_methods_hdf import print_methods_hdf
