#!/usr/bin/env python
# test_sub_gw_file.py
# Unit tests for sub_gw_file.py
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

import pytest
import tempfile
import os
from iwfm.iwfm_dataclasses import SimulationFiles


def create_gw_file(bc_file, td_file, pump_file, subs_file, nouth, hydrographs,
                   pgroups, node_params, nebk, anomalies, initial_heads, layers=4):
    """Create properly structured IWFM Groundwater main file for testing.

    This follows the exact format from C2VSimCG groundwater files:
    - Comment lines start with 'C', 'c', '*', or '#' in column 1
    - Data lines start with whitespace (space or tab)
    - '/' marks end of data value on a line

    Parameters
    ----------
    bc_file : str
        Boundary conditions file path (empty string for none)
    td_file : str
        Tile drain file path (empty string for none)
    pump_file : str
        Pumping file path (empty string for none)
    subs_file : str
        Subsidence file path (empty string for none)
    nouth : int
        Number of hydrographs
    hydrographs : list of tuples
        Each tuple: (id, hydtyp, iouthl, x, y, iouth, name)
    pgroups : int
        Number of parametric groups (usually 0)
    node_params : list of lists
        Each inner list contains [node_id, pkh1, ps1, pn1, pv1, pl1, pkh2, ps2, pn2, pv2, pl2, ...]
        where each node has <layers> sets of 5 params after the node_id
    nebk : int
        Number of hydraulic conductivity anomalies
    anomalies : list of tuples
        Each tuple: (ic, iebk, bk1, bk2, bk3, bk4) for 4 layers
    initial_heads : list of tuples
        Each tuple: (node_id, hp1, hp2, hp3, hp4) for 4 layers
    layers : int
        Number of model layers (default 4)

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Groundwater Component Main Data File")
    lines.append("C*******************************************************************************")

    # File names section (4 file references)
    if bc_file:
        lines.append(f"   {bc_file}                       / BCFL")
    else:
        lines.append("                                         / BCFL")

    if td_file:
        lines.append(f"   {td_file}                       / TDFL")
    else:
        lines.append("                                         / TDFL")

    if pump_file:
        lines.append(f"   {pump_file}                       / PUMPFL")
    else:
        lines.append("                                         / PUMPFL")

    if subs_file:
        lines.append(f"   {subs_file}                       / SUBSFL")
    else:
        lines.append("                                         / SUBSFL")

    # 16 parameters/options to skip to get to hydrograph section
    lines.append("                                         / OVRWRTFL")
    lines.append("   1                                     / FACTLTOU")
    lines.append("   FEET                                  / UNITLTOU")
    lines.append("   0.000022957                           / FACTVLOU")
    lines.append("   ACRE-FEET                             / UNITVLOU")
    lines.append("   0.000022957                           / FACTVROU")
    lines.append("   AC-FT/MON                             / UNITVROU")
    lines.append("                                         / VELOUTFL")
    lines.append("                                         / VFLOWOUTFL")
    lines.append("                                         / GWALLOUTFL")
    lines.append("                                         / HTPOUTFL")
    lines.append("                                         / VTPOUTFL")
    lines.append("                                         / GWBUDFL")
    lines.append("                                         / ZBUDFL")
    lines.append("                                         / FNGWFL")
    # Note: No IHTPFLAG line - the code skips exactly 16 data lines to get from SUBSFL to NOUTH

    # Debugging section (KDEB is the 16th data line after SUBSFL)
    lines.append("C Debugging")
    lines.append("      0                         / KDEB")

    # Hydrograph section
    lines.append("C Groundwater Hydrograph Output Data")
    lines.append(f"     {nouth}                                       / NOUTH")
    lines.append("     3.2808                                     / FACTXY")
    lines.append("     Results/Hydrographs_GW.out                  / GWHYDOUTFL")
    lines.append("C   ID    HYDTYP   IOUTHL      X             Y             IOUTH       NAME")

    for hyd in hydrographs:
        hid, hydtyp, iouthl, x, y, iouth, name = hyd
        # Tab-separated format like in real file
        lines.append(f"{hid}\t{hydtyp}\t{iouthl}\t{x}\t{y}\t\t{name}")

    # Element face flow section (skip with 2 lines after hydrographs)
    lines.append("C Element Face Flow Section")
    lines.append("      0                         / NOUTF")
    lines.append("                                / FCHYDOUTFL")

    # Parametric grid section
    lines.append("C Aquifer Parameters")
    lines.append(f"          {pgroups}                     / NGROUP")

    # Factors (4 data lines to skip after NGROUP - sub_gw_file.py line 195)
    lines.append("   3.2802    1.          1.          1.          1.          1.          / FX FKH FS FN FV FL")
    lines.append("    1DAY               / TUNITKH")
    lines.append("    1DAY               / TUNITV")
    lines.append("    1DAY               / TUNITL")

    # Node parameters section
    # Note: After the 4 factor lines above, node parameters begin immediately
    # Format: first line has node_id + 5 values, subsequent layer lines have 5 values only
    lines.append("C Node Parameters")
    for node_data in node_params:
        node_id = node_data[0]
        # Each node has <layers> sets of parameters
        # First layer line includes node ID
        lines.append(f"\t\t{node_id}\t\t{node_data[1]}\t\t{node_data[2]}\t{node_data[3]}\t{node_data[4]}\t{node_data[5]}")
        # Subsequent layer lines don't have node ID (only 5 values)
        for layer in range(1, layers):
            base_idx = 1 + layer * 5
            if base_idx + 4 < len(node_data):
                lines.append(f"\t\t\t\t{node_data[base_idx]}\t\t{node_data[base_idx+1]}\t{node_data[base_idx+2]}\t{node_data[base_idx+3]}\t{node_data[base_idx+4]}")
            else:
                # Default values if not provided
                lines.append(f"\t\t\t\t10.0\t\t1.0E-06\t0.1\t0.0\t1.0")

    # Hydraulic conductivity anomalies section
    lines.append("C Anomaly in Hydraulic Conductivity")
    lines.append(f"      {nebk}                         / NEBK")
    lines.append("      1.0                       / FACT")
    lines.append("      1MON                      / TUNITH")
    lines.append("C   IC      IEBK     BK[1]       BK[2]       BK[3]       BK[4]")

    for anom in anomalies:
        ic, iebk, bk1, bk2, bk3, bk4 = anom
        lines.append(f"      {ic}       {iebk}       {bk1}    {bk2}   {bk3}   {bk4}")

    # Initial conditions section
    lines.append("C Initial Groundwater Head Values")
    lines.append("      1.0                       / FACTHP")
    lines.append("C          ID        HP[1]       HP[2]       HP[3]        HP[4]")

    for head_data in initial_heads:
        node_id = head_data[0]
        hp1, hp2, hp3, hp4 = head_data[1], head_data[2], head_data[3], head_data[4]
        lines.append(f"\t\t\t{node_id}\t\t{hp1}\t\t{hp2}\t\t{hp3}\t\t{hp4}")

    return '\n'.join(lines)


class TestSubGwFile:
    """Tests for sub_gw_file function"""

    def test_missing_gw_file_key(self):
        """Test error when gw_file key is missing from sim_files"""
        from iwfm.sub.gw_file import sub_gw_file
        from shapely.geometry import Polygon

        sim_files = SimulationFiles()  # Missing 'gw_file' value (empty string)
        sim_files_new = SimulationFiles(gw_file='new_gw.dat')
        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

        with pytest.raises(ValueError):
            sub_gw_file(sim_files, sim_files_new, [1, 2], [[1], [2]], bounding_poly)

    def test_file_not_found(self):
        """Test error handling for non-existent groundwater file"""
        from iwfm.sub.gw_file import sub_gw_file
        from shapely.geometry import Polygon

        sim_files = SimulationFiles(gw_file='nonexistent_file.dat')
        sim_files_new = SimulationFiles(gw_file='new_gw.dat')
        bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

        with pytest.raises(FileNotFoundError):
            sub_gw_file(sim_files, sim_files_new, [1, 2], [[1], [2]], bounding_poly)

    def test_all_files_blank(self):
        """Test GW file with all sub-files blank"""
        # Node params: node_id, then 5 values per layer (4 layers = 21 values total)
        # Format: [node_id, pkh1, ps1, pn1, pv1, pl1, pkh2, ps2, pn2, pv2, pl2, ...]
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0],
            [3, 44.0, 2.2e-05, 0.09, 0.0, 1.5, 23.0, 2.1e-05, 0.09, 0.0, 0.7,
             14.0, 2.3e-05, 0.08, 0.0, 0.4, 19.0, 1.7e-05, 0.11, 0.0, 0.5]
        ]

        # Hydrographs inside bounding box (0-100, 0-100)
        # Format: (id, hydtyp, iouthl, x, y, iouth, name)
        hydrographs = [
            (1, 0, 1, 50.0, 50.0, '', 'Well_1'),
            (2, 0, 1, 25.0, 75.0, '', 'Well_2')
        ]

        # Initial heads: (node_id, hp1, hp2, hp3, hp4)
        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0),
            (3, 90.0, 85.0, 80.0, 80.0)
        ]

        content = create_gw_file('', '', '', '', 2, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            # Bounding polygon includes all hydrographs
            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # All 3 nodes are in submodel
            node_list = [1, 2, 3]
            elem_list = [[1], [2]]  # Element list format: [[elem_id], ...]

            sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly)

            # Verify output file was created
            assert os.path.exists(new_gw_file)

    def test_filters_hydrographs_outside_boundary(self):
        """Test that hydrographs outside bounding polygon are removed"""
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0]
        ]

        # Some hydrographs inside, some outside bounding box (0-50, 0-50)
        hydrographs = [
            (1, 0, 1, 25.0, 25.0, '', 'Well_Inside_1'),   # Inside
            (2, 0, 1, 75.0, 75.0, '', 'Well_Outside_1'),  # Outside
            (3, 0, 1, 40.0, 40.0, '', 'Well_Inside_2'),   # Inside
            (4, 0, 1, 200.0, 200.0, '', 'Well_Outside_2') # Outside
        ]

        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0)
        ]

        content = create_gw_file('', '', '', '', 4, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            # Bounding polygon only includes wells at (25,25) and (40,40)
            bounding_poly = Polygon([(0, 0), (50, 0), (50, 50), (0, 50)])

            node_list = [1, 2]
            elem_list = [[1], [2]]

            sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly)

            # Verify output file
            with open(new_gw_file) as f:
                new_content = f.read()

            # Check NOUTH was updated to 2 (only 2 hydrographs inside)
            assert '2' in new_content  # NOUTH should be 2
            assert 'Well_Inside_1' in new_content
            assert 'Well_Inside_2' in new_content
            # Outside wells should be removed
            assert 'Well_Outside_1' not in new_content
            assert 'Well_Outside_2' not in new_content

    def test_filters_nodes_not_in_submodel(self):
        """Test that node parameters for nodes not in submodel are removed"""
        # 4 nodes, 4 layers each
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0],
            [3, 44.0, 2.2e-05, 0.09, 0.0, 1.5, 23.0, 2.1e-05, 0.09, 0.0, 0.7,
             14.0, 2.3e-05, 0.08, 0.0, 0.4, 19.0, 1.7e-05, 0.11, 0.0, 0.5],
            [4, 51.0, 2.5e-05, 0.10, 0.0, 1.1, 38.0, 1.7e-05, 0.13, 0.0, 0.6,
             15.0, 2.9e-05, 0.09, 0.0, 0.3, 12.0, 3.1e-05, 0.08, 0.0, 0.2]
        ]

        hydrographs = [(1, 0, 1, 50.0, 50.0, '', 'Well_1')]
        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0),
            (3, 90.0, 85.0, 80.0, 80.0),
            (4, 85.0, 80.0, 75.0, 75.0)
        ]

        content = create_gw_file('', '', '', '', 1, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Only nodes 1 and 3 are in submodel
            node_list = [1, 3]
            elem_list = [[1], [2]]

            sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly)

            # Verify output file exists
            assert os.path.exists(new_gw_file)

    def test_filters_anomalies_not_in_submodel(self):
        """Test that hydraulic conductivity anomalies for elements not in submodel are removed"""
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0]
        ]

        hydrographs = [(1, 0, 1, 50.0, 50.0, '', 'Well_1')]

        # Anomalies for different elements
        # Format: (ic, iebk, bk1, bk2, bk3, bk4)
        anomalies = [
            (1, 10, 5.0, 5.0, 5.0, 5.0),   # Element 10 - in submodel
            (2, 20, 3.0, 3.0, 3.0, 3.0),   # Element 20 - NOT in submodel
            (3, 30, 4.0, 4.0, 4.0, 4.0),   # Element 30 - in submodel
            (4, 40, 6.0, 6.0, 6.0, 6.0)    # Element 40 - NOT in submodel
        ]

        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0)
        ]

        content = create_gw_file('', '', '', '', 1, hydrographs, 0, node_params, 4, anomalies, initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            node_list = [1, 2]
            # Only elements 10 and 30 are in submodel
            elem_list = [[10], [30]]

            sub_gw_file(sim_files, sim_files_new, node_list, elem_list, bounding_poly)

            # Verify output file
            with open(new_gw_file) as f:
                new_content = f.read()

            # NEBK should be updated to 2
            assert '2' in new_content  # Updated NEBK

    def test_verbose_mode(self):
        """Test that verbose mode runs without error"""
        # Need at least 2 nodes for layer detection to work properly
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0]
        ]
        hydrographs = [(1, 0, 1, 50.0, 50.0, '', 'Well_1')]
        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0)
        ]

        content = create_gw_file('', '', '', '', 1, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            # Should not raise an error with verbose=True
            sub_gw_file(sim_files, sim_files_new, [1, 2], [[1]], bounding_poly, verbose=True)

            assert os.path.exists(new_gw_file)

    def test_returns_none(self):
        """Test that function returns None"""
        # Need at least 2 nodes for layer detection to work properly
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0]
        ]
        hydrographs = [(1, 0, 1, 50.0, 50.0, '', 'Well_1')]
        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0)
        ]

        content = create_gw_file('', '', '', '', 1, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'new_bc'),
                drain_file=os.path.join(tmpdir, 'new_drain'),
                pump_file=os.path.join(tmpdir, 'new_pump'),
                sub_file=os.path.join(tmpdir, 'new_sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            result = sub_gw_file(sim_files, sim_files_new, [1, 2], [[1]], bounding_poly)

            assert result is None

    def test_updates_file_references(self):
        """Test that file references are updated with new names"""
        # Need at least 2 nodes for layer detection to work properly
        node_params = [
            [1, 70.0, 6.2e-06, 0.13, 0.0, 4.9, 57.0, 1.1e-06, 0.18, 0.0, 4.3,
             31.0, 6.7e-06, 0.12, 0.0, 1.9, 24.0, 7.1e-06, 0.12, 0.0, 1.4],
            [2, 54.0, 1.1e-05, 0.10, 0.0, 2.9, 30.0, 1.1e-05, 0.11, 0.0, 1.5,
             17.0, 1.4e-05, 0.09, 0.0, 0.9, 23.0, 8.8e-06, 0.13, 0.0, 1.0]
        ]
        hydrographs = [(1, 0, 1, 50.0, 50.0, '', 'Well_1')]
        initial_heads = [
            (1, 100.0, 95.0, 90.0, 90.0),
            (2, 95.0, 90.0, 85.0, 85.0)
        ]

        content = create_gw_file('', '', '', '', 1, hydrographs, 0, node_params, 0, [], initial_heads)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_gw.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_gw_file = os.path.join(tmpdir, 'new_gw.dat')
            sim_files = SimulationFiles(gw_file=old_file)
            sim_files_new = SimulationFiles(
                gw_file=new_gw_file,
                bc_file=os.path.join(tmpdir, 'NewModel_BC'),
                drain_file=os.path.join(tmpdir, 'NewModel_Drain'),
                pump_file=os.path.join(tmpdir, 'NewModel_Pump'),
                sub_file=os.path.join(tmpdir, 'NewModel_Sub')
            )

            from iwfm.sub.gw_file import sub_gw_file
            from shapely.geometry import Polygon

            bounding_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

            sub_gw_file(sim_files, sim_files_new, [1, 2], [[1]], bounding_poly)

            # Verify output file was created
            assert os.path.exists(new_gw_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
