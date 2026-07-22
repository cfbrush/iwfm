# Unbuffered.py
# Print unbuffered output to console
# Copyright (C) 2020 University of California
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


'''Print unbuffered output to console.'''

class Unbuffered(object):
    '''Write unbuffered output to console, for example to print progress at runtime without newline characters.

        Example::

            outport = Unbuffered(sys.stdout)
            outport.write(' ' + date)

        From Magnus Lycka Magnus at thinkware.se

    Parameters
    ----------
    object : console object


    '''

    def __init__(self, stream):
        '''Wrap stream so writes are flushed immediately.

        Parameters
        ----------
        stream : file-like object
            stream to wrap, e.g. sys.stdout
        '''
        self.stream = stream

    def write(self, data):
        '''Write data to the wrapped stream and flush immediately.'''
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        '''Write a sequence of lines to the wrapped stream and flush immediately.'''
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
