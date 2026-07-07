#!/usr/bin/env python
# test_sub_pp_file.py
# Unit tests for sub_pp_file.py
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
from iwfm.iwfm_dataclasses import PreprocessorFiles


def create_pp_file(preout, elem_file, node_file, strat_file, stream_file, lake_file=''):
    """Create a preprocessor input file for testing.

    Parameters
    ----------
    preout : str
        Preprocessor output file path
    elem_file : str
        Element configuration file path
    node_file : str
        Node coordinate file path
    strat_file : str
        Stratigraphy file path
    stream_file : str
        Stream file path
    lake_file : str, optional
        Lake file path (empty string if no lake)

    Returns
    -------
    str
        File contents
    """
    lines = []

    # Header comments
    lines.append("C IWFM Preprocessor Main Input File")
    lines.append("C*******************************************************************************")

    # Title lines (3 data lines before the file names)
    lines.append("                            Historical Simulation")
    lines.append("                         Central Valley, California")
    lines.append("                               C2VSimCG v2025 ")

    # Comment before file names
    lines.append("C File Names Section")
    lines.append("C-----------------------------------------------------------------------------")

    # File names (each preceded by skip_ahead(line_index + 1, pre_lines, 0))
    lines.append(f"    {preout}                          / 1: BINARY OUTPUT FOR SIMULATION")

    lines.append("C Element file")
    lines.append(f"    {elem_file}                       / 2: ELEMENT CONFIGURATION FILE")

    lines.append("C Node file")
    lines.append(f"    {node_file}                       / 3: NODE X-Y COORDINATE FILE")

    lines.append("C Stratigraphy file")
    lines.append(f"    {strat_file}                      / 4: STRATIGRAPHIC DATA FILE")

    lines.append("C Stream file")
    lines.append(f"    {stream_file}                     / 5: STREAM GEOMETRIC DATA FILE")

    lines.append("C Lake file")
    if lake_file:
        lines.append(f"    {lake_file}                       / 6: LAKE DATA FILE")
    else:
        lines.append("                                                     / 6: LAKE DATA FILE")

    return '\n'.join(lines)


class TestSubPpFile:
    """Tests for sub_pp_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_file import sub_pp_file

        pre_files = PreprocessorFiles(lake_file='')
        pre_files_new = PreprocessorFiles(
            prename='new.in', preout='out.bin', elem_file='elem.dat',
            node_file='node.dat', strat_file='strat.dat',
            stream_file='stream.dat', lake_file='',
        )

        with pytest.raises(FileNotFoundError):
            sub_pp_file('nonexistent_file.in', pre_files, pre_files_new)

    def test_basic_file_replacement(self):
        """Test basic file name replacement"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check new file names are in the output
            assert 'new_output.bin' in new_content
            assert 'new_elem.dat' in new_content
            assert 'new_node.dat' in new_content
            assert 'new_strat.dat' in new_content
            assert 'new_stream.dat' in new_content

    def test_with_lake_file(self):
        """Test file replacement when lake file exists"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file='old_lake.dat'
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='old_lake.dat')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='new_lake.dat',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new, has_lake=True)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check lake file is in output
            assert 'new_lake.dat' in new_content

    def test_without_lake_when_original_has_lake(self):
        """Test when original has lake but submodel doesn't"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file='old_lake.dat'
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='old_lake.dat')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            # has_lake=False means the lake file line should be blanked
            sub_pp_file(in_file, pre_files, pre_files_new, has_lake=False)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check lake file is NOT in output (line blanked)
            assert 'new_lake.dat' not in new_content
            assert 'old_lake.dat' not in new_content

    def test_preserves_header_comments(self):
        """Test that header comments are preserved"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            with open(new_file) as f:
                new_content = f.read()

            # Check header is preserved
            assert 'IWFM Preprocessor Main Input File' in new_content

    def test_preserves_titles(self):
        """Test that title lines are preserved"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            with open(new_file) as f:
                new_content = f.read()

            # Check title lines are preserved
            assert 'Historical Simulation' in new_content
            assert 'Central Valley, California' in new_content

    def test_returns_none(self):
        """Test that function returns None"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            result = sub_pp_file(in_file, pre_files, pre_files_new)

            assert result is None

    def test_file_descriptions_preserved(self):
        """Test that file descriptions after / are preserved"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            with open(new_file) as f:
                new_content = f.read()

            # Check descriptions are preserved
            assert 'BINARY OUTPUT FOR SIMULATION' in new_content
            assert 'ELEMENT CONFIGURATION FILE' in new_content
            assert 'NODE X-Y COORDINATE FILE' in new_content
            assert 'STRATIGRAPHIC DATA FILE' in new_content
            assert 'STREAM GEOMETRIC DATA FILE' in new_content
            assert 'LAKE DATA FILE' in new_content

    def test_windows_paths(self):
        """Test handling of Windows-style paths"""
        content = create_pp_file(
            preout='..\\Simulation\\old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='..\\Simulation\\new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check new Windows path is in output
            assert '..\\Simulation\\new_output.bin' in new_content

    def test_old_files_not_in_output(self):
        """Test that old file names are replaced, not present"""
        content = create_pp_file(
            preout='old_output.bin',
            elem_file='old_elem.dat',
            node_file='old_node.dat',
            strat_file='old_strat.dat',
            stream_file='old_stream.dat',
            lake_file=''
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = os.path.join(tmpdir, 'old_pp.in')
            with open(in_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_pp.in')

            pre_files = PreprocessorFiles(lake_file='')
            pre_files_new = PreprocessorFiles(
                prename=new_file,
                preout='new_output.bin',
                elem_file='new_elem.dat',
                node_file='new_node.dat',
                strat_file='new_strat.dat',
                stream_file='new_stream.dat',
                lake_file='',
            )

            from iwfm.sub.pp_file import sub_pp_file

            sub_pp_file(in_file, pre_files, pre_files_new)

            with open(new_file) as f:
                new_content = f.read()

            # Check old file names are NOT in output (except in comments if any)
            # Check specifically in data lines
            lines = new_content.split('\n')
            data_lines = [l for l in lines if not l.startswith('C') and l.strip()]
            data_text = '\n'.join(data_lines)

            assert 'old_output.bin' not in data_text
            assert 'old_elem.dat' not in data_text
            assert 'old_node.dat' not in data_text
            assert 'old_strat.dat' not in data_text
            assert 'old_stream.dat' not in data_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
