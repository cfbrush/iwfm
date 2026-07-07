# get_cdec.py
# Save a data table from a California Data Exchange Center (CDEC) website
# into a csv file. Prints status
# Copyright (C) 2023-2026 University of California
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

from bs4 import BeautifulSoup
import requests
import polars as pl


def parse_html_table(table):
    """ parse_html_table() - Parse an HTML table element into a list of rows.

    Parameters
    ----------
    table : bs4.element.Tag
        BeautifulSoup table element.

    Returns
    -------
    headers : list
        List of column headers.
    rows : list
        List of rows, each row is a list of cell values.
    """
    # Extract headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]

    # Extract data rows
    rows = []
    for row in table.find_all('tr')[1:]:  # skip header row
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if cells:  # skip empty rows
            rows.append(cells)

    return headers, rows


def save_table_as_csv(name, table):
    """ save_table_as_csv() - Save a data table from a website into a csv file. Prints status.

    Parameters
    ----------
    name : string
        Name for new csv file.

    table : bs4.element.Tag
        BeautifulSoup table element collected from website.

    Returns
    -------
    nothing
    """
    try:
        headers, rows = parse_html_table(table)
        if not rows:
            print(f"Failed to parse HTML table for '{name}': Table is empty or malformed")
            return
        # Create polars DataFrame
        # Ensure all rows have same number of columns as headers
        if headers:
            rows = [row[:len(headers)] + [''] * (len(headers) - len(row)) for row in rows]
            df = pl.DataFrame(rows, schema=headers, orient='row')
        else:
            df = pl.DataFrame(rows, orient='row')
    except Exception as e:
        print(f"Failed to parse HTML table for '{name}': {e}")
        return

    try:
        df.write_csv(name)
    except PermissionError as e:
        print(f"Failed to save '{name}': Permission denied")
        print(f"Details: {e}")
        return
    except OSError as e:
        print(f"Failed to save '{name}': File system error")
        print(f"Details: {e}")
        return

    print(f"Data table saved to {name}")
    

def download_data_table(files):
    """ download_data_table() - Save a data table from a website into a csv file. Prints status.

    Parameters
    ----------
    files : list
        List of information about each file in the form [Name, Data Source, url]
    
    Returns
    -------
    info : list
        List of information about the saved files in the form [Name, Data Source]
    """


    info = []

    #  Iterate through provided list
    for name, data_source, url in files:

        #  Form file name
        name = name.replace(' ', '_').lower() + '_raw.csv'
        info.append([name, data_source])

        #  Access url
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"Failed to download '{name}': Request to {url} timed out")
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"Failed to download '{name}': Connection error for {url}")
            print(f"Details: {e}")
            continue
        except requests.exceptions.HTTPError as e:
            print(f"Failed to download '{name}': HTTP error {response.status_code} for {url}")
            print(f"Details: {e}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Failed to download '{name}': Request failed for {url}")
            print(f"Details: {e}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        #  Extract all the data tables from the webpage
        table = soup.find("table")

        #  Save the last table as a CSV file
        if table:
            save_table_as_csv(name, table)
        else:
            print(f"No tables found on {url}")

    return info


def get_cdec(files):
    ''' get_cdec() - Download and format data tables from CDEC websites.

    This is the main entry point for downloading CDEC data. It downloads
    the raw data tables and formats them into standard CSV format.

    Parameters
    ----------
    files : list
        List of information about each file in the form [Name, Data Source, url]

    Returns
    -------
    info : list
        List of information about the saved files in the form [Name, Data Source]

    Raises
    ------
    ValueError
        If files list is invalid
    '''
    if not isinstance(files, list) or not files:
        raise ValueError(
            f"files must be a non-empty list, got {type(files).__name__}"
        )

    info = download_data_table(files)
    format_file(info)
    return info


def format_file(info):
    ''' format_file() - Save a data table from a website into a csv file. Prints status.

    Parameters
    ----------
    info : list
        List of information about the files to access in the form [Name, Data Source]

    Returns
    -------
    nothing

    Raises
    ------
    FileNotFoundError
        If raw data file doesn't exist
    IOError
        If file operations fail
    '''
    import csv
    import os
    from pathlib import Path

    #  Access each file separately
    for file, data_source in info:
        name = file.replace('raw', 'data')

        #  Read file contents with error handling
        try:
            with open(file, 'r', encoding='utf-8') as raw:
                csv_reader = csv.reader(raw)

                #  Write to new file
                with open(name, 'w', newline='', encoding='utf-8') as new_file:
                    csv_writer = csv.writer(new_file)

                    # Write the header to the new CSV file
                    csv_writer.writerow(["Date", " Data", " Units", " Data Source"])

                    units = "Unknown"  # Default value for units
                    for line_number, line in enumerate(csv_reader, start=0):
                        try:
                            # Get units from the first line
                            if line_number == 0:
                                if len(line) > 1:
                                    labels = line[1].split()
                                    if len(labels) > 1:
                                        units = labels[1]

                            # Process data starting from the second line
                            if line_number >= 1:
                                if len(line) >= 2:
                                    year, data = line[0:2]
                                    csv_writer.writerow([year, data, units, data_source])
                                else:
                                    print(f"Warning: Line {line_number+1} has insufficient columns in '{file}', skipping")

                        except (ValueError, IndexError) as e:
                            print(f"Warning: Error processing line {line_number+1} in '{file}': {str(e)}")
                            continue

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Raw data file not found: '{file}'"
            ) from None
        except IOError as e:
            raise IOError(
                f"Failed to read or write file '{file}': {str(e)}"
            ) from e

        #  Delete old file of website table data with error handling
        try:
            if Path(file).exists():
                os.remove(file)
        except OSError as e:
            print(f"Warning: Could not delete raw file '{file}': {str(e)}")

        print(f"Data saved to {name}")


if __name__ == "__main__":
    """Run the main script to extract text from websites and save it to CSV files."""
    
    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()

    """NOTE: The 'files' list expects information about each website in the form of a list. Each sublist should contain 
    [name, data source, url]. This format could be changed. However, then each function/input probably would need to be changed as well. 

    It's essential to have the required dependencies (requests, csv, BeautifulSoup) installed to run this script 
    successfully. 

    """
    
    file_info1 = ["Feather River", "CDEC Kelly Ridge Powerplant Release", "https://cdec.water.ca.gov/dynamicapp/selectQuery?Stations=KLL&SensorNums=23&dur_code=D&Start=2021-10-01&End=2022-09-30"]
    files = [file_info1]
    
    print("WARNING: if 'Name' property is the same for any file(s), their output csv file will have the same name and be overwritten")
    info = download_data_table(files)
    format_file(info)

