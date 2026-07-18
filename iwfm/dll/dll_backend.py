# dll_backend.py
# DLL backend for HDF5 metadata access (deprecated, Windows-only)
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

'''DLL backend for HDF5 metadata access (deprecated, Windows-only).'''

import platform
import warnings
from typing import Tuple, Optional, List

from iwfm.debug.logger_setup import logger

from iwfm.hdf5.hdf_metadata_base import HdfBackend, HdfMetadata
from iwfm.hdf5.hdf_exceptions import BackendNotAvailableError


class DllBackend(HdfBackend):
    """IWFM DLL backend for HDF5 metadata access (deprecated, Windows-only).

    This backend wraps the iwfm.dll module to provide model metadata access
    through the IWFM DLL. It is deprecated in favor of the H5py backend which
    is cross-platform and does not require the DLL.

    .. deprecated::
        Use :func:`iwfm.hdf5.open_hdf` with HDF5 files for cross-platform access.

    Parameters
    ----------
    dll_path : str
        Path to IWFM DLL file
    pre_file : str
        Path to preprocessor file
    sim_file : str
        Path to simulation file
    verbose : bool, optional
        If True, print status messages (default False)

    Raises
    ------
    BackendNotAvailableError
        If platform is not Windows or DLL module cannot be imported
    """

    def __init__(self, dll_path: str, pre_file: str, sim_file: str, verbose: bool = False):
        # Check platform
        if platform.system() != 'Windows':
            logger.error(f"DLL backend requires Windows, current platform: {platform.system()}")
            raise BackendNotAvailableError(
                f"DLL backend is only available on Windows. "
                f"Current platform: {platform.system()}. "
                f"Use iwfm.hdf5.open_hdf() with HDF5 files for cross-platform access."
            )

        # Issue deprecation warning
        warning_msg = (
            "DLL backend is deprecated and will be removed in a future version. "
            "Use iwfm.hdf5.open_hdf() with HDF5 files for cross-platform access. "
            "Example: hdf = iwfm.hdf5.open_hdf(hdf5_file='GW_Budget.hdf')"
        )
        warnings.warn(warning_msg, DeprecationWarning, stacklevel=3)
        logger.warning("DLL backend initialized - deprecated, use H5py backend")

        # Import iwfm.dll module functions
        try:
            from iwfm.dll import (
                dll_init, dll_open, get_nnodes, get_nelem, get_timesteps,
                get_timespecs, get_node_ids, get_elem_ids, get_node_xy, get_elem_nodes
            )
            self._dll_init = dll_init
            self._dll_open = dll_open
            self._get_nnodes = get_nnodes
            self._get_nelem = get_nelem
            self._get_timesteps = get_timesteps
            self._get_timespecs = get_timespecs
            self._get_node_ids = get_node_ids
            self._get_elem_ids = get_elem_ids
            self._get_node_xy = get_node_xy
            self._get_elem_nodes = get_elem_nodes
        except ImportError as e:
            logger.error(f"Failed to import iwfm.dll module: {e}")
            raise BackendNotAvailableError(
                "DLL backend requires iwfm.dll module which could not be imported. "
                "This may indicate the DLL is not available on this system."
            ) from e

        self._dll_path = dll_path
        self._pre_file = pre_file
        self._sim_file = sim_file
        self._verbose = verbose
        self._iwfm_dll = None
        self._metadata_cache = None

        # Initialize DLL
        logger.debug(f"Initializing DLL: {dll_path}")
        logger.debug(f"Preprocessor file: {pre_file}")
        logger.debug(f"Simulation file: {sim_file}")

        try:
            self._iwfm_dll = self._dll_init(dll_path)
            if verbose:
                print(f"Initialized DLL from {dll_path}")
            logger.info(f"DLL initialized from {dll_path}")

            # Open model
            status = self._dll_open(self._iwfm_dll, pre_file, sim_file)
            if verbose:
                print(f"Opened model (status={status})")
            logger.info(f"Model opened with status={status}")

        except Exception as e:
            logger.error(f"Failed to initialize DLL or open model: {e}")
            raise

    def get_n_nodes(self, verbose: bool = False) -> int:
        """Get the number of nodes from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        int
            Number of nodes
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_nnodes")
        n_nodes, status = self._get_nnodes(self._iwfm_dll)
        logger.debug(f"get_nnodes returned: n_nodes={n_nodes}, status={status}")

        if verbose:
            print(f"Retrieved {n_nodes:,} nodes from DLL")

        return n_nodes

    def get_n_elements(self, verbose: bool = False) -> int:
        """Get the number of elements from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        int
            Number of elements
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_nelem")
        n_elem, status = self._get_nelem(self._iwfm_dll)
        logger.debug(f"get_nelem returned: n_elem={n_elem}, status={status}")

        if verbose:
            print(f"Retrieved {n_elem:,} elements from DLL")

        return n_elem

    def get_n_layers(self, verbose: bool = False) -> int:
        """Get the number of groundwater layers.

        This method is not available from the IWFM DLL interface.

        Raises
        ------
        NotImplementedError
            Always raised - DLL backend does not support layer count
        """
        logger.warning("get_n_layers() not available from DLL backend")
        raise NotImplementedError(
            "Layer count not available from DLL backend. "
            "Use H5py backend with zone budget HDF5 file, or read stratigraphy file directly."
        )

    def get_n_timesteps(self, verbose: bool = False) -> int:
        """Get the number of simulation timesteps from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        int
            Number of timesteps
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_timesteps")
        n_timesteps, status = self._get_timesteps(self._iwfm_dll)
        logger.debug(f"get_timesteps returned: n_timesteps={n_timesteps}, status={status}")

        if verbose:
            print(f"Retrieved {n_timesteps:,} timesteps from DLL")

        return n_timesteps

    def get_timestep_info(self, verbose: bool = False) -> Tuple[str, float, str]:
        """Get simulation timestep information from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        start_date : str
            Simulation start date and time
        delta : float
            Length of each timestep (extracted from unit string)
        unit : str
            Unit of timestep (e.g., '1MON', '1DAY')
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_timespecs")
        dates_times, time_step, status = self._get_timespecs(self._iwfm_dll)
        logger.debug(f"get_timespecs returned {len(dates_times)} dates, timestep={time_step}, status={status}")

        start_date = dates_times[0] if dates_times else ""

        # Parse timestep to extract delta and unit
        # DLL returns strings like "1MON", "1DAY", etc.
        time_step = time_step.strip()

        # Try to extract numeric delta (default to 1)
        delta = 1.0
        unit = time_step

        # Simple parsing - extract leading digits
        import re
        match = re.match(r'^(\d+)(.*)$', time_step)
        if match:
            delta = float(match.group(1))
            unit = match.group(2).strip()

        if verbose:
            print(f"Timestep info: start={start_date}, delta={delta}, unit={unit}")

        logger.debug(f"Parsed timestep: start={start_date}, delta={delta}, unit={unit}")

        return start_date, delta, unit

    def get_metadata(self, verbose: bool = False) -> HdfMetadata:
        """Get all available model metadata from IWFM DLL.

        This method caches the metadata after the first read for efficiency.

        Note: Layer count is not available from DLL and will raise NotImplementedError
        if you try to access metadata.n_layers.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        HdfMetadata
            Container with all available metadata (n_layers will be 0)
        """
        verbose = verbose if verbose is not None else self._verbose

        # Return cached metadata if available
        if self._metadata_cache is not None:
            logger.debug("Returning cached metadata")
            if verbose:
                print("Retrieved cached metadata")
            return self._metadata_cache

        logger.info("Loading metadata from DLL")

        # Gather all metadata
        n_nodes = self.get_n_nodes(verbose=False)
        n_elements = self.get_n_elements(verbose=False)
        n_timesteps = self.get_n_timesteps(verbose=False)
        start_date, delta_t, unit = self.get_timestep_info(verbose=False)

        # Note: n_layers not available from DLL - set to 0 as indicator
        n_layers = 0

        logger.debug(
            f"Metadata: nodes={n_nodes}, elements={n_elements}, "
            f"layers={n_layers} (not available), timesteps={n_timesteps}"
        )

        # Create metadata object
        metadata = HdfMetadata(
            n_nodes=n_nodes,
            n_elements=n_elements,
            n_layers=n_layers,  # Not available from DLL
            n_timesteps=n_timesteps,
            start_date=start_date,
            timestep_unit=unit,
            timestep_delta=delta_t,
            node_ids=None,  # Available but not populated by get_metadata
            element_ids=None,  # Available but not populated by get_metadata
            node_coords=None  # Available but not populated by get_metadata
        )

        # Cache for future requests
        self._metadata_cache = metadata
        logger.debug("Cached metadata for future requests")

        if verbose:
            print(f"Loaded metadata: {n_nodes:,} nodes, {n_elements:,} elements, "
                  f"{n_timesteps:,} timesteps (layers not available from DLL)")

        return metadata

    def close(self):
        '''The DLL backend.

        Note: The DLL stays loaded in memory. This is a no-op for compatibility.
        '''
        logger.debug("Close called on DLL backend (no-op, DLL stays loaded)")
        self._metadata_cache = None

    # Optional methods - available from DLL
    def get_node_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Get list of node IDs from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        List[int]
            List of node IDs
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_node_ids")
        node_ids, status = self._get_node_ids(self._iwfm_dll)
        logger.debug(f"get_node_ids returned {len(node_ids)} IDs, status={status}")

        if verbose:
            print(f"Retrieved {len(node_ids):,} node IDs from DLL")

        return node_ids

    def get_element_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Get list of element IDs from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        List[int]
            List of element IDs
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_elem_ids")
        elem_ids, status = self._get_elem_ids(self._iwfm_dll)
        logger.debug(f"get_elem_ids returned {len(elem_ids)} IDs, status={status}")

        if verbose:
            print(f"Retrieved {len(elem_ids):,} element IDs from DLL")

        return elem_ids

    def get_node_coords(self, verbose: bool = False) -> Optional[List[Tuple[float, float]]]:
        """Get node coordinates from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        List[Tuple[float, float]]
            List of (x, y) coordinates for each node
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_node_xy")
        node_coords, status = self._get_node_xy(self._iwfm_dll)
        logger.debug(f"get_node_xy returned {len(node_coords)} coordinates, status={status}")

        if verbose:
            print(f"Retrieved {len(node_coords):,} node coordinates from DLL")

        return node_coords

    def get_element_nodes(self, verbose: bool = False) -> Optional[List[List[int]]]:
        """Get element connectivity (node IDs for each element) from IWFM DLL.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        List[List[int]]
            List of node ID lists for each element
        """
        verbose = verbose if verbose is not None else self._verbose

        logger.debug("Calling DLL function: get_elem_nodes")
        elem_nodes, status = self._get_elem_nodes(self._iwfm_dll)
        logger.debug(f"get_elem_nodes returned {len(elem_nodes)} element connectivity lists, status={status}")

        if verbose:
            print(f"Retrieved connectivity for {len(elem_nodes):,} elements from DLL")

        return elem_nodes
