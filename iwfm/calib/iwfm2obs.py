# iwfm2obs.py
# Read IWFM hydrograph output files and corresponding observation smp files,
# interpolate simulated values to the observation times ('simulated equivalents'),
# and save them in an smp file, optionally writing a paired instruction file.
# Copyright (C) 2020-2026 University of California
# Based on a PEST utility written by Matt Tonkin
#-----------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------
# This file contains python code based on FORTRAN modules and subroutines written
# by John Doherty. John's utility SMP2SMP was ported to python to time-interpolate
# model simulated values to times of observed values. Also added the option to
# write a PEST instruction file.
#-----------------------------------------------------------------------------


def iwfm2obs(verbose=False, head_divisor=None):
    ''' iwfm2obs() interpolates model output to match the times and
        locations of calibration observations and puts them into a PEST-compatible
        smp-formatted output file.

        head_divisor : float or None (default None)
            Divisor applied to simulated GROUNDWATER heads before writing, to undo the
            model head output unit-scale (FACTLTOU) so heads are reported in model units.
            None (default) = auto-detect FACTLTOU from the groundwater file. For legacy
            models FACTLTOU=1 -> no scaling, 3-decimal output (unchanged behavior). When
            the effective divisor is >1 (e.g. FACTLTOU=100 to boost printed precision),
            heads are divided and written to 6 decimals. Passing a value overrides the
            auto-detected FACTLTOU.

    Parameters
    ----------
    nothing

    Returns
    -------
    nothing

    '''
    import sys
    import os
    import iwfm
    import iwfm.calib as calib
    import numpy as np
    from math import ceil
    from scipy.interpolate import interp1d
    from itertools import islice
    from datetime import datetime
    from iwfm.debug.logger_setup import logger

    # == Get main simulation file name via prompt -----------------------------------
    sim_file    = input('IWFM Simulation main file: ')
    sim_dir     = os.path.dirname(sim_file)                                    # directory of simulation file
    logger.info(f'Simulation file: {sim_file}')
    logger.info(f'Model directory: {sim_dir if sim_dir else "(current directory)"}')

    def sim_path(filename):
        ''' Prepend simulation file directory to a filename, unless it is 'none'.
            Converts Windows backslash paths to OS-native separators. '''
        if filename == 'none' or not sim_dir:
            return filename.replace('\\', os.sep)
        return os.path.normpath(os.path.join(sim_dir, filename.replace('\\', os.sep)))

    # == Read Time Step info from IWFM Simulation Input File ------------------------
    start_date, end_date, time_step = iwfm.sim_info(sim_file)
    logger.info(f'Read Simulation Main File {sim_file}')
    if verbose: print(f'\n  Read Simulation Main File {sim_file}')

    start_date = datetime.strptime(start_date[0:10], '%m/%d/%Y')  # string to datetime
    end_date = datetime.strptime(end_date[0:10], '%m/%d/%Y')  # string to datetime
    no_days = (end_date - start_date).days  # days between start and end
    time_step  = time_step.lower()
    logger.info(f'Simulation period: {start_date.strftime("%m/%d/%Y")} to {end_date.strftime("%m/%d/%Y")} ({no_days:,} days, {time_step} steps)')

    sim_file_d = iwfm.iwfm_read_sim(sim_file)                                # get package file names from simulation file
    logger.debug(f'Stream file: {sim_file_d["stream_file"]}')
    logger.debug(f'GW file: {sim_file_d["gw_file"]}')
    gw_file_d, node_id, layers, Kh, Ss, Sy, Kq, Kv, init_cond, units, hydrographs, factxy = iwfm.iwfm_read_gw(sim_path(sim_file_d['gw_file']))                  # get groundwater file names from groundwater file
    logger.debug(f'Subsidence file: {gw_file_d.subs_file}')
    logger.debug(f'Tile drain file: {gw_file_d.drain_file}')

    # Groundwater head output unit-scale (FACTLTOU): iwfm2obs divides simulated GW heads
    # by it so heads are reported in model units regardless of the output factor. A high
    # FACTLTOU (e.g. 100) is used to boost printed precision; dividing recovers ~1e-5 ft.
    # Auto-detected from the GW file unless head_divisor is passed explicitly (override).
    # Legacy models have FACTLTOU=1 -> divisor 1 -> unchanged 3-decimal output.
    def _read_factltou(path):
        try:
            for ln in open(path, encoding='latin-1', errors='ignore'):
                if 'FACTLTOU' in ln and not ln.lstrip().startswith('C'):
                    return float(ln.split()[0])
        except Exception:
            pass
        return 1.0
    gw_divisor = head_divisor if head_divisor is not None else _read_factltou(sim_path(sim_file_d['gw_file']))
    logger.info(f'Groundwater head divisor (FACTLTOU) = {gw_divisor}'
                + (' -> 6-decimal output' if gw_divisor != 1.0 else ' -> 3-decimal output (legacy)'))
    if verbose: print(f'  GW head divisor (FACTLTOU) = {gw_divisor}')

    # check for existence of subprocess file names
    file_dict = {   # 0                              1             2             3             4             5    6     7       8     9
        # name/type     main_file                    smp_obs       smp_out       ins_out       pcf_out       proc wrins rthresh colid skips
        'Streams':     [sim_path(sim_file_d['stream_file']),'st_obs.smp','st_temp.smp','st_temp.ins','st_temp.pcf',True,True, 0,      1,    [ 6,6]],
        'Groundwater': [sim_path(sim_file_d['gw_file'])    ,'gw_obs.smp','gw_temp.smp','gw_temp.ins','gw_temp.pcf',True,True, 0,      5,    [20,2]],
        'Subsidence':  [sim_path(gw_file_d.subs_file)      ,'sb_obs.smp','sb_temp.smp','sb_temp.ins','sb_temp.pcf',True,True, 0,      5,    [ 5,2]],
        'Tile drains': [sim_path(gw_file_d.drain_file)     ,'td_obs.smp','td_temp.smp','td_temp.ins','td_temp.pcf',True,True, 0,      2,    [-1,3]]
    }
    for nt in ['Streams', 'Groundwater', 'Subsidence', 'Tile drains']:
        logger.debug(f'{nt} main file: {file_dict[nt][0]}')

    # == Get other inputs via prompts -------------------------------------------------------------
    headdiffs, missing_file = False, 'sim_miss.out'
    nametype   = ['Streams', 'Groundwater', 'Subsidence', 'Tile drains']
    for nt in nametype:
        main_file  = file_dict[nt][0]
        obs_file, out_file, ins_file, pcf_file = '', '', '', ''
        bprocess, bwriteins, rthresh = False, False, 0
        if main_file != 'none':
            iwfm.file_test(main_file)
            obs_file = input(f'{nt} observation smp file: ')
            if obs_file.strip().lower() in ('none', ''):                       # skip this output type
                bprocess = False
                logger.info(f'{nt}: skipped (no observation file provided)')
                if verbose: print(f'{nt}: skipped (no observation file provided)')
            else:
                iwfm.file_test(obs_file)
                bprocess = True
                rthresh = float(input('Extrapolation threshold (days, float): '))
                logger.info(f'{nt}: obs_file={obs_file}, rthresh={rthresh}')
                if nt == 'Groundwater':
                    head_diff = input('Calculate head differences? [y/n]: ').lower()
                    if head_diff[0] == 'n':
                        headdiffs, hdiffile = False, 'none'
                    else:
                        headdiffs = True
                        hdiffile  = input('Name of well pairs file: ')
                        iwfm.file_test(hdiffile)
                    logger.info(f'  Head differences: {headdiffs}, file: {hdiffile if headdiffs else "n/a"}')
                out_file = input('SMP output file name: ')
                ins_file = input('PEST instruction file (or \'none\'): ')
                if ins_file.lower()[0] == 'n':
                    bwriteins = False
                    pcf_file = ins_file
                else:
                    bwriteins = True
                    pcf_file = ins_file[0:ins_file.find('.')]+'.pcf'                  # replace 'ins' with '.pcf'
                logger.info(f'  out_file={out_file}, ins_file={ins_file}, bwriteins={bwriteins}')
        # replace file_dict place-holders with new info
        old_value = file_dict[nt]
        new_value = [old_value[0],obs_file,out_file,ins_file,pcf_file,bprocess,bwriteins,rthresh,old_value[8],old_value[9]]
        file_dict.update({nt: new_value})
    print(' ') # clean screen

    # == Process hydrographs --------------------------------------------------------
    logger.info('Reading hydrograph info from IWFM input files')
    hyd_info = []
    hyd_file, hyd_names, hdiff_sites, hdiff_pairs = 'none', [], '', ''
    for nt in nametype:
        if file_dict[nt][0] != 'none'and file_dict[nt][5] == True:
            logger.info(f'Reading {nt} Main File {file_dict[nt][0]}')
            if verbose: print(f'\n  Reading {nt} Main File {file_dict[nt][0]}')
            hyd_file, hyd_names = calib.get_hyd_info(nt,file_dict,model_dir=sim_dir)
            logger.info(f'  {len(hyd_names):,} {nt.lower()} hydrograph locations')
            if verbose: print(f'    Read {len(hyd_names):,} {nt.lower()} hydrograph locations')
            if nt == 'Groundwater' and headdiffs == True:
                hdiff_sites, hdiff_pairs, hdiff_link = calib.headdiff_read(hdiffile)
                logger.info(f'  {len(hdiff_sites):,} vertical well pairs from {hdiffile}')
                if verbose: print(f'    Read {len(hdiff_sites):,} vertical well pairs')
        hyd_info.append([hyd_file, hyd_names])

    hyd_dict = dict(zip(nametype, hyd_info))                                      # put hyd_info into a dictionary for easier access

    # == Is there anything to do? ----------------------------------------------------------
    todo = 0
    for nt in nametype:
        if file_dict[nt][5] == True:
            todo += len(hyd_dict[nt][1])                                          # count number of nametypes with work
    if todo == 0:
        logger.warning('Nothing to do, exiting')
        if verbose: print('\n  Nothing to do, exiting')
        sys.exit()
        return 0

    with open(missing_file, 'w') as fmiss:                                        # erase old version
        fmiss.write('')

    # == read simulated hydrographs --------------------------------------------------------
    logger.info('Processing simulated hydrographs')
    for nt in nametype:
        if file_dict[nt][0] != 'none'and file_dict[nt][5] == True:
            logger.info(f'Processing {nt.lower()} hydrographs')
            if verbose: print(f'\n  Processing {nt.lower()} hydrographs')
            sim_sites = hyd_dict[nt][1]                                           # list of site names from Streams.dat file

            sim_hyd, sim_dates = calib.get_sim_hyd(nt,hyd_dict[nt][0],start_date) # read simulated hydrograph values into lists
            if len(sim_dates) == 0:
                logger.warning(f'No simulation data in {hyd_dict[nt][0]}, skipping {nt.lower()}')
                if verbose: print(f'    No simulation data in {hyd_dict[nt][0]}, skipping {nt.lower()}')
                continue
            logger.info(f'  Read {len(sim_dates):,} time steps, {len(sim_sites):,} sites from {hyd_dict[nt][0]}')

            # set up function to interpolate time step from date
            time_steps = [x+1 for x in list(range(len(sim_dates)))]

            # scipy interpolation function for time steps. Same clamped-extrapolation
            # behaviour as sim_func below, so observation dates outside a truncated
            # simulation map to the first/last available time step instead of crashing.
            ts_func = interp1d(
                np.array(sim_dates), np.array(time_steps),
                kind='linear',
                bounds_error=False,
                fill_value=(float(time_steps[0]), float(time_steps[-1])),
            )

            obs_file = file_dict[nt][1]
            obs_sites, obs_data = calib.get_obs_hyd(obs_file,start_date)          # get the observation sites and dates
            logger.info(f'  Read {len(obs_sites):,} observation sites, {len(obs_data):,} observations from {obs_file}')

            sim_miss, sim_both = calib.compare(sim_sites,obs_sites)               # how many obs_sites not in sim_sites?
            if len(sim_miss) > 0:
                logger.warning(f'  {len(sim_miss):,} observation sites not found in simulated sites')
            logger.info(f'  {len(sim_both):,} sites matched between obs and sim')
            calib.write_missing(sim_miss,obs_file,fname=missing_file)

            # -- interpolate simulated values to observation dates and put into smp- and ins-format strings
            obs_data.sort( key = lambda l: (l[0], l[1]))                          # sort by site then by date
            obs_site, obs_date, obs_dt = islice(zip(*obs_data), 3)                # put each obs_data col into a separate list
            smp_out, ins_out, hdiff_data, old_site = [], [], [], ''
            for i in range(0,len(obs_data)):
                if obs_site[i] in sim_sites:
                    if obs_site[i] != old_site:                                   # set up interpolation function for new site
                        old_site = obs_site[i]
                        col_id = sim_sites.index(obs_site[i])

                        sim = []
                        for j in range(0,len(sim_hyd)):
                            sim.append(sim_hyd[j][col_id])

                        # Set up interpolation function. Use clamped extrapolation
                        # (fill with first/last sim value) so observation dates outside
                        # the simulated range — e.g. when a perturbed-param run truncates
                        # the simulation early — produce a finite (large) residual instead
                        # of crashing iwfm2obs. PEST then sees a strong "bad direction"
                        # signal and naturally avoids the broken region.
                        sim_arr = np.array(sim)
                        sim_func = interp1d(
                            np.array(sim_dates), sim_arr,
                            kind='linear',
                            bounds_error=False,
                            fill_value=(float(sim_arr[0]), float(sim_arr[-1])),
                        )

                    if obs_date[i] <= no_days:                                      # should latest be end_date?
                        obs_val = float(sim_func(obs_date[i]))                    # use interpolation function (clamped at sim range edges)
                        ts = ceil(float(ts_func(obs_date[i])))                    # use interpolation function

                        # Groundwater heads: divide by FACTLTOU (auto-detected above) to report
                        # heads in model units; gw_divisor==1.0 for legacy models -> 3 decimals.
                        if nt == 'Groundwater' and gw_divisor != 1.0:
                            obs_val = obs_val / gw_divisor
                            ndec = 6
                        else:
                            ndec = 3
                        smp, ins = calib.to_smp_ins(obs_site[i],obs_dt[i],round(obs_val,ndec),ts)   # put into smp and ins strings
                        smp_out.append(smp)                                       # add smp string to smp_out list
                        ins_out.append(ins)                                       # add ins string to ins_out list

                        if nt == 'Groundwater' and headdiffs == True and obs_site[i] in hdiff_sites:
                            hdiff_data.append([obs_site[i],obs_dt[i],obs_val,ts])   # obs_val already unscaled above

            if nt == 'Groundwater' and headdiffs == True and len(hdiff_data) > 0:  # process headdiffs
                smp, ins = calib.headdiff_hyds(hdiff_pairs, hdiff_data, file_dict[nt][7], ts_func, start_date, verbose)
                smp_out.extend(smp)                                                # add smp string list to smp_out list
                ins_out.extend(ins)                                                # add ins string list to ins_out list

            # -- write smp file ----------------------------------------------------------------
            smp_outfile  = file_dict[nt][2]
            with open(smp_outfile, 'w') as f:
                for item in smp_out:
                    f.write("%s\n" % item)
            logger.info(f'  Wrote {len(smp_out):,} simulated {nt.lower()} values to {smp_outfile}')
            if verbose: print(f'    Wrote {len(smp_out):,} simulated {nt.lower()} values to {smp_outfile}')

            # -- write ins file ----------------------------------------------------------------
            if file_dict[nt][6] == True:        # iwriteins
                ins_outfile  = file_dict[nt][3]
                with open(ins_outfile, 'w') as f:
                    f.write("pif #\n")
                    for item in ins_out:
                        f.write("%s\n" % item)
                logger.info(f'  Wrote instructions to {ins_outfile}')
                if verbose: print(f'    Wrote instrutions to {ins_outfile}')

                # -- if pcf creation is added to smp2smp, write pcf file -------------------------
                #pcf_file  = file_dict[nt][4]
                #with open(pcf_file, 'w') as fpcf:
                #  for item in pcf_out:
                #    fpcf.write("%s\n" % item)
                #print('    Wrote pcf to {}'.format(pcf_file))


if __name__ == "__main__":
    ''' Run iwfm2obs() from command line '''
    import sys
    import iwfm.debug as idb
    from iwfm.debug import parse_cli_flags
    from iwfm.debug.logger_setup import logger, setup_debug_logger

    verbose, debug = parse_cli_flags()

    # Optional override: --head-divisor N. If omitted, iwfm2obs auto-detects FACTLTOU from the GW file.
    head_divisor = None
    for _i, _a in enumerate(sys.argv):
        if _a.startswith('--head-divisor='):
            head_divisor = float(_a.split('=', 1)[1])
        elif _a == '--head-divisor' and _i + 1 < len(sys.argv):
            head_divisor = float(sys.argv[_i + 1])

    if not debug:
        # Always create a log file, even without --debug
        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"iwfm2obs_{timestamp}.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
            level="INFO"
        )
        logger.info(f"Logging to {log_file}")

    idb.exe_time()  # initialize timer
    iwfm2obs(verbose=verbose, head_divisor=head_divisor)

    logger.info('iwfm2obs completed')
    print(' ') # clean screen
    idb.exe_time()  # print elapsed time


