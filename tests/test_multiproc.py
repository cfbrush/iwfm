#!/usr/bin/env python
# test_multiproc.py
# Unit tests for multiproc.py
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

from iwfm.multiproc import multiproc


def _square(x):
    """Top-level so it's pickleable for mp.Pool."""
    return x * x


def _identity(x):
    return x


class TestMultiproc:
    """multiproc(function, inputlist) — fan a function across CPU cores via
    multiprocessing.Pool.map. Functions must be importable (top-level)."""

    def test_square_inputs(self):
        result = multiproc(_square, [1, 2, 3, 4])
        assert result == [1, 4, 9, 16]

    def test_preserves_input_order(self):
        inputs = [10, 5, 7, 2, 8]
        result = multiproc(_identity, inputs)
        assert result == inputs

    def test_empty_input(self):
        assert multiproc(_square, []) == []

    def test_single_input(self):
        assert multiproc(_square, [3]) == [9]

    def test_returns_list(self):
        result = multiproc(_identity, [1, 2, 3])
        assert isinstance(result, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
