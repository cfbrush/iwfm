# iwfm

Python functions to work with IWFM-based models

# README #

* Quick summary

The California Department of Water Resources is actively developing the Integrated Water Flow Model for creating integrated hydrologic models. 

This repository contains a python package for working with IWFM model input and output files. Many of these work across the Windows, Linux and MacOS operating systems.

* Version

Initial release: Alpha January 2021, most recent update April 2026

### How do I get set up? ###

Install a version of Python between 3.6 and 3.10 (some dependencies may not have been updated to the latest Python version, currently optimized for Python 3.9).

Download this repository and navigate to the iwfm directory. Install using 'python -m pip install'. 

Alternatively, if you want to contribute to this project, see the installation instructions below under Contribution Guidelines.

There are two potential installation errors, with workarounds described here.

1. pip may stop when trying to install demjson. This package will install using an older version of setuptools.
Roll back the setuptools to version 57.5.0, install demjson, and then update to the current setuptools.
	> pip install setuptools==57.5.0
 
	> pip install demjson
 
	> pip install --upgrade setuptools
Then run ‘pip install -e iwfm’ again.

2. Installation stops on some Windows computers using Arm processors when trying to install a package called leven. 
Apparently PyPI doesn't contain a wheel for these processors, but there's an easy work-around.
If this happens: 
	- Download the "Microsoft C++ Build Tools" from https://visualstudio.microsoft.com/visual-cpp-build-tools/.
	- Install the "Desktop Development with C++” package
	> pip install leven
 
Then run ‘pip install -e iwfm’ again.

### How do I use this package? ###

* In python programs

Once this package is installed, import 'iwfm' to use the package components.

For example, to use the hyd_diff function (create a new IWFM hydrograph file as the difference between two IWFM hydrograph files):
 
import iwfm as iwfm

iwfm.hyd_diff(scenario_file_name, base_file_name, diff_file_name)
 
Or:
 
import iwfm.hyd_diff as hyd_diff

hyd_diff(scenario_file_name, base_file_name, diff_file_name)
 
* From the command line

Many of the python functions can also be run from the command line, as they contain a section “if __name__ = ‘__main__’:" that handles command line input. For example, to run hyd_diff.py from the Results directory of a model, you can use:
 
python [path\to\iwfm\package\directory]\hyd_diff.py C2VSimFG_GW_Hydrograph_Scenario.out C2VSimFG_GW_Hydrograph_Base.out C2VSimFG_GW_Hydrograph_Diff.out
 
You may also be able to make [path\to\iwfm\package\directory] part of the PYTHONPATH environment variable to run commands without specifying this path.

### Contribution guidelines ###

Please consider contributing to this effort, whether through bug reporting, making improvements or contributing new components.

To become a contributor, download the source file repository using Github Desktop, Sourcetree, terminal-based git, or another source control program.

Install the package from the top 'iwfm' directory using 'python -m pip install -e iwfm'. The '-e' option will allow you to edit the source files while using the package; python will then re-compile any changed files to pseudocode at execution time.

Submit suggested code changes and additions to the repository using a 'pull request'.

* Adding to the package

Add your new function foo() to this package in two steps.

First, create a new file containing the function foo(), and save it as foo.py in directory iwfm

Next, open the file __init__.py in directory iwfm and add the following line:

from iwfm.foo import foo

Congratulations! foo() is now part of the iwfm package.

You can now call foo() with:

import iwfm as iwfm

iwfm.foo()

### Who do I talk to? ###

* Repo owner/admin: cfbrush_AT_gmail_DOT_com or charles_DOT_brush_AT_hydrolytics-llc_DOT_com
