#!/usr/bin/env python
# test_sub_pp_stream_file.py
# Unit tests for sub_pp_stream_file.py
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


def create_stream_file_42(nrh, nrtb, reaches):
    """Create a stream specification file (version 4.2) for testing.

    Parameters
    ----------
    nrh : int
        Number of stream reaches
    nrtb : int
        Number of data points in rating tables
    reaches : list of tuples
        Each tuple: (reach_id, num_nodes, outflow_node, name, snodes)
        snodes is a list of (stream_node, gw_node) tuples

    Returns
    -------
    str
        File contents

    Note: The function sub_pp_stream_file parses:
    - Line 0: stream type (e.g., "#4.2")
    - skip_ahead(0, ..., 0) to get NRH line
    - Then writes new file using provided data structures
    """
    lines = []

    # Version line (first line, must be exactly "#4.2")
    lines.append("#4.2")

    # Header comments
    lines.append("C IWFM Stream Specification File")
    lines.append("C*******************************************************************************")

    # NRH - number of stream reaches
    lines.append(f"     {nrh}                         / NRH")

    # NRTB - number of points in rating tables
    lines.append(f"     {nrtb}                         / NRTB")

    # Comments before reach data
    lines.append("C Stream Reach Data")

    # Reach data
    for reach in reaches:
        reach_id, num_nodes, outflow_node, name, snodes = reach
        lines.append(f"C     REACH   {reach_id}")
        lines.append("C	Reach	Number	Outflow	Reach")
        lines.append("C	Node	Nodes	Node	Name")
        lines.append("C	ID	NRD	IDWN	NAME")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append(f"	{reach_id}	{num_nodes}	{outflow_node}		{name}")
        lines.append("C-------------------------------------------------------------------------------")
        lines.append("C	Stream	Groundwater")
        lines.append("C    node  node")
        lines.append("C	IRV	IGW")
        lines.append("C-------------------------------------------------------------------------------")
        for sn, gw in snodes:
            lines.append(f"	{sn}	{gw}")
        lines.append("C-------------------------------------------------------------------------------")

    return '\n'.join(lines)


class TestSubPpStreamFile:
    """Tests for sub_pp_stream_file function"""

    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        from iwfm.sub.pp_stream_file import sub_pp_stream_file

        snode_dict = {1: 100, 2: 200}
        reach_info = [(1, 2, 0, 'TestReach', [1, 2])]
        rattab_dict = {1: ['C Rating table for node 1', '	1	100.0	0.0	0	50.0']}
        rating_header = ['C Rating Table Header']
        stream_aq = ['C Stream-Aquifer Section']

        with pytest.raises(FileNotFoundError):
            sub_pp_stream_file('nonexistent_file.dat', 'output.dat',
                              snode_dict, reach_info, rattab_dict,
                              rating_header, stream_aq)

    def test_basic_stream_file_creation(self):
        """Test basic stream file creation with version 4.2"""
        reaches = [
            (1, 3, 0, 'Clear Creek', [(1, 100), (2, 200), (3, 300)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            # Prepare input data structures
            snode_dict = {1: 100, 2: 200, 3: 300}
            reach_info = [(1, 2, 0, 'Clear Creek', [1, 2, 3])]
            rattab_dict = {
                1: ['C Rating table for node 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table for node 2', '\t2\t200.0\t0.0\t0\t60.0'],
                3: ['C Rating table for node 3', '\t3\t300.0\t0.0\t0\t70.0'],
            }
            rating_header = ['C Rating Table Header', 'C NRTB = 10']
            stream_aq = ['C Stream-Aquifer Section', 'C End of file']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            # Check reach info is present
            assert 'Clear Creek' in new_content
            # Check stream nodes are present
            assert '100' in new_content  # gw node for stream node 1
            assert '200' in new_content  # gw node for stream node 2
            # Check rating header is present
            assert 'Rating Table Header' in new_content
            # Check stream-aquifer section is present
            assert 'Stream-Aquifer Section' in new_content

    def test_multiple_reaches(self):
        """Test stream file with multiple reaches"""
        reaches = [
            (1, 2, 17, 'Clear Creek', [(1, 100), (2, 200)]),
            (2, 3, 0, 'Sacramento River', [(17, 300), (18, 400), (19, 500)]),
        ]

        content = create_stream_file_42(2, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200, 17: 300, 18: 400, 19: 500}
            reach_info = [
                (1, 2, 17, 'Clear Creek', [1, 2]),
                (2, 3, 0, 'Sacramento River', [17, 18, 19]),
            ]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
                17: ['C Rating table 17', '\t17\t300.0\t0.0\t0\t70.0'],
                18: ['C Rating table 18', '\t18\t400.0\t0.0\t0\t80.0'],
                19: ['C Rating table 19', '\t19\t500.0\t0.0\t0\t90.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check both reaches are present
            assert 'Clear Creek' in new_content
            assert 'Sacramento River' in new_content
            # Check number of reaches is updated
            assert '2' in new_content.split('\n')[0:10][-1] or \
                   any('2' in line and 'NRH' not in line for line in new_content.split('\n')[:10])

    def test_returns_none(self):
        """Test that function returns None"""
        reaches = [
            (1, 2, 0, 'Test Creek', [(1, 100), (2, 200)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200}
            reach_info = [(1, 2, 0, 'Test Creek', [1, 2])]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = ['C Stream-Aquifer Section']

            result = sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                                       rattab_dict, rating_header, stream_aq)

            assert result is None

    def test_preserves_header_comments(self):
        """Test that header comments from original file are preserved"""
        reaches = [
            (1, 2, 0, 'Test Creek', [(1, 100), (2, 200)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200}
            reach_info = [(1, 2, 0, 'Test Creek', [1, 2])]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check header comments are preserved
            assert 'IWFM Stream Specification File' in new_content

    def test_rating_tables_written(self):
        """Test that rating tables are written to output"""
        reaches = [
            (1, 2, 0, 'Test Creek', [(1, 100), (2, 200)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200}
            reach_info = [(1, 2, 0, 'Test Creek', [1, 2])]
            rattab_dict = {
                1: ['C Rating table for stream node 1', '\t1\t100.0\t0.0\t0\t50.0',
                    '\t\t5.0\t100\t60.0'],
                2: ['C Rating table for stream node 2', '\t2\t200.0\t0.0\t0\t70.0',
                    '\t\t6.0\t150\t80.0'],
            }
            rating_header = ['C Rating Table Header', 'C FACT = 1.0']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check rating tables are written
            assert 'Rating table for stream node 1' in new_content
            assert 'Rating table for stream node 2' in new_content

    def test_stream_aquifer_section_written(self):
        """Test that stream-aquifer section is written to output"""
        reaches = [
            (1, 2, 0, 'Test Creek', [(1, 100), (2, 200)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200}
            reach_info = [(1, 2, 0, 'Test Creek', [1, 2])]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = [
                'C*******************************************************************************',
                'C                    Stream-Aquifer Interaction Data',
                'C   CSTRM;   Coefficient of stream-groundwater interaction',
                '    0.001                         / CSTRM',
            ]

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check stream-aquifer section is written
            assert 'Stream-Aquifer Interaction Data' in new_content
            assert 'CSTRM' in new_content

    def test_single_stream_node(self):
        """Test with single stream node"""
        reaches = [
            (1, 1, 0, 'Small Creek', [(1, 100)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100}
            reach_info = [(1, 1, 0, 'Small Creek', [1])]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            assert os.path.exists(new_file)

            with open(new_file) as f:
                new_content = f.read()

            assert 'Small Creek' in new_content

    def test_reach_outflow_to_another_reach(self):
        """Test reach that flows into another reach (non-zero outflow node)"""
        reaches = [
            (1, 2, 38, 'Upper Creek', [(1, 100), (2, 200)]),
            (2, 2, 0, 'Lower Creek', [(38, 300), (39, 400)]),
        ]

        content = create_stream_file_42(2, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200, 38: 300, 39: 400}
            reach_info = [
                (1, 2, 38, 'Upper Creek', [1, 2]),
                (2, 2, 0, 'Lower Creek', [38, 39]),
            ]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
                38: ['C Rating table 38', '\t38\t300.0\t0.0\t0\t70.0'],
                39: ['C Rating table 39', '\t39\t400.0\t0.0\t0\t80.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check both reaches are present
            assert 'Upper Creek' in new_content
            assert 'Lower Creek' in new_content
            # Check outflow node 38 is written
            assert '38' in new_content

    def _write_version_file(self, tmpdir, version, with_nrtb=True):
        lines = [
            f"#{version}",
            "C IWFM Stream Specification File",
            "     1                         / NRH",
        ]
        if with_nrtb:
            lines.append("     2                         / NRTB")
        old_file = os.path.join(tmpdir, 'old_stream.dat')
        with open(old_file, 'w') as f:
            f.write('\n'.join(lines))
        return old_file

    def test_version_40_writes(self):
        """Test that version 4.0 files are written."""
        from iwfm.sub.pp_stream_file import sub_pp_stream_file

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = self._write_version_file(tmpdir, '4.0')
            new_file = os.path.join(tmpdir, 'new_stream.dat')

            sub_pp_stream_file(old_file, new_file, {1: 100},
                               [[1, 1, 0, 'Test Creek', [1]]],
                               {1: ['\t1\t100.0\t0.0\t0.0', '\t\t2.0\t50.0']},
                               ['C Rating Table Header'], ['C Stream-Aquifer Section'])

            content = open(new_file).read()
            assert 'Test Creek' in content
            assert '100.0' in content

    def test_version_41_writes(self):
        """Test that version 4.1 files (WPTB column) are written."""
        from iwfm.sub.pp_stream_file import sub_pp_stream_file

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = self._write_version_file(tmpdir, '4.1')
            new_file = os.path.join(tmpdir, 'new_stream.dat')

            sub_pp_stream_file(old_file, new_file, {1: 100},
                               [[1, 1, 0, 'Test Creek', [1]]],
                               {1: ['\t1\t100.0\t0.0\t0.0\t1.5', '\t\t2.0\t50.0\t2.5']},
                               ['C Rating Table Header'], ['C Stream-Aquifer Section'])

            content = open(new_file).read()
            assert 'Test Creek' in content
            assert '1.5' in content  # WPTB column preserved

    def test_version_50_writes(self):
        """Test that version 5.0 files (no rating tables) are written."""
        from iwfm.sub.pp_stream_file import sub_pp_stream_file

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = self._write_version_file(tmpdir, '5.0', with_nrtb=False)
            new_file = os.path.join(tmpdir, 'new_stream.dat')

            sub_pp_stream_file(old_file, new_file, {1: 100},
                               [[1, 1, 0, 'Test Creek', [1]]],
                               {}, [], ['     0    / NSTRPINT'])

            content = open(new_file).read()
            assert 'Test Creek' in content
            assert 'NRTB' not in content  # v5.0 has no rating-table count
            assert 'NSTRPINT' in content

    def test_unknown_version_raises(self):
        """Test that an unknown version raises NotImplementedError."""
        from iwfm.sub.pp_stream_file import sub_pp_stream_file

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = self._write_version_file(tmpdir, '3.0')
            new_file = os.path.join(tmpdir, 'new_stream.dat')

            with pytest.raises(NotImplementedError):
                sub_pp_stream_file(old_file, new_file, {1: 100},
                                   [[1, 1, 0, 'Test Creek', [1]]],
                                   {1: ['C Rating table 1']},
                                   ['C Rating Table Header'], ['C Stream-Aquifer Section'])

    def test_empty_stream_aq(self):
        """Test with empty stream-aquifer section"""
        reaches = [
            (1, 2, 0, 'Test Creek', [(1, 100), (2, 200)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100, 2: 200}
            reach_info = [(1, 2, 0, 'Test Creek', [1, 2])]
            rattab_dict = {
                1: ['C Rating table 1', '\t1\t100.0\t0.0\t0\t50.0'],
                2: ['C Rating table 2', '\t2\t200.0\t0.0\t0\t60.0'],
            }
            rating_header = ['C Rating Table Header']
            stream_aq = []  # Empty stream-aquifer section

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            assert os.path.exists(new_file)

    def test_multiple_rating_table_entries(self):
        """Test rating tables with multiple data points"""
        reaches = [
            (1, 1, 0, 'Test Creek', [(1, 100)]),
        ]

        content = create_stream_file_42(1, 10, reaches)

        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = os.path.join(tmpdir, 'old_stream.dat')
            with open(old_file, 'w') as f:
                f.write(content)

            new_file = os.path.join(tmpdir, 'new_stream.dat')

            from iwfm.sub.pp_stream_file import sub_pp_stream_file

            snode_dict = {1: 100}
            reach_info = [(1, 1, 0, 'Test Creek', [1])]
            rattab_dict = {
                1: [
                    'C Rating table for node 1',
                    '\t1\t467.09\t0.00\t0\t350.92',
                    '\t\t5.48\t1500\t350.92',
                    '\t\t7.20\t2793\t368.28',
                    '\t\t8.41\t3923\t379.81',
                    '\t\t11.50\t7603\t408.38',
                    '\t\t14.50\t12236\t444.34',
                    '\t\t18.00\t19404\t499.99',
                    '\t\t25.50\t41512\t671.61',
                    '\t\t33.05\t82158\t987.14',
                    '\t\t42.60\t162287\t1609.17',
                ],
            }
            rating_header = ['C Rating Table Header', 'C FACTRT = 1.0']
            stream_aq = ['C Stream-Aquifer Section']

            sub_pp_stream_file(old_file, new_file, snode_dict, reach_info,
                              rattab_dict, rating_header, stream_aq)

            with open(new_file) as f:
                new_content = f.read()

            # Check rating table data is written
            assert '467.09' in new_content
            assert '162287' in new_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
