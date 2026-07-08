# test_hdf5_get_zbudget_elemids.py 
# Test hdf5/get_zbudget_elemids function
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
from unittest.mock import Mock

# Check if pywfm is available
try:
    import pywfm  # noqa: F401
    del pywfm
    HAS_PYWFM = True
except ImportError:
    HAS_PYWFM = False


def _zone_file(tmp_path, zextent=1):
    """Write a minimal zone definition file."""
    if zextent == 1:
        content = (
            "C zone definition file\n"
            "     1                / ZEXTENT\n"
            "C   ZID   ZNAME\n"
            "     1    North Zone\n"
            "     2    South Zone\n"
            "C   IE   ZONE\n"
            "     10   1\n"
            "     11   1\n"
            "     20   2\n"
            "     11   1\n"
        )
    else:
        content = (
            "C zone definition file\n"
            "     0                / ZEXTENT\n"
            "C   ZID   ZNAME\n"
            "     1    Zone A\n"
            "C   IE   ZONE   (with layer)\n"
            "     5    1    1\n"
            "     5    2    1\n"
            "     6    1    1\n"
        )
    f = tmp_path / 'zones.dat'
    f.write_text(content)
    return str(f)


def test_get_zbudget_elemids_horizontal_zones(tmp_path):
    """zextent=1: unique sorted element IDs."""
    from iwfm.hdf5.get_zbudget_elemids import get_zbudget_elemids

    result = get_zbudget_elemids(None, _zone_file(tmp_path, zextent=1))

    assert result == [10, 11, 20]


def test_get_zbudget_elemids_layered_zones(tmp_path):
    """zextent=0: element IDs deduplicated across layers."""
    from iwfm.hdf5.get_zbudget_elemids import get_zbudget_elemids

    result = get_zbudget_elemids(None, _zone_file(tmp_path, zextent=0))

    assert result == [5, 6]


def test_get_zbudget_elemids_verbose(tmp_path, capsys):
    """verbose=True prints a summary."""
    from iwfm.hdf5.get_zbudget_elemids import get_zbudget_elemids

    get_zbudget_elemids(None, _zone_file(tmp_path), verbose=True)

    assert 'elements' in capsys.readouterr().out


def test_get_zbudget_elemids_function_signature():
    """Signature retains backward-compatible parameters."""
    import inspect
    from iwfm.hdf5.get_zbudget_elemids import get_zbudget_elemids

    params = list(inspect.signature(get_zbudget_elemids).parameters)
    assert params == ['zbud', 'zones_file', 'area_conversion_factor',
                      'area_units', 'volume_conversion_factor',
                      'volume_units', 'verbose']


def test_get_zbudget_elemids_default_parameters():
    import inspect
    from iwfm.hdf5.get_zbudget_elemids import get_zbudget_elemids

    sig = inspect.signature(get_zbudget_elemids)
    assert sig.parameters['area_conversion_factor'].default == 0.0000229568411
    assert sig.parameters['verbose'].default is False
