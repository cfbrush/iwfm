# iwfm — Usage Examples

Short scripts showing common workflows. Each example is self-contained and runnable from this directory.

## Library examples

| File | What it does |
|---|---|
| `01_read_preprocessor.py` | Open an IWFM preprocessor file, print node/element/stratigraphy counts |
| `02_hyd_diff.py` | Compute the difference between two IWFM hydrograph output files |
| `03_model_shapefiles.py` | Read preprocessor file, write node + element shapefiles for the model mesh |
| `04_head_maps.py` | Map simulated heads over the model domain at one timestep (point/contour/filled-contour TIFFs per layer) |
| `05_hdf_to_csv.py` | Convert an IWFM groundwater budget HDF5 file to text |
| `06_xls_workbook.py` | Build an Excel workbook with the openpyxl backend |
| `07_logging.py` | Configure loguru-based logging from a script |

## CLI examples

| File | What it shows |
|---|---|
| `cli_examples.sh` | Common `iwfm` subcommand invocations |

## Running

Most scripts assume you've installed the package (`python -m pip install -e ../..` from this directory) and that any input files referenced exist. Each script's docstring lists what it expects.
