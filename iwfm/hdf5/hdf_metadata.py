# hdf_metadata.py
# HDF5 metadata reader using h5py
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

"""
HDF5 metadata access for IWFM output files.

Provides cross-platform access to IWFM model metadata from HDF5 output files
(budget files, zone budget files, etc.) using h5py.

Recommended usage:
    >>> import iwfm.hdf5
    >>> with iwfm.hdf5.open_hdf(hdf5_file='GW_Budget.hdf') as hdf:
    ...     print(f"Nodes: {hdf.get_n_nodes()}")
    ...     print(f"Elements: {hdf.get_n_elements()}")
    ...     meta = hdf.get_metadata()
"""

from typing import Optional, Tuple, List

try:
    import h5py
except ImportError:
    h5py = None

from iwfm.debug.logger_setup import logger

from iwfm.hdf5.hdf_metadata_base import HdfBackend, HdfMetadata
from iwfm.hdf5.hdf_exceptions import BackendNotAvailableError, DataSourceError
from iwfm.hdf5.hdf5_utils import decode_hdf5_string


class HdfReader(HdfBackend):
    """HDF5 file reader for IWFM model metadata using h5py.

    This class reads model metadata from IWFM HDF5 output files
    (budget files, zone budget files, etc.). It provides cross-platform
    access to basic model metadata.

    Parameters
    ----------
    hdf5_file : str
        Path to HDF5 file (budget or zone budget file)
    verbose : bool, optional
        If True, print status messages (default False)

    Raises
    ------
    BackendNotAvailableError
        If h5py is not installed
    FileNotFoundError
        If the HDF5 file does not exist

    Examples
    --------
    >>> with HdfReader('GW_Budget.hdf') as hdf:
    ...     print(f"Nodes: {hdf.get_n_nodes()}")
    ...     print(f"Elements: {hdf.get_n_elements()}")
    """

    def __init__(self, hdf5_file: str, verbose: bool = False):
        if h5py is None:
            logger.error("h5py module not available")
            raise BackendNotAvailableError(
                "HDF5 reader requires h5py module. "
                "Install with: pip install h5py"
            )

        self._hdf5_file = hdf5_file
        self._verbose = verbose
        self._h5file = None
        self._metadata_cache = None

        logger.debug(f"Opening HDF5 file: {hdf5_file}")

        try:
            self._h5file = h5py.File(hdf5_file, 'r')
            if verbose:
                print(f"Opening HDF5 file: {hdf5_file}")
            logger.info(f"Opened HDF5 file: {hdf5_file}")
        except FileNotFoundError:
            logger.error(f"HDF5 file not found: {hdf5_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to open HDF5 file: {e}")
            raise

    def _get_attribute(self, attr_name: str, default=None, required: bool = True):
        """Helper to get an attribute from HDF5 file with error handling.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to retrieve
        default : any, optional
            Default value if attribute not found and not required
        required : bool, optional
            If True, raise error if attribute not found (default True)

        Returns
        -------
        any
            Attribute value

        Raises
        ------
        DataSourceError
            If attribute not found and required=True
        """
        logger.debug(f"Reading attribute: {attr_name}")

        try:
            attrs = self._h5file['Attributes'].attrs
            if attr_name in attrs:
                value = attrs[attr_name]
                logger.debug(f"  {attr_name}={value}")
                return value
            elif not required:
                logger.warning(f"Attribute {attr_name} not found, using default: {default}")
                return default
            else:
                logger.error(f"Required attribute {attr_name} not found")
                raise DataSourceError(
                    f"Required attribute '{attr_name}' not found in HDF5 file. "
                    f"This file may not contain complete model metadata. "
                    f"Try using a zone budget file (*_ZBudget.hdf) which typically has more complete metadata."
                )
        except KeyError as e:
            logger.error("Attributes group not found in HDF5 file")
            raise DataSourceError(
                "HDF5 file does not have an 'Attributes' group. "
                "This may not be a valid IWFM HDF5 file."
            ) from e

    def get_n_nodes(self, verbose: bool = False) -> int:
        """Get the number of nodes from HDF5 file.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        int
            Number of nodes

        Raises
        ------
        DataSourceError
            If node count not available in this HDF5 file
        """
        verbose = verbose if verbose is not None else self._verbose
        n_nodes = self._get_attribute('SystemData%NNodes', required=True)

        if verbose:
            print(f"Retrieved {n_nodes:,} nodes")

        return int(n_nodes)

    def get_n_elements(self, verbose: bool = False) -> int:
        """Get the number of elements from HDF5 file.

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

        # Try SystemData%NElements first, then fall back to nLocations
        try:
            n_elements = self._get_attribute('SystemData%NElements', required=True)
        except DataSourceError:
            logger.debug("SystemData%NElements not found, trying nLocations")
            n_elements = self._get_attribute('nLocations', required=True)

        if verbose:
            print(f"Retrieved {n_elements:,} elements")

        return int(n_elements)

    def get_n_layers(self, verbose: bool = False) -> int:
        """Get the number of groundwater layers from HDF5 file.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        int
            Number of layers (defaults to 1 if not available)
        """
        verbose = verbose if verbose is not None else self._verbose

        # Try SystemData%NLayers first, then NLayers, default to 1
        try:
            n_layers = self._get_attribute('SystemData%NLayers', default=None, required=False)
            if n_layers is None:
                n_layers = self._get_attribute('NLayers', default=1, required=False)
        except DataSourceError:
            logger.warning("Layer count not available, defaulting to 1")
            n_layers = 1

        if verbose:
            print(f"Retrieved {n_layers} layer(s)")

        return int(n_layers)

    def get_n_timesteps(self, verbose: bool = False) -> int:
        """Get the number of simulation timesteps from HDF5 file.

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
        n_timesteps = self._get_attribute('NTimeSteps', required=True)

        if verbose:
            print(f"Retrieved {n_timesteps:,} timesteps")

        return int(n_timesteps)

    def get_timestep_info(self, verbose: bool = False) -> Tuple[str, float, str]:
        """Get simulation timestep information from HDF5 file.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        start_date : str
            Simulation start date and time (e.g., '10/31/1973_24:00')
        delta : float
            Length of each timestep
        unit : str
            Unit of timestep (e.g., '1MON', '1DAY')
        """
        verbose = verbose if verbose is not None else self._verbose

        start_date_raw = self._get_attribute('TimeStep%BeginDateAndTime', required=True)
        start_date = decode_hdf5_string(start_date_raw)

        delta_t = self._get_attribute('TimeStep%DeltaT', required=True)

        unit_raw = self._get_attribute('TimeStep%Unit', required=True)
        unit = decode_hdf5_string(unit_raw)

        if verbose:
            print(f"Timestep info: start={start_date}, delta={delta_t}, unit={unit}")

        return start_date, float(delta_t), unit

    def get_metadata(self, verbose: bool = False) -> HdfMetadata:
        """Get all available model metadata from HDF5 file.

        This method caches the metadata after the first read for efficiency.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default uses instance setting)

        Returns
        -------
        HdfMetadata
            Container with all available metadata
        """
        verbose = verbose if verbose is not None else self._verbose

        # Return cached metadata if available
        if self._metadata_cache is not None:
            logger.debug("Returning cached metadata")
            if verbose:
                print("Retrieved cached metadata")
            return self._metadata_cache

        logger.info("Loading metadata from HDF5 file")

        # Gather all metadata
        n_nodes = self.get_n_nodes(verbose=False)
        n_elements = self.get_n_elements(verbose=False)
        n_layers = self.get_n_layers(verbose=False)
        n_timesteps = self.get_n_timesteps(verbose=False)
        start_date, delta_t, unit = self.get_timestep_info(verbose=False)

        logger.debug(
            f"Metadata: nodes={n_nodes}, elements={n_elements}, "
            f"layers={n_layers}, timesteps={n_timesteps}"
        )

        # Create metadata object (optional fields are None for HDF5 backend)
        metadata = HdfMetadata(
            n_nodes=n_nodes,
            n_elements=n_elements,
            n_layers=n_layers,
            n_timesteps=n_timesteps,
            start_date=start_date,
            timestep_unit=unit,
            timestep_delta=delta_t,
            node_ids=None,
            element_ids=None,
            node_coords=None
        )

        # Cache for future requests
        self._metadata_cache = metadata
        logger.debug("Cached metadata for future requests")

        if verbose:
            print(f"Loaded metadata: {n_nodes:,} nodes, {n_elements:,} elements, "
                  f"{n_layers} layer(s), {n_timesteps:,} timesteps")

        return metadata

    def close(self):
        '''The HDF5 file and release resources.'''
        if self._h5file is not None:
            logger.info(f"Closing HDF5 file: {self._hdf5_file}")
            self._h5file.close()
            self._h5file = None
            self._metadata_cache = None

    def __enter__(self):
        """Support context manager protocol."""
        logger.debug("Entering HdfReader context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol."""
        logger.debug("Exiting HdfReader context manager, closing file")
        self.close()
        return False

    # Optional methods - return None for HDF5 reader
    def get_node_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Not available from HDF5 files - use preprocessor files instead.

        Returns None. To get node IDs, read from the preprocessor node file
        using iwfm.iwfm_read_nodes().
        """
        logger.debug("get_node_ids() not supported by HDF5 reader, returning None")
        if verbose:
            print("Node IDs not available from HDF5 files - read from preprocessor node file")
        return None

    def get_element_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Not available from HDF5 files - use preprocessor files instead.

        Returns None. To get element IDs, read from the preprocessor element file
        using iwfm.iwfm_read_elements().
        """
        logger.debug("get_element_ids() not supported by HDF5 reader, returning None")
        if verbose:
            print("Element IDs not available from HDF5 files - read from preprocessor element file")
        return None

    def get_node_coords(self, verbose: bool = False) -> Optional[List[Tuple[float, float]]]:
        """Not available from HDF5 files - use preprocessor files instead.

        Returns None. To get node coordinates, read from the preprocessor node file
        using iwfm.iwfm_read_nodes().
        """
        logger.debug("get_node_coords() not supported by HDF5 reader, returning None")
        if verbose:
            print("Node coordinates not available from HDF5 files - read from preprocessor node file")
        return None

    def get_element_nodes(self, verbose: bool = False) -> Optional[List[List[int]]]:
        """Not available from HDF5 files - use preprocessor files instead.

        Returns None. To get element connectivity, read from the preprocessor element file
        using iwfm.iwfm_read_elements().
        """
        logger.debug("get_element_nodes() not supported by HDF5 reader, returning None")
        if verbose:
            print("Element connectivity not available from HDF5 files - read from preprocessor element file")
        return None


# -----------------------------------------------------------------------------
# Factory Function
# -----------------------------------------------------------------------------

def open_hdf(hdf5_file: str, verbose: bool = False) -> HdfReader:
    """Open an IWFM HDF5 output file for metadata access.

    Parameters
    ----------
    hdf5_file : str
        Path to HDF5 file (budget or zone budget file)
    verbose : bool, optional
        If True, print status messages (default False)

    Returns
    -------
    HdfReader
        HDF5 reader instance for metadata access

    Raises
    ------
    BackendNotAvailableError
        If h5py is not available
    FileNotFoundError
        If the HDF5 file does not exist

    Examples
    --------
    Using context manager (recommended):

    >>> import iwfm.hdf5
    >>> with iwfm.hdf5.open_hdf('GW_Budget.hdf') as hdf:
    ...     print(f"Nodes: {hdf.get_n_nodes()}")
    ...     print(f"Elements: {hdf.get_n_elements()}")

    Without context manager:

    >>> hdf = iwfm.hdf5.open_hdf('GW_Budget.hdf')
    >>> n_nodes = hdf.get_n_nodes()
    >>> hdf.close()
    """
    logger.debug(f"open_hdf() called with hdf5_file={hdf5_file}")

    if verbose:
        print(f"Opening HDF5 file: {hdf5_file}")
    logger.info(f"Opening HDF5 file via open_hdf(): {hdf5_file}")

    return HdfReader(hdf5_file, verbose=verbose)


# -----------------------------------------------------------------------------
# Public API Exports
# -----------------------------------------------------------------------------

__all__ = [
    'HdfReader',
    'open_hdf',
    'HdfMetadata',
    'HdfBackend',
]
