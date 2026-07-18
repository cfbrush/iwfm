# histogram_draw.py
# Creates an image from a histogram array
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


'''Create an image from a histogram array.'''

def histogram_draw(hist, scale=True):
    '''Create an image from a histogram array.

    Parameters
    ----------
    hist : numpy array or list
        Histogram array

    scale : bool, default=True
        Whether or not to scale the histogram

    Return
    ------
    t : image object
    '''
    import turtle as t

    t.color('black')
    # Draw the axes
    axes = ((-355, -200), (355, -200), (-355, -200), (-355, 250))
    t.up()
    for p in axes:
        t.goto(p)
        t.down()
    # Labels
    t.up()
    t.goto(0, -250)
    t.write('VALUE', font=('Arial, ', 12, 'bold'))
    t.up()
    t.goto(-400, 280)
    t.write('FREQUENCY', font=('Arial, ', 12, 'bold'))
    # Tick marks
    # x axis
    x = -355
    y = -200
    t.up()
    for i in range(1, 11):
        x = x + 65
        t.goto(x, y)
        t.down()
        t.goto(x, y - 10)
        t.up()
        t.goto(x, y - 25)
        t.write(f'{i * 25}', align='center')
    # y axis
    x = -355
    y = -200
    t.up()
    pixels = sum(hist[0])
    if scale:
        max = 0
        for h in hist:
            hmax = h.max()
            if hmax > max:
                max = hmax
        pixels = max
    label = int(pixels / 10)
    for i in range(1, 11):
        y = y + 45
        t.goto(x, y)
        t.down()
        t.goto(x - 10, y)
        t.up()
        t.goto(x - 15, y - 6)
        t.write(f'{i * label}', align='right')
    # Plot each histogram as a colored line
    x_ratio = 709.0 / 256
    y_ratio = 450.0 / pixels
    # Add more colors to this list if comparing
    # more than 3 bands or 1 image
    colors = ['red', 'green', 'blue']
    for j in range(len(hist)):
        h = hist[j]
        x = -354
        y = -199
        t.up()
        t.goto(x, y)
        t.down()
        t.color(colors[j])
        for i in range(256):
            x = i * x_ratio
            y = h[i] * y_ratio
            x = x - (709 / 2)
            y = y + -199
            t.goto((x, y))
    return t
