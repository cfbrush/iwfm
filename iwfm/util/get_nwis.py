# get_nwis.py
# Save a data table from an NWIS website into a csv file. Prints status
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


def get_nwis(files, timeout=30):
    ''' get_nwis() - Save a data table from an NWIS website into a csv file. Prints status.

    Parameters
    ----------
    files : list
        List of information about each file in the form [Name, Data Source, url]

    timeout : int, default=30
        Request timeout in seconds

    Returns
    -------
    info : list
        List of information about the saved files in the form [Name, Data Source]

    Raises
    ------
    ValueError
        If files list is invalid or empty
    '''
    import requests
    from bs4 import BeautifulSoup

    # Validate input
    if not isinstance(files, list) or not files:
        raise ValueError(
            f"files must be a non-empty list, got {type(files).__name__}"
        )

    info = []
    failed_urls = []

    #  Iterate through provided list
    for file_info in files:
        # Validate file_info structure
        if not isinstance(file_info, (list, tuple)) or len(file_info) != 3:
            print(f"Warning: Skipping invalid file_info: {file_info}. "
                  f"Expected [name, data_source, url]")
            continue

        name, data_source, url = file_info

        #  Form file name
        name = name.replace(' ', '_').lower() + '_raw.csv'
        info.append([name, data_source])

        try:
            #  Access url with timeout and error handling
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

        except requests.exceptions.Timeout:
            print(f"Failed to download '{name}': Request to {url} timed out after {timeout}s")
            failed_urls.append((name, url, "timeout"))
            continue

        except requests.exceptions.ConnectionError as e:
            print(f"Failed to download '{name}': Connection error for {url}")
            failed_urls.append((name, url, "connection_error"))
            continue

        except requests.exceptions.HTTPError as e:
            print(f"Failed to download '{name}': HTTP {response.status_code} error for {url}")
            failed_urls.append((name, url, f"http_{response.status_code}"))
            continue

        except requests.exceptions.RequestException as e:
            print(f"Failed to download '{name}': Unexpected error for {url}: {str(e)}")
            failed_urls.append((name, url, "unknown_error"))
            continue

        # Parse HTML
        try:
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"Failed to parse HTML from {url}: {str(e)}")
            failed_urls.append((name, url, "parse_error"))
            continue

        #  Extract all the data tables from the webpage
        tables = soup.find_all("table")

        #  Save the last table as a CSV file
        if tables:
            last_table = tables[-1]
            save_table_as_csv(name, last_table)
        else:
            print(f"No tables found on {url}")
            failed_urls.append((name, url, "no_tables"))

    # Report failures if any
    if failed_urls:
        print(f"\n⚠️  Warning: {len(failed_urls)} URL(s) failed to download:")
        for name, url, reason in failed_urls:
            print(f"  - {name}: {reason}")

    return info

def parse_html_table(table):
    ''' parse_html_table() - Parse an HTML table element into headers and rows.

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
    '''
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
    ''' save_table_as_csv() - Save a data table from a website into a csv file. Prints status.

    Parameters
    ----------
    name : str
        Name for new csv file

    table : bs4.element.Tag
        HTML table element collected from website

    Returns
    -------
    nothing

    Raises
    ------
    ValueError
        If table cannot be parsed or contains no data
    IOError
        If file cannot be written
    '''
    import polars as pl

    try:
        # Parse HTML table using BeautifulSoup
        headers, rows = parse_html_table(table)

        # Validate parsed data
        if not rows:
            raise ValueError(f"Table '{name}' contains no data")

        # Create polars DataFrame
        # Ensure all rows have same number of columns as headers
        if headers:
            rows = [row[:len(headers)] + [''] * (len(headers) - len(row)) for row in rows]
            df = pl.DataFrame(rows, schema=headers, orient='row')
        else:
            df = pl.DataFrame(rows, orient='row')

    except ValueError as e:
        raise ValueError(
            f"Failed to parse HTML table for '{name}': {str(e)}"
        ) from e
    except Exception as e:
        raise ValueError(
            f"Failed to parse HTML table for '{name}': {str(e)}"
        ) from e

    # Write to CSV with error handling
    try:
        df.write_csv(name)
        print(f"Data table saved to {name} ({len(df)} rows)")
    except IOError as e:
        raise IOError(
            f"Failed to write CSV file '{name}': {str(e)}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error saving table to '{name}': {str(e)}"
        ) from e
    

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
    ValueError
        If file format is invalid
    IOError
        If file operations fail
    '''
    import csv
    import os
    from pathlib import Path

    #  Access each file separately
    for file, data_source in info:
        # Only replace 'raw' in the filename, not the directory path
        file_path = Path(file)
        new_filename = file_path.name.replace('raw', 'data')
        name = str(file_path.parent / new_filename)

        #  Read file contents with error handling
        try:
            with open(file, 'r', encoding='utf-8') as raw:
                csv_reader = csv.reader(raw)
                next(csv_reader)  # Skip the first line (header)

                #  Write to new file
                with open(name, 'w', newline='', encoding='utf-8') as new_file:
                    csv_writer = csv.writer(new_file)

                    # Write the header to the new CSV file
                    csv_writer.writerow(["Date", "Data", "Units", "Data Source"])

                    for line_number, line in enumerate(csv_reader, start=1):
                        try:
                            # Get units from the second line
                            if line_number == 1:
                                if len(line) < 2:
                                    raise ValueError(f"Line 2 has insufficient columns: {len(line)}")
                                if "Monthly mean in " not in line[1]:
                                    raise ValueError(f"Line 2 does not contain expected 'Monthly mean in' text")
                                index = line[1].index("Monthly mean in ") + 16
                                units = line[1][index:].split()[0]

                            # Process data starting from the fourth line
                            if line_number >= 4:
                                if len(line) < 13:
                                    print(f"Warning: Line {line_number+1} has fewer than 13 columns, skipping")
                                    continue
                                year = line[0]
                                for i, data in enumerate(line[1:13], start=1):
                                    csv_writer.writerow([f"{i}/{year}", data, units, data_source])

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
    # TODO: Add command line arguments

    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    file_info1 = ["Sacramento River", "USGS Gage 11370500 SACRAMENTO RIVER AT KESWICK, CA", "https://waterdata.usgs.gov/nwis/monthly?referred_module=sw&amp;site_no=11370500&amp;por_11370500_10158=2209233,00060,10158,1938-10,2022-11&amp;format=html_table&amp;date_format=YYYY-MM-DD&amp;rdb_compression=file&amp;submitted_form=parameter_selection_list"]
    file_info2 = ["Clear Creek", "USGS Gage 11372000 CLEAR C NR IGO CA", "https://waterdata.usgs.gov/nwis/monthly?referred_module=sw&amp;site_no=11372000&amp;por_11372000_10170=2209239,00060,10170,1940-10,2023-02&amp;format=html_table&amp;date_format=YYYY-MM-DD&amp;rdb_compression=file&amp;submitted_form=parameter_selection_list"]
    files = [file_info1, file_info2]
    
    print("WARNING: if 'Name' property is the same for any file(s), their output csv file will have the same name and be overwritten")
    info = get_nwis(files)
    format_file(info)

