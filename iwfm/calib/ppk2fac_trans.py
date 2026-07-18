# ppk2fac_trans.py
# The ppk2fac file requires sequential model node numbers. This script
# replaces the sequential model node numbers with the actual node numbers.
# Copyright (C) 2020-2023 University of California
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

def ppk2fac_trans(factors_file, trans_file, out_file, verbose=False):
    '''Convert the ppk2fac file to the fac2fac file.

    Parameters
    ----------
    factors_file: str
        Name of factors file from ppk2fac

    trans_file: str
        Name of file containing the translation from sequential to actual node

    out_file: str
        Name of output file

    verbose: bool
        If True, prints out the translation

    Returns
    -------
    None
    '''
    with open(factors_file, 'r', encoding='utf-8') as f:
        factor_lines = []
        for line in f:
            if line.startswith('#') or line.startswith('C'):
                continue
            else:
                line = line[:-1]    # remove newline
                factor_lines.append(line)
    if verbose:
        print(f'  Read {len(factor_lines):,} pilot points from {factors_file}')

    with open(trans_file, 'r', encoding='utf-8') as f:
        trans_d = {}
        for line in f:
            if line.startswith('#') or line.startswith('C'):
                continue
            else:
                line = line.strip().split()
                trans_d[line[0]] = line[1]
    if verbose:
        print(f'  Read {len(trans_d):,} pilot points from {trans_file}')

    num_params = int(factor_lines[2].split()[0])

    # skip parameter lines
    i = 3 + num_params 

    while i < len(factor_lines):
        this_node = factor_lines[i].split()[0]
        new_node = trans_d[this_node]
        factor_lines[i] = factor_lines[i].replace(this_node, new_node)
        # skip three lines
        i += 3

    with open(out_file, 'w', encoding='utf-8') as f:
        for line in factor_lines:
            f.write(line + '\n')
    if verbose:
        print(f'  Wrote {len(factor_lines):,} lines to {out_file}')


if __name__ == '__main__':
    ''' Run ppk2fac_trans() from command line '''

    import sys
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    if len(sys.argv) > 1:  # arguments are listed on the command line
        factors_file  = sys.argv[1]
        trans_file    = sys.argv[2]
        out_file      = sys.argv[3]
    else:  # ask for file names from terminal
        factors_file  = input('PPK2FAC Factors file name: ')
        trans_file    = input('Factor to Nods file name: ')
        out_file      = input('Output file name: ')

    iwfm.file_test(factors_file)
    iwfm.file_test(trans_file)

    ppk2fac_trans(factors_file, trans_file, out_file)
