# test_calib_fac2iwfm.py
# Unit tests for calib/fac2iwfm.py - Transfer parameter values from pilot points to model nodes
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
import os


class TestFac2Iwfm:
    """Tests for fac2iwfm function"""

    def create_pp_factors_file(self, tmp_path, num_nodes=3, num_ppts=2):
        """Create a mock pilot point factors file.
        
        Format:
        - Line 0: Header/comment
        - Line 1: Number of nodes
        - Line 2: Number of pilot points
        - Lines 3 to (3+num_ppts-1): Pilot point info
        - Lines (3+num_ppts) onwards: Node interpolation factors
          Format: node_id  x  num_alloc  y  pp1  factor1  pp2  factor2 ...
        """
        pp_file = tmp_path / 'pp_factors.dat'
        
        lines = []
        lines.append('# Pilot point factors file')
        lines.append(str(num_nodes))
        lines.append(str(num_ppts))
        
        # Pilot point definitions (num_ppts lines)
        for i in range(num_ppts):
            lines.append(f'PP_{i+1}  {100.0 * (i+1)}  {200.0 * (i+1)}')
        
        # Node interpolation factors
        # Format: node_id  unused  num_allocations  unused  pp_id  factor  [pp_id  factor ...]
        # Node 1: 100% from PP1
        lines.append('1  0.0  1  0.0  1  1.0')
        # Node 2: 50% from PP1, 50% from PP2
        lines.append('2  0.0  2  0.0  1  0.5  2  0.5')
        # Node 3: 100% from PP2
        lines.append('3  0.0  1  0.0  2  1.0')
        
        pp_file.write_text('\n'.join(lines))
        return str(pp_file)

    def create_param_file(self, tmp_path, num_ppts=2, values=None):
        """Create a mock parameter values file.
        
        Format: Each line has pilot point info with value in column 5 (index 4)
        """
        param_file = tmp_path / 'params.dat'
        
        if values is None:
            values = [100.0, 200.0][:num_ppts]
        
        lines = []
        for i, val in enumerate(values):
            # Format: pp_name  x  y  zone  value
            lines.append(f'PP_{i+1}  {100.0*(i+1)}  {200.0*(i+1)}  1  {val}')
        
        param_file.write_text('\n'.join(lines))
        return str(param_file)

    def test_basic_functionality(self, tmp_path):
        """Test basic functionality with simple interpolation."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path, values=[100.0, 200.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        assert os.path.exists(output_file)

    def test_output_file_created(self, tmp_path):
        """Test that output file is created."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path)
        output_file = str(tmp_path / 'result.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_interpolation_single_pp(self, tmp_path):
        """Test interpolation when node uses single pilot point (100% weight)."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path, values=[100.0, 200.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Node 1 should have value 100.0 (100% from PP1)
        assert '100' in lines[0]
        # Node 3 should have value 200.0 (100% from PP2)
        assert '200' in lines[2]

    def test_interpolation_multiple_pp(self, tmp_path):
        """Test interpolation when node uses multiple pilot points."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path, values=[100.0, 200.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Node 2 should have value 150.0 (50% * 100 + 50% * 200)
        assert '150' in lines[1]

    def test_output_format(self, tmp_path):
        """Test that output has correct format: node and value."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            line = f.readline()

        # Format should include 'node:' and 'value:'
        assert 'node:' in line
        assert 'value:' in line

    def test_number_of_output_lines(self, tmp_path):
        """Test that output has one line per node."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path, num_nodes=3)
        param_file = self.create_param_file(tmp_path)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 3

    def test_verbose_output(self, tmp_path, capsys):
        """Test verbose output."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=True)

        captured = capsys.readouterr()
        assert 'FAC2IWFM' in captured.out
        assert 'Read' in captured.out
        assert 'Wrote' in captured.out

    def test_return_value_is_none(self, tmp_path):
        """Test that function returns None (no explicit return)."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = self.create_pp_factors_file(tmp_path)
        param_file = self.create_param_file(tmp_path)
        output_file = str(tmp_path / 'output.dat')

        result = fac2iwfm(pp_file, param_file, output_file, verbose=False)

        assert result is None


class TestFac2IwfmInterpolation:
    """Tests for interpolation calculations."""

    def create_files_with_weights(self, tmp_path, weights, pp_values):
        """Create test files with specific weights and values.
        
        Parameters
        ----------
        weights : list of tuples
            Each tuple is (pp_id, weight) pairs for one node
        pp_values : list
            Parameter values at each pilot point
        """
        num_nodes = len(weights)
        num_ppts = len(pp_values)
        
        # Create PP factors file
        pp_file = tmp_path / 'pp_factors.dat'
        lines = ['# Header', str(num_nodes), str(num_ppts)]
        
        # PP definitions
        for i in range(num_ppts):
            lines.append(f'PP_{i+1}  0.0  0.0')
        
        # Node weights
        for node_idx, node_weights in enumerate(weights):
            node_id = node_idx + 1
            num_alloc = len(node_weights) // 2  # Each allocation is (pp_id, factor)
            weight_str = '  '.join(str(w) for w in node_weights)
            lines.append(f'{node_id}  0.0  {num_alloc}  0.0  {weight_str}')
        
        pp_file.write_text('\n'.join(lines))
        
        # Create param file
        param_file = tmp_path / 'params.dat'
        param_lines = []
        for i, val in enumerate(pp_values):
            param_lines.append(f'PP_{i+1}  0.0  0.0  1  {val}')
        param_file.write_text('\n'.join(param_lines))
        
        return str(pp_file), str(param_file)

    def test_weighted_average_calculation(self, tmp_path):
        """Test weighted average calculation."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        # Node 1: 30% PP1 + 70% PP2
        weights = [(1, 0.3, 2, 0.7)]
        pp_values = [100.0, 200.0]
        
        pp_file, param_file = self.create_files_with_weights(tmp_path, weights, pp_values)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        # Expected: 0.3 * 100 + 0.7 * 200 = 30 + 140 = 170
        assert '170' in content

    def test_three_pilot_points(self, tmp_path):
        """Test interpolation with three pilot points."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        # Node 1: 25% PP1 + 50% PP2 + 25% PP3
        weights = [(1, 0.25, 2, 0.5, 3, 0.25)]
        pp_values = [100.0, 200.0, 300.0]
        
        pp_file, param_file = self.create_files_with_weights(tmp_path, weights, pp_values)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        # Expected: 0.25 * 100 + 0.5 * 200 + 0.25 * 300 = 25 + 100 + 75 = 200
        assert '200' in content

    def test_zero_weight(self, tmp_path):
        """Test with zero weight (pilot point not contributing)."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        # Node 1: 100% PP1 + 0% PP2
        weights = [(1, 1.0, 2, 0.0)]
        pp_values = [100.0, 999.0]  # PP2 should not contribute
        
        pp_file, param_file = self.create_files_with_weights(tmp_path, weights, pp_values)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        # Expected: 1.0 * 100 + 0.0 * 999 = 100
        assert '100' in content
        assert '999' not in content

    def test_fractional_values(self, tmp_path):
        """Test with fractional parameter values."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        weights = [(1, 1.0)]
        pp_values = [123.456]
        
        pp_file, param_file = self.create_files_with_weights(tmp_path, weights, pp_values)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        # Value should be rounded to 3 decimal places
        assert '123.456' in content

    def test_multiple_nodes_different_weights(self, tmp_path):
        """Test multiple nodes with different weight configurations."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        weights = [
            (1, 1.0),           # Node 1: 100% PP1 -> 100
            (2, 1.0),           # Node 2: 100% PP2 -> 200
            (1, 0.5, 2, 0.5),   # Node 3: 50% each -> 150
        ]
        pp_values = [100.0, 200.0]
        
        pp_file, param_file = self.create_files_with_weights(tmp_path, weights, pp_values)
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 3
        assert '100' in lines[0]
        assert '200' in lines[1]
        assert '150' in lines[2]


class TestFac2IwfmEdgeCases:
    """Edge case tests for fac2iwfm."""

    def create_simple_files(self, tmp_path, num_nodes, num_ppts, pp_values):
        """Create simple test files with 100% weight from first PP for each node."""
        pp_file = tmp_path / 'pp.dat'
        lines = ['# Header', str(num_nodes), str(num_ppts)]
        for i in range(num_ppts):
            lines.append(f'PP_{i+1}  0.0  0.0')
        for i in range(num_nodes):
            pp_idx = (i % num_ppts) + 1
            lines.append(f'{i+1}  0.0  1  0.0  {pp_idx}  1.0')
        pp_file.write_text('\n'.join(lines))
        
        param_file = tmp_path / 'param.dat'
        param_lines = []
        for i, val in enumerate(pp_values):
            param_lines.append(f'PP_{i+1}  0.0  0.0  1  {val}')
        param_file.write_text('\n'.join(param_lines))
        
        return str(pp_file), str(param_file)

    def test_single_node(self, tmp_path):
        """Test with single node."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file, param_file = self.create_simple_files(tmp_path, 1, 1, [50.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 1
        assert '50' in lines[0]

    def test_many_nodes(self, tmp_path):
        """Test with many nodes."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file, param_file = self.create_simple_files(tmp_path, 100, 2, [10.0, 20.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 100

    def test_large_values(self, tmp_path):
        """Test with large parameter values."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file, param_file = self.create_simple_files(tmp_path, 1, 1, [999999.999])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        assert '999999.999' in content

    def test_small_values(self, tmp_path):
        """Test with small parameter values."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file, param_file = self.create_simple_files(tmp_path, 1, 1, [0.001])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        assert '0.001' in content

    def test_zero_value(self, tmp_path):
        """Test with zero parameter value."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file, param_file = self.create_simple_files(tmp_path, 1, 1, [0.0])
        output_file = str(tmp_path / 'output.dat')

        fac2iwfm(pp_file, param_file, output_file, verbose=False)

        with open(output_file, 'r') as f:
            content = f.read()

        assert '0' in content


class TestFac2IwfmFileHandling:
    """Tests for file handling."""

    def test_missing_pp_file(self, tmp_path):
        """Test error handling for missing pilot point file."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        pp_file = str(tmp_path / 'nonexistent.dat')
        param_file = str(tmp_path / 'param.dat')
        output_file = str(tmp_path / 'output.dat')
        
        # Create param file only
        (tmp_path / 'param.dat').write_text('PP_1  0.0  0.0  1  100.0')

        with pytest.raises(FileNotFoundError):
            fac2iwfm(pp_file, param_file, output_file, verbose=False)

    def test_missing_param_file(self, tmp_path):
        """Test error handling for missing parameter file."""
        from iwfm.calib.fac2iwfm import fac2iwfm

        # Create minimal PP file
        pp_file = tmp_path / 'pp.dat'
        pp_file.write_text('# Header\n1\n1\nPP_1  0.0  0.0\n1  0.0  1  0.0  1  1.0')
        
        param_file = str(tmp_path / 'nonexistent_param.dat')
        output_file = str(tmp_path / 'output.dat')

        with pytest.raises(FileNotFoundError):
            fac2iwfm(str(pp_file), param_file, output_file, verbose=False)


class TestFac2IwfmImports:
    """Tests for function imports and signature."""

    def test_import_from_calib(self):
        """Test that fac2iwfm can be imported from iwfm.calib."""
        from iwfm.calib import fac2iwfm
        assert callable(fac2iwfm)

    def test_import_directly(self):
        """Test direct import from module."""
        from iwfm.calib.fac2iwfm import fac2iwfm
        assert callable(fac2iwfm)

    def test_function_signature(self):
        """Test function has correct parameters."""
        from iwfm.calib.fac2iwfm import fac2iwfm
        import inspect
        
        sig = inspect.signature(fac2iwfm)
        params = list(sig.parameters.keys())
        
        assert 'pp_file_name' in params
        assert 'param_file_name' in params
        assert 'save_name' in params
        assert 'rlow' in params
        assert 'rhigh' in params
        assert 'empty' in params
        assert 'verbose' in params

    def test_default_parameter_values(self):
        """Test default parameter values."""
        from iwfm.calib.fac2iwfm import fac2iwfm
        import inspect
        
        sig = inspect.signature(fac2iwfm)
        
        assert sig.parameters['rlow'].default == 0.0
        assert sig.parameters['rhigh'].default == 1000000.0
        assert sig.parameters['empty'].default == -999.0
        assert sig.parameters['verbose'].default == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
