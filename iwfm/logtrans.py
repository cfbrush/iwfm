# logtrans.py
# log-transform a value
# Copyright (C) 2020-2021 University of California
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


def logtrans(q, zero_offset=-2.0, neg_val=1e-9, roundoff=4):
    '''Log-transform a number, accounting for non-zero and negative values.

    Parameters
    ----------
    q : float
        value to be log-transformed

    zero_offset : float, default=-2.0
        value to return if q == 0

    neg_val : float, default=1e-9
        value to return if q < 0

    roundoff : int, default=4
        decimal places to round result

    Returns:
      - the log-transformed value for positive q
      - neg_val for negative q, or
      - zero_offset for q == 0
    '''
    import math

    q = float(q)

    if q == 0:
        outval = zero_offset
    elif q < 0:  # can't log-transform ...
        outval = neg_val  # so set to a very small number
    else:
        outval = round(math.log10(q), roundoff)
    return outval


if __name__ == '__main__':
    ' Run logtrans() from command line '
    import sys
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        q = float(sys.argv[1])
    else:  # ask for file names from terminal
        q = float(input('Value to log-transform: '))

    print(f'  Log-transform of {q} is {logtrans(q)}')
