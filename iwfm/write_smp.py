# write_smp.py
# Write observed values to a PEST smp file
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

from iwfm.debug.logger_setup import logger


def write_smp(output_filename, lines):
    ''' write_smp() - Write observations to a PEST smp file
        smp format:'   OBSLOCATIONID          MM/DD/YYYY   HH:MM:SS   123.456'

    Parameters
    ----------
    output_filename : str
        name of smp output file

    lines : list
        data as [obslicationid, date, time, value]

    Returns
    -------
    len(lines) : int
        number of items written to the smp file

    '''
    if not output_filename.endswith('.smp'):  # ensure .smp extension
        output_filename = output_filename.rstrip('.') + '.smp'
    try:
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            for i in range(0, len(lines)):
                output_file.write(f'{lines[i][0]}\t{lines[i][1]}\t{lines[i][2]}\t{lines[i][3]}\n')
    except PermissionError:
        logger.error(f'Permission denied writing file: {output_filename}')
        raise
    except OSError as e:
        logger.error(f'OS error writing file {output_filename}: {e}')
        raise
    logger.debug(f'Wrote {len(lines)} lines to {output_filename}')
    return len(lines)
