iwfm — IWFM file tools for Python
==================================

The ``iwfm`` package reads, writes, and modifies input and output files of
IWFM (Integrated Water Flow Model), the integrated hydrologic model developed
by the California Department of Water Resources. It runs on Windows, Linux,
and macOS.

Highlights
----------

- Readers for preprocessor files (nodes, elements, stratigraphy, streams,
  lakes) and simulation files (groundwater, root zone, unsaturated zone)
- Budget and ZBudget post-processing (HDF5 → text/CSV/Excel)
- Head, hydrograph, and land-use processing
- Submodel extraction (cut a subdomain out of an existing model)
- GIS export (shapefiles, maps), calibration utilities (PEST support),
  and external data fetching (CDEC, NWIS, USACE, USBR)

.. toctree::
   :maxdepth: 1
   :caption: Contents

   install
   file-formats
   api

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
