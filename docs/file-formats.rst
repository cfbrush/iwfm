IWFM file conventions
=====================

Comment and data lines
----------------------

IWFM input files follow a Fortran-style convention for distinguishing
comments from data:

- **Comment lines** start with ``C``, ``c``, ``*``, or ``#`` in column 1.
- **Data lines** must start with whitespace (or a digit) in column 1, so a
  data value beginning with a comment character is never misread — e.g. a
  filename ``crop_data.dat`` appears as ``  crop_data.dat`` with leading
  spaces.
- ``/`` typically separates the value from a trailing description:
  ``  1387   / NOUTH``.

This convention is implemented in :func:`iwfm.skip_ahead` and used by all
file-reading utilities. When creating test data or example files, always
start data lines with whitespace.

File types
----------

- ``.dat``, ``.in``, ``.out`` — plain text (often very large)
- ``.hdf`` — HDF5 binary (budgets, ZBudgets, head output); read with
  ``h5py`` via the :mod:`iwfm.hdf5` functions
- ``.bud`` — formatted text budget output

Component file versions
-----------------------

Several simulation components are versioned; the version tag is the first
line of the file (e.g. ``#4.2``). 

  The package handles:

- **Groundwater (simulation)**: 4.0 
- **Lakes (simulation)**: 4.0, 5.0
- **Rootzone (simulation)**: 4.0, 4.01, 4.1, 4.11, 4.12, 4.13
- **Streams (preprocessor and simulation)**: 4.0, 4.1, 4.2, 5.0
- **Subsidence (simulation/groundwater)**: 4.0

  Not yet supported:

- **Rootzone (simulation)**: 5.0
- **Subsidence (simulation/groundwater)**: 5.0

Rootzone land use component files are identical across all 4.x versions.
They do not contain version tags; the version is inherited from the main file.

Dates
-----

IWFM uses DSS-style timestamps, e.g. ``09/30/1990_24:00``. Conversion
helpers include :func:`iwfm.date2text`, :func:`iwfm.text_date`,
:func:`iwfm.dss_date`, and :func:`iwfm.generate_timesteps`.


