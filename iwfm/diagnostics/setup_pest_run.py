# setup_pest_run.py
# Create a clean PEST run folder from reference run
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

import os
import shutil


def setup_pest_run(reference_dir, output_dir, pst_file=None,
                   run_name='c2vsim_llm', copy_model=True,
                   verbose=False):
    """Create a clean PEST run folder from a reference run directory.

    Copies essential files from reference_dir to output_dir:
    - Template files (.tpl)
    - Instruction files (.ins)
    - Observation data files (.smp)
    - Run scripts (.sh)
    - Control input files (.in)
    - Model directory (if copy_model=True)
    - Places the new .pst file if provided

    Parameters
    ----------
    reference_dir : str
        Path to reference PEST run (e.g., c2vsimcg_pypest_iterate).
    output_dir : str
        Path for new PEST run folder. Created if it doesn't exist.
    pst_file : str, optional
        Path to .pst file to place in the new folder. If None,
        no .pst is copied (must be generated separately).
    run_name : str
        Base name for PEST files (used for run script).
    copy_model : bool
        If True, copy the model/ subdirectory.
    verbose : bool
        Print progress.

    Returns
    -------
    dict
        {'output_dir': str, 'pst_path': str or None,
         'files_copied': int, 'model_copied': bool}.
    """
    os.makedirs(output_dir, exist_ok=True)

    # File patterns to copy from reference
    copy_extensions = {'.tpl', '.ins', '.smp', '.in'}
    copy_scripts = {'run_c2vsim_with_pest.sh', 'run_iwfm2obs.sh'}

    files_copied = 0

    # Copy essential files
    for entry in os.listdir(reference_dir):
        src = os.path.join(reference_dir, entry)
        if not os.path.isfile(src):
            continue

        _, ext = os.path.splitext(entry)
        should_copy = (ext in copy_extensions or entry in copy_scripts)

        if should_copy:
            dst = os.path.join(output_dir, entry)
            shutil.copy2(src, dst)
            files_copied += 1
            if verbose:
                print(f'  Copied {entry}')

    # Copy model directory
    model_copied = False
    if copy_model:
        src_model = os.path.join(reference_dir, 'model')
        dst_model = os.path.join(output_dir, 'model')
        if os.path.isdir(src_model):
            if os.path.exists(dst_model):
                shutil.rmtree(dst_model)
            shutil.copytree(src_model, dst_model)
            model_copied = True
            if verbose:
                n_model = len(os.listdir(dst_model))
                print(f'  Copied model/ ({n_model} files)')

    # Create results directory
    results_dir = os.path.join(output_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Place .pst file
    pst_path = None
    if pst_file and os.path.exists(pst_file):
        pst_dest = os.path.join(output_dir, f'{run_name}.pst')
        shutil.copy2(pst_file, pst_dest)
        pst_path = pst_dest
        if verbose:
            print(f'  Placed PST: {pst_dest}')

    # Write a simple run script for the new PEST run
    run_script = os.path.join(output_dir, f'run_pest_{run_name}.sh')
    with open(run_script, 'w', encoding='utf-8') as f:
        f.write('#!/bin/zsh\n')
        f.write(f'echo "START: $(date)" >> pest_timing.txt\n\n')
        f.write(f'pypest {run_name}.pst --n-workers 10 \\\n')
        f.write(f'   --log-file {run_name}.log '
                f'--err-file {run_name}.err\n\n')
        f.write(f'echo "END: $(date)" >> pest_timing.txt\n')
    os.chmod(run_script, 0o755)

    if verbose:
        print(f'\n  PEST run folder ready: {output_dir}')
        print(f'  {files_copied} files copied, '
              f'model {"copied" if model_copied else "skipped"}')

    return {
        'output_dir': output_dir,
        'pst_path': pst_path,
        'files_copied': files_copied,
        'model_copied': model_copied,
    }
