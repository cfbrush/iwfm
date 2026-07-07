# test_iwfm_boundary_coords.py
# Tests for iwfm_boundary_coords function
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

"""
Tests for iwfm.iwfm_boundary_coords function.

The iwfm_boundary_coords function reads node and element files and returns
(x,y) coordinates for the nodes on the bounding polygon of the model.

Example files used for testing:
- Node file: iwfm/tests/C2VSimCG-2021/Preprocessor/C2VSimCG_Nodes.dat
- Element file: iwfm/tests/C2VSimCG-2021/Preprocessor/C2VSimCG_Elements.dat

C2VSimCG model characteristics:
- 1,393 nodes
- 1,392 elements
- Factor: 3.2808 (feet to meters conversion)

Returns:
- boundary_coords: list of (x, y) tuples for nodes on the bounding polygon
"""

import pytest
import os
import sys
import inspect

# Add the iwfm directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from iwfm.iwfm_boundary_coords import iwfm_boundary_coords

# Path to example files
EXAMPLE_NODE_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Preprocessor', 'C2VSimCG_Nodes.dat'
)

EXAMPLE_ELEM_FILE = os.path.join(
    os.path.dirname(__file__),
    'C2VSimCG-2021', 'Preprocessor', 'C2VSimCG_Elements.dat'
)

# Check if example files exist
EXAMPLE_FILES_EXIST = (os.path.exists(EXAMPLE_NODE_FILE) and
                       os.path.exists(EXAMPLE_ELEM_FILE))

# Check if shapely is available (required by get_boundary_coords)
try:
    from shapely.geometry import Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

# Combined check for all dependencies
ALL_DEPS_AVAILABLE = EXAMPLE_FILES_EXIST and SHAPELY_AVAILABLE


class TestIwfmBoundaryCoordsFunctionExists:
    """Test that iwfm_boundary_coords function exists and has correct signature."""

    def test_function_exists(self):
        """Test that iwfm_boundary_coords function is importable."""
        assert iwfm_boundary_coords is not None

    def test_function_is_callable(self):
        """Test that iwfm_boundary_coords is callable."""
        assert callable(iwfm_boundary_coords)

    def test_function_has_docstring(self):
        """Test that iwfm_boundary_coords has a docstring."""
        assert iwfm_boundary_coords.__doc__ is not None
        assert len(iwfm_boundary_coords.__doc__) > 0

    def test_function_signature(self):
        """Test that iwfm_boundary_coords has the expected parameters."""
        sig = inspect.signature(iwfm_boundary_coords)
        params = list(sig.parameters.keys())

        assert 'node_filename' in params
        assert 'elem_filename' in params


@pytest.mark.skipif(not ALL_DEPS_AVAILABLE,
                    reason="shapely or example files not available")
class TestIwfmBoundaryCoordsReturnValue:
    """Test the return value structure of iwfm_boundary_coords."""

    def test_returns_list_or_tuple(self):
        """Test that iwfm_boundary_coords returns a list or tuple."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)
        assert isinstance(result, (list, tuple))

    def test_returns_non_empty(self):
        """Test that result is not empty."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)
        assert len(result) > 0

    def test_returns_coordinate_pairs(self):
        """Test that result contains coordinate pairs."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # Each element should be a coordinate pair (x, y)
        for coord in result[:10]:  # Check first 10
            assert len(coord) >= 2
            # Coordinates should be numeric
            assert isinstance(coord[0], (int, float))
            assert isinstance(coord[1], (int, float))


@pytest.mark.skipif(not ALL_DEPS_AVAILABLE,
                    reason="shapely or example files not available")
class TestIwfmBoundaryCoordsPolygonProperties:
    """Test that the boundary coordinates form a valid polygon."""

    def test_polygon_is_closed(self):
        """Test that the polygon is closed (first point equals last point)."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        first_point = result[0]
        last_point = result[-1]

        # First and last points should be the same (closed polygon)
        assert first_point[0] == pytest.approx(last_point[0], abs=0.001)
        assert first_point[1] == pytest.approx(last_point[1], abs=0.001)

    def test_has_multiple_vertices(self):
        """Test that the polygon has multiple vertices."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # A polygon needs at least 4 points (including closing point)
        assert len(result) >= 4

    def test_creates_valid_shapely_polygon(self):
        """Test that the coordinates can create a valid Shapely polygon."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # Convert to list of tuples for Shapely
        coords = [(c[0], c[1]) for c in result]

        polygon = Polygon(coords)
        assert polygon.is_valid


@pytest.mark.skipif(not ALL_DEPS_AVAILABLE,
                    reason="shapely or example files not available")
class TestIwfmBoundaryCoordsCoordinateValues:
    """Test the coordinate values returned by iwfm_boundary_coords."""

    def test_coordinates_are_positive(self):
        """Test that coordinates are positive (typical for UTM)."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        for coord in result:
            assert coord[0] > 0  # x coordinate
            assert coord[1] > 0  # y coordinate

    def test_coordinates_in_reasonable_range(self):
        """Test that coordinates are in reasonable UTM range for California."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        for coord in result:
            x, y = coord[0], coord[1]
            # UTM range for California Central Valley
            assert 100000 < x < 900000, f"x={x} out of range"
            assert 3500000 < y < 4600000, f"y={y} out of range"

    def test_x_coordinates_have_range(self):
        """Test that x coordinates span a reasonable range (not all same value)."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        x_values = [coord[0] for coord in result]
        x_range = max(x_values) - min(x_values)

        # Model should span at least 10km in x direction
        assert x_range > 10000

    def test_y_coordinates_have_range(self):
        """Test that y coordinates span a reasonable range (not all same value)."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        y_values = [coord[1] for coord in result]
        y_range = max(y_values) - min(y_values)

        # Model should span at least 10km in y direction
        assert y_range > 10000


@pytest.mark.skipif(not ALL_DEPS_AVAILABLE,
                    reason="shapely or example files not available")
class TestIwfmBoundaryCoordsC2VSimCGSpecific:
    """Test C2VSimCG-specific expectations for iwfm_boundary_coords."""

    def test_c2vsimcg_has_many_boundary_nodes(self):
        """Test that C2VSimCG boundary has many nodes."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # C2VSimCG is a large model, boundary should have many points
        # (excluding the closing point which duplicates the first)
        assert len(result) > 50

    def test_c2vsimcg_polygon_area_reasonable(self):
        """Test that C2VSimCG polygon area is reasonable."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # Convert to list of tuples for Shapely
        coords = [(c[0], c[1]) for c in result]

        polygon = Polygon(coords)
        area = polygon.area

        # C2VSimCG covers the Central Valley - should be large area
        # Area in square meters (UTM coordinates)
        assert area > 1e10  # Greater than 10,000 km²

    def test_c2vsimcg_centroid_in_california(self):
        """Test that C2VSimCG centroid is in California."""
        result = iwfm_boundary_coords(EXAMPLE_NODE_FILE, EXAMPLE_ELEM_FILE)

        # Calculate centroid manually
        x_values = [coord[0] for coord in result[:-1]]  # Exclude closing point
        y_values = [coord[1] for coord in result[:-1]]

        centroid_x = sum(x_values) / len(x_values)
        centroid_y = sum(y_values) / len(y_values)

        # Centroid should be in Central Valley region
        assert 400000 < centroid_x < 700000
        assert 3900000 < centroid_y < 4400000


class TestIwfmBoundaryCoordsErrorHandling:
    """Test error handling in iwfm_boundary_coords."""

    def test_nonexistent_node_file_raises_error(self):
        """Test that nonexistent node file raises an error."""
        with pytest.raises(FileNotFoundError):
            iwfm_boundary_coords('/nonexistent/nodes.dat',
                                EXAMPLE_ELEM_FILE if EXAMPLE_FILES_EXIST else '/nonexistent/elem.dat')

    @pytest.mark.skipif(not EXAMPLE_FILES_EXIST,
                        reason="Example files not available")
    def test_nonexistent_elem_file_raises_error(self):
        """Test that nonexistent element file raises an error."""
        with pytest.raises(FileNotFoundError):
            iwfm_boundary_coords(EXAMPLE_NODE_FILE, '/nonexistent/elements.dat')
