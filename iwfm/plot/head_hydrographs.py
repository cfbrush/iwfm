# head_hydrographs.py
# Create hydrograph plots comparing simulated vs observed heads
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


'''Create hydrograph plots comparing simulated vs observed heads.'''

def read_hyd_info(gw_file):
    """Read hydrograph well information from IWFM Groundwater.dat file.

    Uses iwfm.iwfm_read_gw() to parse the groundwater file and extracts
    the hydrograph well dictionary.

    Parameters
    ----------
    gw_file : str
        Path to IWFM Groundwater.dat file

    Returns
    -------
    dict
        Dictionary mapping well_name to (order, layer, x, y)
        order: 1-based column index in simulated output
        layer: aquifer layer number
        x, y: coordinates (IHYDTYP=0) or (0.0, 0.0) if IHYDTYP=1
    """
    from iwfm.iwfm_read_gw import iwfm_read_gw

    gw_files, node_id, layers, Kh, Ss, Sy, Kq, Kv, init_cond, units, \
        hydrographs, factxy = iwfm_read_gw(gw_file)

    return hydrographs


def read_obs_heads(obsfile):
    """Read observed head data from PEST SMP format file.

    Delegates to iwfm.read_obs_smp() which reads any PEST SMP file
    and returns a polars DataFrame or dict with columns:
    site_name, date, time, obs_value.

    Parameters
    ----------
    obsfile : str
        Path to observation file in SMP format
        Format: well_name  date(MM/DD/YYYY)  time(H:MM:SS)  head(ft)

    Returns
    -------
    polars.DataFrame or dict
        DataFrame/dict with keys: site_name, date, time, obs_value.
        date values are datetime objects, obs_value values are floats.
    """
    from iwfm.read_obs_smp import read_obs_smp

    return read_obs_smp(obsfile)


def plot_head_hydrograph(well_name, layer, obs_dates, obs_heads, sim_data_list,
                         run_names, plot_title='', yaxis_width=0,
                         output_dir='.', verbose=False):
    """Create a single hydrograph PDF comparing observed and simulated heads.

    Parameters
    ----------
    well_name : str
        Well identifier for title and filename

    layer : int
        Aquifer layer number for title

    obs_dates : list of datetime
        Observation dates

    obs_heads : list of float
        Observed head values (ft)

    sim_data_list : list of tuples
        Each tuple contains (sim_dates, sim_heads) for one simulation run
        sim_dates: list of datetime
        sim_heads: list of float

    run_names : list of str
        Names for each simulation run (legend entries)

    plot_title : str, default=''
        Title printed above the well name/layer line (e.g. project name).
        If empty, only the well name and layer are shown.

    yaxis_width : int or float, default=0
        Minimum y-axis range in feet. If the data range is smaller
        than this value, the axis will be padded equally on both sides.
        Use 0 to auto-scale to data range.

    output_dir : str, default='.'
        Directory for output PDF

    verbose : bool, default=False
        Print progress messages

    Returns
    -------
    str
        Path to created PDF file
    """
    import os
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages

    # Line styles for multiple runs: solid, dashed, dotted
    line_colors = ['r-', 'g-', 'c-', 'm-', 'k-', 'y-',
                   'r--', 'g--', 'c--', 'm--', 'k--', 'y--',
                   'r:', 'g:', 'c:', 'm:', 'k:', 'y:']

    # Determine y-axis range
    ymin, ymax = float('inf'), float('-inf')

    if obs_heads:
        ymin = min(ymin, min(obs_heads))
        ymax = max(ymax, max(obs_heads))

    for sim_dates, sim_heads in sim_data_list:
        if sim_heads:
            ymin = min(ymin, min(sim_heads))
            ymax = max(ymax, max(sim_heads))

    # Enforce minimum y-axis width
    if ymin != float('inf') and ymax != float('-inf'):
        data_range = ymax - ymin
        if data_range < yaxis_width:
            mid = (ymin + ymax) / 2
            ymin = mid - yaxis_width / 2
            ymax = mid + yaxis_width / 2

    # Determine x-axis tick interval based on date range
    date_range = None
    if sim_data_list and sim_data_list[0][0]:
        date_range = (sim_data_list[0][0][-1] - sim_data_list[0][0][0]).days
    elif obs_dates and len(obs_dates) > 1:
        date_range = (max(obs_dates) - min(obs_dates)).days

    if date_range is not None:
        if date_range < 365 * 10:
            year_interval = 1
        elif date_range < 365 * 20:
            year_interval = 2
        elif date_range < 365 * 70:
            year_interval = 5
        else:
            year_interval = 10
    else:
        year_interval = 5

    # Create PDF
    pdf_name = f"{well_name}_layer{layer}_hydrograph.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    if verbose:
        print(f"  Creating hydrograph: {pdf_name}")

    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(10, 7.5))

        # Add 0.75 inch margins on all sides (in figure fraction units)
        # For 10x7.5 inch figure: 0.75/10 = 0.075 left/right, 0.75/7.5 = 0.1 top/bottom
        fig.subplots_adjust(left=0.12, right=0.925, top=0.9, bottom=0.12)

        # Configure axes
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.YearLocator(year_interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Grid and box
        ax.grid(True, linestyle='dashed', alpha=0.7)
        ax.spines['top'].set_visible(True)
        ax.spines['right'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)

        # Labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Head (ft)')
        if plot_title:
            fig.suptitle(plot_title, fontsize=14, fontweight='bold')
            ax.set_title(f'{well_name} - Layer {layer}', fontsize=12)
        else:
            ax.set_title(f'{well_name} - Layer {layer}')

        # Plot observed data as blue dots
        if obs_dates and obs_heads:
            ax.plot(obs_dates, obs_heads, 'bo', markersize=4, label='Observed')

        # Plot simulated data as colored lines
        for i, ((sim_dates, sim_heads), run_name) in enumerate(zip(sim_data_list, run_names)):
            color_style = line_colors[i % len(line_colors)]
            ax.plot(sim_dates, sim_heads, color_style, linewidth=1.5, label=run_name)

        # Set y-axis limits
        if ymin != float('inf') and ymax != float('-inf'):
            ax.set_ylim(ymin, ymax)

        # Legend
        ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='black')

        pdf.savefig(fig)
        plt.close(fig)

    return pdf_path


def extract_sim_dates(sim_data):
    """Extract dates from simulation data structure.

    Parameters
    ----------
    sim_data : list of lists
        Simulation data with dates in first element of each row

    Returns
    -------
    list of datetime
        Dates for each time step
    """
    return [row[0] for row in sim_data]


def extract_sim_column(sim_data, column_index):
    """Extract a column of head values from simulation data.

    Parameters
    ----------
    sim_data : list of lists
        Simulation data with head values

    column_index : int
        Column index (1-based well order) to extract

    Returns
    -------
    list of float
        Head values for the specified well
    """
    # column_index is 1-based order, which maps to sim_data column index
    # sim_data[row][0] is date, sim_data[row][1] is first well, etc.
    return [row[column_index] for row in sim_data if len(row) > column_index]


def plot_all_hydrographs(gw_file, obsfile, simfiles, plot_title='',
                         yaxis_width=0, output_dir='.', verbose=False):
    """Create hydrograph PDFs for all wells with observations and/or simulations.

    Parameters
    ----------
    gw_file : str
        Path to IWFM Groundwater.dat file for well info

    obsfile : str or None
        Path to observed heads file (PEST SMP format).
        Use None (or 'None'/'none') to plot simulated values only.

    simfiles : list of tuples
        Each tuple is (filepath, run_name) for a simulation.
        May be empty to plot observations only.

    plot_title : str, default=''
        Title printed above the well name/layer on each plot
        (e.g. project name). Passed to plot_head_hydrograph().

    yaxis_width : int or float, default=0
        Minimum y-axis range in feet. Passed to plot_head_hydrograph().
        Use 0 to auto-scale to data range.

    output_dir : str, default='.'
        Directory for output PDFs

    verbose : bool, default=False
        Print progress messages

    Returns
    -------
    list of str
        Paths to created PDF files
    """
    import os

    # Treat 'None' and 'none' strings as no observation file
    has_obs = obsfile is not None and str(obsfile).lower() != 'none'

    # Read well metadata: {well_name: (order, layer, x, y)}
    well_dict = read_hyd_info(gw_file)

    if verbose:
        print(f"Read {len(well_dict)} wells from {gw_file}")

    # Read observed data if available
    obs_data = None
    is_polars = False
    obs_wells = []

    if has_obs:
        obs_data = read_obs_heads(obsfile)

        # Handle both polars DataFrame and dict
        try:
            import polars as pl
            is_polars = isinstance(obs_data, pl.DataFrame)
        except ImportError:
            is_polars = False

        if is_polars:
            obs_count = len(obs_data)
            obs_wells = obs_data.select('site_name').unique().to_series().to_list()
        else:
            obs_count = len(obs_data['site_name'])
            obs_wells = list(set(obs_data['site_name']))

        if verbose:
            print(f"Read {obs_count} observations from {obsfile}")

    # Read simulated data for each run (if any)
    sim_runs = []
    run_names = []
    if simfiles:
        from iwfm.read_sim_hyd import read_sim_hyd

        for simfile, run_name in simfiles:
            sim_data = read_sim_hyd(simfile)
            sim_runs.append(sim_data)
            # Use provided run_name, or filename without extension
            if not run_name:
                run_name = os.path.splitext(os.path.basename(simfile))[0]
            run_names.append(run_name)

            if verbose:
                print(f"Read {len(sim_data)} time steps from {simfile}")

    # Determine which wells to plot:
    # - If observations exist, plot wells with observations
    # - If no observations, plot all wells in the well dictionary
    if has_obs:
        plot_wells = obs_wells
    else:
        plot_wells = list(well_dict.keys())

    if verbose:
        print(f"Plotting {len(plot_wells)} wells")

    # Create output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    created_files = []

    for well_name in plot_wells:
        if well_name not in well_dict:
            if verbose:
                print(f"  Warning: {well_name} not in well dictionary, skipping")
            continue

        order, layer, x, y = well_dict[well_name]

        # Extract observed data for this well (empty if no obs file)
        obs_dates = []
        obs_heads = []
        if has_obs:
            if is_polars:
                import polars as pl
                well_obs = obs_data.filter(pl.col('site_name') == well_name)
                obs_dates = well_obs.select('date').to_series().to_list()
                obs_heads = well_obs.select('obs_value').to_series().to_list()
            else:
                obs_dates = [obs_data['date'][i] for i, sn in enumerate(obs_data['site_name']) if sn == well_name]
                obs_heads = [obs_data['obs_value'][i] for i, sn in enumerate(obs_data['site_name']) if sn == well_name]

        # Extract simulated data for this well (column = order)
        sim_data_list = []
        for sim_data in sim_runs:
            sim_dates = extract_sim_dates(sim_data)
            sim_heads = extract_sim_column(sim_data, order)
            sim_data_list.append((sim_dates, sim_heads))

        # Create hydrograph
        pdf_path = plot_head_hydrograph(
            well_name, layer, obs_dates, obs_heads,
            sim_data_list, run_names, plot_title, yaxis_width,
            output_dir, verbose
        )
        created_files.append(pdf_path)

    if verbose:
        print(f"Created {len(created_files)} hydrograph PDFs")

    return created_files


if __name__ == '__main__':
    import sys
    from iwfm.debug import exe_time

    if len(sys.argv) < 4:
        print("Usage: python plot_head_hydrographs.py <plot_title> <gw_file> <obs_file> [sim_file1 name1 ...]")
        print("  Creates hydrograph PDFs comparing observed and/or simulated heads")
        print("")
        print("  plot_title : Title for each plot (e.g. project name, use 'None' to skip)")
        print("  gw_file    : IWFM Groundwater.dat file with hydrograph locations")
        print("  obs_file   : Observed heads in PEST SMP format (use 'None' to skip)")
        print("  sim_file   : IWFM hydrograph output file(s), each followed by a run name")
        print("")
        print("  Examples:")
        print("    python plot_head_hydrographs.py 'C2VSim Fine Grid' gw.dat obs.smp sim.out 'Base Run'")
        print("    python plot_head_hydrographs.py 'My Project' gw.dat None sim1.out 'Run 1' sim2.out 'Run 2'")
        print("    python plot_head_hydrographs.py None gw.dat obs.smp")
        sys.exit(1)

    plot_title = sys.argv[1]
    gw_file = sys.argv[2]
    obs_file = sys.argv[3]

    # Treat 'None' or 'none' as no plot title
    if plot_title.lower() == 'none':
        plot_title = ''

    # Parse sim file / run name pairs from remaining arguments
    sim_args = sys.argv[4:]
    sim_files = []
    i = 0
    while i < len(sim_args):
        simfile = sim_args[i]
        if i + 1 < len(sim_args):
            run_name = sim_args[i + 1]
            i += 2
        else:
            run_name = simfile  # Use filename as name if no name provided
            i += 1
        sim_files.append((simfile, run_name))

    # Treat 'None' or 'none' as no observation file
    if obs_file.lower() == 'none':
        obs_file = None

    if obs_file is None and not sim_files:
        print("Error: Must provide either an observation file or simulation file(s)")
        sys.exit(1)

    # Verify input files exist
    import iwfm
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    iwfm.file_test(gw_file)
    if obs_file is not None:
        iwfm.file_test(obs_file)
    for simfile, _ in sim_files:
        iwfm.file_test(simfile)

    exe_time()  # initialize timer
    pdfs = plot_all_hydrographs(gw_file, obs_file, sim_files, plot_title, verbose=verbose)
    count = len(pdfs)
    print(f"Created {count} hydrograph PDF files")
    exe_time()  # print elapsed time
