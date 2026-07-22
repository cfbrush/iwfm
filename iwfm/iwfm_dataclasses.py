# dataclasses.py
# Dataclass definitions for structured data containers used throughout the iwfm package
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

'''Dataclass definitions for structured data containers used throughout the iwfm package.'''

from dataclasses import dataclass, fields


class _DictAccessMixin:
    """Mixin providing dict-style access for backward compatibility.

    Allows dataclass instances to be accessed with bracket notation
    (obj['field']) in addition to attribute access (obj.field).
    """

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __len__(self):
        return len(fields(self))

    def __iter__(self):
        return (f.name for f in fields(self))

    def get(self, key, default=None):
        """Return field value for key, or default if not found, like dict.get()."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def keys(self):
        """Return field names, like dict.keys()."""
        return [f.name for f in fields(self)]

    def values(self):
        """Return field values, like dict.values()."""
        return [getattr(self, f.name) for f in fields(self)]

    def items(self):
        """Return (name, value) pairs, like dict.items()."""
        return [(f.name, getattr(self, f.name)) for f in fields(self)]


@dataclass
class PreprocessorFiles(_DictAccessMixin):
    """Preprocessor input/output file paths.

    Supports both attribute access (obj.field) and dict-style access
    (obj['field']) for backward compatibility with code that previously
    used plain dicts.

    Attributes
    ----------
    prename : str
        preprocessor input file
    preout : str
        preprocessor output binary file
    elem_file : str
        elements definition file
    node_file : str
        node coordinates file
    strat_file : str
        stratigraphy file
    stream_file : str
        stream specification file
    lake_file : str
        lake specification file (empty string if no lakes)
    """
    prename: str = ''
    preout: str = ''
    elem_file: str = ''
    node_file: str = ''
    strat_file: str = ''
    stream_file: str = ''
    lake_file: str = ''


@dataclass
class SimulationFiles(_DictAccessMixin):
    """Simulation input/output file paths.

    Attributes
    ----------
    preout : str
        preprocessor output binary file
    sim_name : str
        simulation input file
    gw_file : str
        groundwater main file
    bc_file : str
        boundary conditions file
    spfl_file : str
        specified flow BC file
    sphd_file : str
        specified head BC file
    ghd_file : str
        general head BC file
    cghd_file : str
        constrained head BC file
    tsbc_file : str
        time series BC file
    pump_file : str
        pumping file
    epump_file : str
        element pumping file
    well_file : str
        well specification file
    prate_file : str
        pump rates file
    sub_file : str
        subsidence file
    drain_file : str
        tile drain file
    stream_file : str
        streams main file
    stin_file : str
        stream inflow file
    divspec_file : str
        diversion specification file
    bp_file : str
        bypass specification file
    div_file : str
        diversions file
    lake_file : str
        lakes file
    lmax_file : str
        max lake elevation file
    root_file : str
        rootzone main file
    np_file : str
        non-ponded crop file
    pc_file : str
        ponded crop file
    ur_file : str
        urban file
    nv_file : str
        native vegetation file
    nva_file : str
        native vegetation area file
    npa_file : str
        non-ponded crop area file
    pca_file : str
        ponded crop area file
    ura_file : str
        urban area file
    swshed_file : str
        small watersheds file
    unsat_file : str
        unsaturated zone file
    irrfrac : str
        irrigation fractions file
    supplyadj : str
        supply adjustment file
    precip : str
        precipitation file
    et : str
        evapotranspiration file
    start : str
        simulation start date
    step : str
        simulation time step
    end : str
        simulation end date
    """
    preout: str = ''
    sim_name: str = ''
    # groundwater
    gw_file: str = ''
    bc_file: str = ''
    spfl_file: str = ''
    sphd_file: str = ''
    ghd_file: str = ''
    cghd_file: str = ''
    tsbc_file: str = ''
    # pumping
    pump_file: str = ''
    epump_file: str = ''
    well_file: str = ''
    prate_file: str = ''
    # subsidence / drainage
    sub_file: str = ''
    drain_file: str = ''
    # streams
    stream_file: str = ''
    stin_file: str = ''
    divspec_file: str = ''
    bp_file: str = ''
    div_file: str = ''
    # lakes
    lake_file: str = ''
    lmax_file: str = ''
    # root zone
    root_file: str = ''
    np_file: str = ''
    pc_file: str = ''
    ur_file: str = ''
    nv_file: str = ''
    dest_file: str = ''
    nva_file: str = ''
    npa_file: str = ''
    pca_file: str = ''
    ura_file: str = ''
    # other
    swshed_file: str = ''
    unsat_file: str = ''
    irrfrac: str = ''
    supplyadj: str = ''
    precip: str = ''
    et: str = ''
    start: str = ''
    step: str = ''
    end: str = ''


@dataclass
class WellInfo:
    """Hydrograph well information from Groundwater.dat file.

    Attributes
    ----------
    column : int
        column number in hydrograph output file (1-based)
    x : float
        X coordinate (0.0 if HYDTYP=1 node format)
    y : float
        Y coordinate (0.0 if HYDTYP=1 node format)
    layer : int
        aquifer model layer number
    name : str
        well name (lowercase)
    """
    column: int = 0
    x: float = 0.0
    y: float = 0.0
    layer: int = 0
    name: str = ''


@dataclass
class RootzoneFiles(_DictAccessMixin):
    """Root zone component file paths.

    Attributes
    ----------
    np_file : str
        non-ponded agriculture file
    p_file : str
        ponded agriculture file
    ur_file : str
        urban file
    nr_file : str
        native/riparian vegetation file
    rf_file : str
        return flow file
    ru_file : str
        reuse file
    ir_file : str
        irrigation period file
    """
    np_file: str = ''
    p_file: str = ''
    ur_file: str = ''
    nr_file: str = ''
    rf_file: str = ''
    ru_file: str = ''
    ir_file: str = ''


@dataclass
class GroundwaterFiles(_DictAccessMixin):
    """Groundwater component file paths.

    Attributes
    ----------
    bc_file : str
        boundary conditions file
    drain_file : str
        tile drain file
    pump_file : str
        pumping file
    subs_file : str
        subsidence file
    headall : str
        head output file
    """
    bc_file: str = 'none'
    drain_file: str = 'none'
    pump_file: str = 'none'
    subs_file: str = 'none'
    headall: str = 'none'
