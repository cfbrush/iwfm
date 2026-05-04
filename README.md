# iwfm

Python functions to work with IWFM-based models

## Overview

The California Department of Water Resources is actively developing the Integrated Water Flow Model for creating integrated hydrologic models.

This repository contains a Python package for working with IWFM model input and output files. Most components work across Windows, Linux, and macOS.

## Version

Initial release: Alpha January 2021. Most recent update: May 2026.

## Installation

Install a version of Python from 3.8 to 3.13 (some dependencies may not have been updated to the latest Python version; the test matrix runs on 3.9).

Download this repository, navigate to the iwfm directory, and install with:

```
python -m pip install -e iwfm
```

The `-e` flag installs in editable mode, useful for development. After install, the `iwfm` console command is on PATH.

### Known installation issues

1. **demjson** — pip may fail building demjson. Roll setuptools back, then forward:
   ```
   pip install setuptools==57.5.0
   pip install demjson
   pip install --upgrade setuptools
   python -m pip install -e iwfm
   ```

2. **leven on Windows ARM** — PyPI lacks a wheel for ARM64. Install Microsoft C++ Build Tools from <https://visualstudio.microsoft.com/visual-cpp-build-tools/> with the "Desktop Development with C++" workload, then:
   ```
   pip install leven
   python -m pip install -e iwfm
   ```

## Usage

### As a Python library

```python
import iwfm

iwfm.hyd_diff(scenario_file_name, base_file_name, diff_file_name)
```

Or import a single function:

```python
from iwfm.hyd_diff import hyd_diff

hyd_diff(scenario_file_name, base_file_name, diff_file_name)
```

### Unified `iwfm` CLI

After installing, the `iwfm` command is on PATH. Five command groups, 41 subcommands:

```
iwfm --help              # top-level help
iwfm calib --help        # PEST/calibration utilities (15 commands)
iwfm hdf5 --help         # HDF5 budget conversion (18 commands)
iwfm gis --help          # GIS utilities (4 commands)
iwfm xls --help          # Excel import/export (2 commands)
iwfm debug --help        # diagnostics (2 commands)
```

Examples:

```
iwfm calib divshort  budget.bud groups.in out.smp
iwfm hdf5  bud-gw    GW_Budget.hdf budget.txt
iwfm hdf5  xlsx-gw   GW_Budget.hdf budget.xlsx
iwfm gis   shp-reproject src.shp tgt.shp --epsg 26910
```

Global flags:
- `--level user|power|dev` controls log verbosity (default `user`).
- `--debug` (per-command, where supported) enables DEBUG-level logging to a timestamped `.log` file.

### Standalone scripts

Many modules also have `if __name__ == "__main__":` blocks for direct invocation:

```
python iwfm/hyd_diff.py scenario.out base.out diff.out
```

These remain supported alongside the unified `iwfm` CLI.

## Logging

The package uses `loguru` (configured at `iwfm/iwfm/debug/logger_setup.py`). By default, `logger.info`, `logger.warning`, and `logger.error` write to stderr. Pass `--debug` (CLI) or call `setup_debug_logger()` (library) to enable DEBUG-level logging to a timestamped file.

## Contributing

Please consider contributing — bug reports, improvements, or new components are all welcome.

Clone the repo, install in editable mode (`pip install -e iwfm`), make changes on a feature branch, and submit a pull request.

### Adding a new function `foo()`

1. Create `iwfm/foo.py` containing the function.
2. Add to `iwfm/__init__.py`:
   ```python
   from iwfm.foo import foo
   ```
3. Add tests in `iwfm/tests/test_foo.py`.

`foo()` is now reachable as `iwfm.foo()`.

## Testing

```
cd iwfm
./run_tests.sh           # comprehensive (per-file + summary logs)
./run_tests_simple.sh    # quick run, single log
```

Current baseline: 355 test files, ~4200 tests, all passing.

## Contact

* Repo owner/admin: cfbrush_AT_gmail_DOT_com or charles_DOT_brush_AT_hydrolytics-llc_DOT_com
