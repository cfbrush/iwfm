API reference
=============

The top-level :mod:`iwfm` package exports all core functions. Subpackages
group specialized functionality:

============================  ==================================================
Package                       Contents
============================  ==================================================
:mod:`iwfm`                   core file readers/writers, dates, land use,
                              budgets, submodel extraction
``iwfm.gis``                  shapefiles, coordinate conversion, mapping
``iwfm.calib``                calibration statistics and PEST utilities
``iwfm.hdf5``                 HDF5 budget/ZBudget processing
``iwfm.sub``                  submodel component-file extraction
``iwfm.plot``                 plotting utilities
``iwfm.xls``                  Excel output
``iwfm.util``                 download external data (CDEC, NWIS, USACE, USBR)
``iwfm.dll``                  IWFM DLL interface
``iwfm.debug``                logging and debugging helpers
``iwfm.diagnostics``          Process IWFM Simulation diagnostic output files
============================  ==================================================

.. autosummary::
   :toctree: _autosummary
   :recursive:

   iwfm
