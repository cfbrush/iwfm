#!/usr/bin/env python
# 07_logging.py
# Configure loguru logging in an iwfm script
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
07_logging.py — Configure loguru logging in an iwfm script.

Usage:
    python 07_logging.py
    python 07_logging.py --debug    # enable DEBUG-level + log file

Default: INFO/WARNING/ERROR visible on stderr, DEBUG silent.
After setup_debug_logger(): DEBUG visible on stderr AND written to a
timestamped log file (e.g. `07_logging_20260504_120000.log`).
"""
from __future__ import annotations

import sys

from iwfm.debug.logger_setup import logger, setup_debug_logger


def do_work() -> None:
    logger.debug("debug-only details: parsing 42 rows")
    logger.info("ran cleanly")
    logger.warning("something might be off")
    logger.error("simulated error condition")


def main(debug: bool) -> None:
    if debug:
        log_file = setup_debug_logger('07_logging')
        logger.info(f"debug mode: tee to {log_file}")
    do_work()


if __name__ == "__main__":
    main(debug='--debug' in sys.argv)
