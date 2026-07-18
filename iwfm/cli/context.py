# context.py
# iwfm CLI user type
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

'''Iwfm CLI user type.'''

from enum import Enum
import typer


class UserLevel(str, Enum):
    """User level for CLI access control.

    Subclasses ``str`` so that typer's ``case_sensitive=False`` option
    can call ``.casefold()`` on enum members directly.
    """
    USER = "user"
    POWER = "power"
    DEV = "dev"

    def is_user(self) -> bool:
        """Check if this is the basic user level."""
        return self == UserLevel.USER

    def is_power(self) -> bool:
        """Check if this is the power user level."""
        return self == UserLevel.POWER

    def is_dev(self) -> bool:
        """Check if this is the developer level."""
        return self == UserLevel.DEV


def get_user_level() -> UserLevel:
    """Get the current user level from the CLI context."""
    return typer.get_current_context().obj.user_level


def is_power() -> bool:
    """Check if current user level is power."""
    return get_user_level().is_power()


def is_dev() -> bool:
    """Check if current user level is dev."""
    return get_user_level().is_dev()
    
    