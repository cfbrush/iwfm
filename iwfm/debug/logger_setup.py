#!/usr/bin/env python
# logger_setup.py
# Setup loguru logger for iwfm package
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

'''Logger_setup.py.

Setup loguru logger for iwfm package.
'''

import sys
from datetime import datetime

try:
    from loguru import logger
    # Replace loguru's verbose default handler with a concise INFO+ handler
    # that is on by default. logger.info/warning/error are visible without
    # any setup; logger.debug only fires once setup_debug_logger() is called.
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<level>{level: <7}</level> | {message}",
    )
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("loguru module not found; falling back to standard logging. Install with: pip install loguru")


def setup_debug_logger(log_prefix=None):
    """
    Configure loguru logger for debug output to timestamped file and console.

    Parameters
    ----------
    log_prefix : str, optional
        Prefix for the log filename (will create <prefix>_YYYYMMDD_HHMMSS.log)
        If None, attempts to use the calling module's name (e.g., "hdf2bud_gw")

    Returns
    -------
    str
        The log filename that was created

    Examples
    --------
    >>> from iwfm.hdf5.logger_setup import setup_debug_logger, logger
    >>> log_file = setup_debug_logger()  # Auto-detects caller name
    >>> logger.debug("This message goes to hdf2xlsx_20260116_143022.log")

    >>> log_file = setup_debug_logger("custom_name")  # Explicit prefix
    >>> logger.debug("This message goes to custom_name_20260116_143022.log")

    Notes
    -----
    This function should be called once at the start of your script when debug
    mode is enabled. It configures both file and console logging.

    The file handler writes detailed logs with timestamps, while the console
    handler uses colored output for better readability.

    When log_prefix is None, the function uses Python's inspect module to
    determine the calling module's filename and uses it as the prefix.
    """
    # Remove default handler
    logger.remove()

    # Determine log prefix if not provided
    if log_prefix is None:
        import inspect
        # Get the caller's frame (2 levels up: this function -> caller)
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            # Get the module name from the caller's globals
            caller_module = caller_frame.f_globals.get('__name__', 'hdf2bud')
            # If it's __main__, try to get the filename
            if caller_module == '__main__':
                import os
                caller_file = caller_frame.f_globals.get('__file__', 'hdf2bud')
                log_prefix = os.path.splitext(os.path.basename(caller_file))[0]
            else:
                # Use the last part of the module name (e.g., iwfm.hdf5.hdf2bud_gw -> hdf2bud_gw)
                log_prefix = caller_module.split('.')[-1]
        else:
            log_prefix = "hdf2bud"

    # Create timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_prefix}_{timestamp}.log"

    # Add file handler with detailed format
    logger.add(
        log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="DEBUG"
    )

    # Also add console output for debug messages
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="DEBUG"
    )

    logger.info(f"Debug logging enabled - writing to {log_filename}")

    return log_filename


def parse_cli_flags():
    """Strip --debug and --quiet flags from sys.argv, enable logging if --debug.

    This utility is designed for __main__ blocks that use sys.argv for positional
    arguments. It removes the flag arguments from sys.argv so existing positional
    argument logic is unchanged.

    Parameters
    ----------
    None

    Returns
    -------
    verbose : bool
        True unless --quiet was passed
    debug : bool
        True if --debug was passed

    Examples
    --------
    >>> # In a __main__ block:
    >>> from iwfm.debug import parse_cli_flags
    >>> verbose, debug = parse_cli_flags()
    """
    debug = '--debug' in sys.argv
    quiet = '--quiet' in sys.argv
    if debug:
        sys.argv.remove('--debug')
        setup_debug_logger()
    if quiet:
        sys.argv.remove('--quiet')
    return not quiet, debug
