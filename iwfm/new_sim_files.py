# new_sim_files.py
# Creates and returns a SimulationFiles dataclass of simulation file names from a basename
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

'''Create and return a SimulationFiles dataclass of simulation file names from a basename.'''

from iwfm.iwfm_dataclasses import SimulationFiles


def new_sim_files(out_base_name):
    '''Create and return a SimulationFiles dataclass of simulation file names from a basename.

    Parameters
    ----------
    out_base_name : str
        base name of new simulation input files

    Returns
    -------
    sim_files_new : SimulationFiles
        SimulationFiles dataclass of new simulation input file names
    '''
    return SimulationFiles(
        preout       = out_base_name + '_Preprocessor.bin',
        sim_name     = out_base_name + '_Simulation.in',
        gw_file      = out_base_name + '_Groundwater.dat',
        bc_file      = out_base_name + '_BC.dat',
        spfl_file    = out_base_name + '_SpecifiedFlowBC.dat',
        sphd_file    = out_base_name + '_SpecifiedHeadBC.dat',
        ghd_file     = out_base_name + '_GeneralHeadBC.dat',
        cghd_file    = out_base_name + '_ConstrainedHeadBC.dat',
        tsbc_file    = out_base_name + '_TimeSeriesBC.dat',
        pump_file    = out_base_name + '_Pumping.dat',
        epump_file   = out_base_name + '_ElemPump.dat',
        well_file    = out_base_name + '_WellSpec.dat',
        prate_file   = out_base_name + '_PumpRates.dat',
        sub_file     = out_base_name + '_Subsidence.dat',
        drain_file   = out_base_name + '_TileDrain.dat',
        stream_file  = out_base_name + '_Streams.dat',
        stin_file    = out_base_name + '_StreamInflow.dat',
        divspec_file = out_base_name + '_DiversionSpec.dat',
        bp_file      = out_base_name + '_BypassSpec.dat',
        div_file     = out_base_name + '_Diversions.dat',
        lake_file    = out_base_name + '_Lakes.dat',
        lmax_file    = out_base_name + '_MaxLakeElev.dat',
        root_file    = out_base_name + '_Rootzone.dat',
        np_file      = out_base_name + '_NonPondedCrop.dat',
        pc_file      = out_base_name + '_PondedCrop.dat',
        ur_file      = out_base_name + '_Urban.dat',
        nv_file      = out_base_name + '_NativeVeg.dat',
        nva_file     = out_base_name + '_NativeVeg_Area.dat',
        npa_file     = out_base_name + '_NonPondedCrop_Area.dat',
        pca_file     = out_base_name + '_PondedCrop_Area.dat',
        ura_file     = out_base_name + '_Urban_Area.dat',
        swshed_file  = out_base_name + '_SmallWatersheds.dat',
        unsat_file   = out_base_name + '_Unsat.dat',
    )
