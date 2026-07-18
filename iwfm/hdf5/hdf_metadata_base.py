# hdf_metadata_base.py
# Abstract base classes and data structures for HDF5 metadata access
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

'''Abstract base classes and data structures for HDF5 metadata access.'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class HdfMetadata:
    """Container for IWFM HDF5 file metadata.

    Attributes
    ----------
    n_nodes : int
        Number of nodes in the model mesh
    n_elements : int
        Number of elements in the model mesh
    n_layers : int
        Number of groundwater layers
    n_timesteps : int
        Number of simulation timesteps
    start_date : str
        Simulation start date and time
    timestep_unit : str
        Unit of timestep (e.g., '1MON', '1DAY')
    timestep_delta : float
        Length of each timestep in the specified unit
    node_ids : Optional[List[int]]
        List of node IDs (may not be available from all backends)
    element_ids : Optional[List[int]]
        List of element IDs (may not be available from all backends)
    node_coords : Optional[List[Tuple[float, float]]]
        List of (x, y) coordinates for each node (may not be available)
    """
    n_nodes: int
    n_elements: int
    n_layers: int
    n_timesteps: int
    start_date: str
    timestep_unit: str
    timestep_delta: float
    # Optional - may not be available from all backends/files
    node_ids: Optional[List[int]] = None
    element_ids: Optional[List[int]] = None
    node_coords: Optional[List[Tuple[float, float]]] = None


class HdfBackend(ABC):
    """Abstract base class defining the interface for HDF5 metadata backends.

    All backend implementations must inherit from this class and implement
    all abstract methods. This ensures a consistent interface regardless of
    the underlying data source (HDF5 file via h5py, DLL, etc.).
    """

    @abstractmethod
    def get_n_nodes(self, verbose: bool = False) -> int:
        """Get the number of nodes in the model mesh.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        int
            Number of nodes
        """
        pass

    @abstractmethod
    def get_n_elements(self, verbose: bool = False) -> int:
        """Get the number of elements in the model mesh.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        int
            Number of elements
        """
        pass

    @abstractmethod
    def get_n_layers(self, verbose: bool = False) -> int:
        """Get the number of groundwater layers.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        int
            Number of layers

        Raises
        ------
        NotImplementedError
            If the backend does not support this operation
        """
        pass

    @abstractmethod
    def get_n_timesteps(self, verbose: bool = False) -> int:
        """Get the number of simulation timesteps.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        int
            Number of timesteps
        """
        pass

    @abstractmethod
    def get_timestep_info(self, verbose: bool = False) -> Tuple[str, float, str]:
        """Get simulation timestep information.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        start_date : str
            Simulation start date and time
        delta : float
            Length of each timestep
        unit : str
            Unit of timestep
        """
        pass

    @abstractmethod
    def get_metadata(self, verbose: bool = False) -> HdfMetadata:
        """Get all available model metadata.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        HdfMetadata
            Container with all available metadata
        """
        pass

    @abstractmethod
    def close(self):
        """Release resources held by the backend.

        This should be called when done with the backend, or use the
        backend via a context manager to ensure automatic cleanup.
        """
        pass

    # Optional methods - may return None if not available
    def get_node_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Get list of node IDs.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        Optional[List[int]]
            List of node IDs, or None if not available from this backend
        """
        return None

    def get_element_ids(self, verbose: bool = False) -> Optional[List[int]]:
        """Get list of element IDs.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        Optional[List[int]]
            List of element IDs, or None if not available from this backend
        """
        return None

    def get_node_coords(self, verbose: bool = False) -> Optional[List[Tuple[float, float]]]:
        """Get node coordinates.

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        Optional[List[Tuple[float, float]]]
            List of (x, y) coordinates, or None if not available from this backend
        """
        return None

    def get_element_nodes(self, verbose: bool = False) -> Optional[List[List[int]]]:
        """Get element connectivity (node IDs for each element).

        Parameters
        ----------
        verbose : bool, optional
            If True, print status messages (default False)

        Returns
        -------
        Optional[List[List[int]]]
            List of node ID lists for each element, or None if not available
        """
        return None
