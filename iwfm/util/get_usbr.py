# get_usbr.py
# Save a data table from a USBR website into a csv file. Prints status
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

def get_usbr(year, pdf_url, excel_filename='temp.xlsx'):
    ''' get_usbr() - Save a data table from a USBR website into a csv file

    Parameters
    ----------
    year : int or str
        Year of the data to be extracted (must be 4-digit year)

    pdf_url : str
        The URL of the online PDF containing tables

    excel_filename : str, default='temp.xlsx'
        The name of the Excel file to save the extracted tables

    Returns
    -------
    nothing

    Raises
    ------
    ValueError
        If year or pdf_url is invalid
    RuntimeError
        If PDF extraction or data processing fails
    '''
    import os
    from pathlib import Path

    # Input validation
    year_str = str(year)
    if not year_str.isdigit() or len(year_str) != 4:
        raise ValueError(
            f"year must be a 4-digit year, got '{year}'"
        )

    if not isinstance(pdf_url, str) or not pdf_url.strip():
        raise ValueError(
            f"pdf_url must be a non-empty string, got '{pdf_url}'"
        )

    if not pdf_url.startswith(('http://', 'https://')):
        raise ValueError(
            f"pdf_url must start with 'http://' or 'https://', got '{pdf_url}'"
        )

    if not isinstance(excel_filename, str) or not excel_filename.strip():
        raise ValueError(
            f"excel_filename must be a non-empty string, got '{excel_filename}'"
        )

    temp_file_created = False

    try:
        #  Extract tables from pdf and save to Excel file
        pdf_to_excel(pdf_url, excel_filename)
        temp_file_created = True

        #  Create a csv file for each table in the pdf (4 total)
        extract_data_to_csv(excel_filename)

    except Exception as e:
        raise RuntimeError(
            f"Failed to process USBR data for year {year}: {str(e)}"
        ) from e

    finally:
        #  Delete created excel file (cleanup)
        if temp_file_created and Path(excel_filename).exists():
            try:
                os.remove(excel_filename)
            except OSError as e:
                print(f"Warning: Could not delete temporary file '{excel_filename}': {str(e)}")


# Function to read tables from an online PDF and save to Excel
def pdf_to_excel(pdf_url, excel_filename, timeout=60):
    '''pdf_to_excel() - Read tables from an online PDF and save them to an Excel file.

    Parameters
    ----------
    pdf_url : str
        The URL of the online PDF containing tables

    excel_filename : str
        The name of the Excel file to save the extracted tables

    timeout : int, default=60
        Timeout for PDF download in seconds

    Returns
    -------
    nothing

    Raises
    ------
    ValueError
        If PDF contains no tables or tables are invalid
    RuntimeError
        If PDF download or parsing fails
    IOError
        If Excel file cannot be written
    '''
    import tabula
    import requests

    # Download PDF with timeout first to provide better error messages
    try:
        print(f"Downloading PDF from {pdf_url}...")
        response = requests.get(pdf_url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"PDF download from {pdf_url} timed out after {timeout} seconds"
        ) from None
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Failed to connect to {pdf_url}: Check your network connection"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"HTTP {response.status_code} error downloading PDF from {pdf_url}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Failed to download PDF from {pdf_url}: {str(e)}"
        ) from e

    # Read tables from the online PDF (tabula returns pandas DataFrames)
    try:
        print(f"Parsing PDF tables...")
        tables = tabula.read_pdf(pdf_url, pages='all', multiple_tables=True)
    except Exception as e:
        raise RuntimeError(
            f"Failed to parse tables from PDF at {pdf_url}: {str(e)}"
        ) from e

    # Validate tables were found
    if not tables:
        raise ValueError(
            f"No tables found in PDF at {pdf_url}"
        )

    print(f"Found {len(tables)} table(s) in PDF")

    # Write the pandas DataFrames from tabula to Excel
    try:
        import openpyxl

        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)  # drop the default empty sheet

        for i, table in enumerate(tables):
            sheet_name = f'Table_{i+1}'

            # Validate table is not empty (table is a pandas DataFrame from tabula)
            if table is None or table.empty:
                print(f"Warning: Table {i+1} is empty, skipping")
                continue

            worksheet = workbook.create_sheet(title=sheet_name)
            worksheet.append([str(col) for col in table.columns])
            for row in table.itertuples(index=False, name=None):
                worksheet.append(list(row))

        if not workbook.sheetnames:  # openpyxl cannot save a sheetless workbook
            workbook.create_sheet(title='Table_1')

        workbook.save(excel_filename)
        print(f"Tables from {pdf_url} have been extracted and saved to {excel_filename}.")

    except Exception as e:
        raise IOError(
            f"Failed to write tables to Excel file '{excel_filename}': {str(e)}"
        ) from e

def is_year_in_list(year, string_list):
    """is_year_in_list() - Check if a given year is present in any of the strings in a list.

    Parameters
    ----------
    year : str
        The year to check for in the strings.

    string_list : list of str
        A list of strings to search for the given year.

    Returns
    -------
    int or -1
        If the year is found in any of the strings, it returns the index (integer) of the first occurrence.
        If the year is not found in any of the strings, it returns -1.
    """

    for i, string in enumerate(string_list):
        # Split the string by whitespace to get individual words
        words = str(string).split()
        
        # Iterate through the words to check if the year is present
        for word in words:
            if year in word:
                return i
    
    # If the year is not found in any of the strings, return False
    return -1

def get_data(df, table_number, year):
    """get_data() - Extract data for a given year from a polars DataFrame.

    Parameters
    ----------
    df : polars DataFrame
        The DataFrame containing the data.

    table_number : int
        An integer representing the table number.

    year : int or str
        The year for which data needs to be extracted from the DataFrame.

    Returns
    -------
    list
        A list containing the data for the given year. If the year is not found, an empty list is returned.
    """

    #  Account for different format in recent year's (2022) pdf
    if int(year) > 2021 and table_number < 3:
        start = 0
    else:
        start = 1

    #  Convert DataFrame to list
    data = df.rows()

    #  Search for year in header line
    index = is_year_in_list(year, list(data[0]))

     #  For new file format (years > 2021), header may be in this line instead
    index0 = is_year_in_list(year, df.columns)

    #  If year not found in header, might be in other line checked
    if(index == -1):
        index = index0

    #  If year is found, form list of data in its column
    if(index != -1):
        datas = []
        for row in data[start:]:
            #  If element is not NaN, add to list
            if(str(row[index]) != 'nan' and row[index] is not None):
                datas.append(row[index])
            #  For years > 2021, sometimes excel sheet creates 2 columns / header
            #  Data is then offest 1 to right
            elif int(year) > 2021:
                datas.append(row[index + 1])
    return datas

def get_names(df, table_number, year):
    """get_names() - Extract reservoir names from a polars DataFrame.

    Parameters
    ----------
    df : polars DataFrame
        The DataFrame containing the data.

    table_number : int
        The table number for which reservoir names need to be extracted.

    year : int or str
        The year for which reservoir names need to be extracted.

    Returns
    -------
    list
        A list of reservoir names extracted from the DataFrame.
    """

    #  Account for different format in recent year's (2022) pdf
    if int(year) > 2021:
        start = 0
    else:
        start = 1

    #  Get first column of DataFrame with names (using polars slicing)
    first_col = df.columns[0]
    names = df[start:, first_col].to_list()


    #  Add names of correct format to list
    resivoir_names = []
    j = 0
    while j < len(names):
        if (str(names[j]) != 'nan' and names[j] is not None):
            #  When converting pdf to excel, error in splitting names at " AT". This fixes it.
            if (" AT" in str(names[j])):
                new_name = names[j] + " " + names[j + 1]
                resivoir_names.append(new_name)
                j += 1
            else:
                resivoir_names.append(names[j])
        j += 1

    #  For first table, concatonate each dam name to the reservoir name
    if(table_number == 0):
        #  Get dam names (using polars slicing)
        second_col = df.columns[1]
        dam_names = df[2:, second_col].to_list()

        #  Concatonate each name pairing
        for k, dam in enumerate(dam_names):
            resivoir_names[k] = resivoir_names[k] + ' AT ' + dam + " DAM"
    return resivoir_names


def extract_data_to_csv(excel_file):
    '''extract_data_to_csv() - Extract data from an Excel file and save it into 4 separate csv files.

    Parameters
    ----------
    excel_file : str
        The path to the Excel file from which data needs to be extracted

    Returns
    -------
    nothing

    Raises
    ------
    FileNotFoundError
        If Excel file doesn't exist
    ValueError
        If year cannot be extracted or data format is invalid
    IOError
        If CSV files cannot be written
    '''
    import polars as pl
    import re
    from pathlib import Path

    # Validate file exists
    if not Path(excel_file).exists():
        raise FileNotFoundError(
            f"Excel file not found: '{excel_file}'"
        )

    #  Get year with validation
    # Try to extract 4-digit year from filename only (not the full path)
    filename = Path(excel_file).name
    year_match = re.search(r'(\d{4})', filename)
    if not year_match:
        raise ValueError(
            f"Could not extract year from filename '{filename}'. "
            f"Expected filename to contain a 4-digit year"
        )
    year = year_match.group(1)

    #  Units for tables 1-4
    units = [
        "Cubic Feet/Second",
        "Thousands of Acre-Feet",
        "Thousands of Acre-Feet",
        "Inches"
    ]

    #  Titles for tables 1-4
    titles = [
        "Reservoir Releases",
        "Storage in Major Resevoirs",
        "Accumulated Inflow",
        "Accumulated Precipitation"
    ]

    # Read all sheets of the Excel file into a dictionary of DataFrames
    try:
        xls = pl.read_excel(excel_file, sheet_name=None)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Excel file not found: '{excel_file}'"
        ) from None
    except Exception as e:
        raise RuntimeError(
            f"Failed to read Excel file '{excel_file}': {str(e)}"
        ) from e

    # Validate sheets were found
    if not xls:
        raise ValueError(
            f"No sheets found in Excel file '{excel_file}'"
        )

    #  Create list of formatted file names
    file_names = []
    for title in titles:
        file_names.append(f"{title.replace(' ', '_').lower()}_{year}_uwbr.csv")

    #  Go through each DataFrame, one per table
    i = 0
    sheets_processed = 0

    for sheet_name, df in xls.items():
        if i >= len(titles):
            print(f"Warning: More sheets than expected. Skipping sheet '{sheet_name}'")
            break

        #  Open the corresponding file with error handling
        try:
            with open(file_names[i], 'w', encoding='utf-8') as f:
                #  Write header
                f.write("Date, Data, Units, Data Source Location\n")

                #  Get names and dates with error handling
                try:
                    names = get_names(df, i, year)
                    datas = get_data(df, i, year)
                except Exception as e:
                    raise ValueError(
                        f"Failed to extract data from table {i+1} (sheet '{sheet_name}'): {str(e)}"
                    ) from e

                # Validate data consistency
                if len(names) != len(datas):
                    raise ValueError(
                        f"Data mismatch in table {i+1}: {len(names)} names but {len(datas)} data values"
                    )

                #  Write formatted information to file
                for n, dat in enumerate(datas):
                    f.write(f"{year}, {dat}, {units[i]}, {names[n]}\n")

            print(f"{titles[i]} data saved into {file_names[i]}")
            sheets_processed += 1

        except IOError as e:
            raise IOError(
                f"Failed to write CSV file '{file_names[i]}': {str(e)}"
            ) from e

        #  Increment to keep track of table number
        i += 1

    if sheets_processed == 0:
        raise ValueError(
            f"No data was extracted from '{excel_file}'"
        )


if __name__ == "__main__":
    # TODO: Add command line arguments

    from iwfm.debug import parse_cli_flags

    verbose, debug = parse_cli_flags()
    year = input("Which year's CVP END OF WATER YEAR REPORT would you like? ")

    pdf_url = f'https://www.usbr.gov/mp/cvo/vungvari/dayrpt09_{year}.pdf'
    
    excel_filename = f'CVP_{year}.xlsx'

    get_usbr(year, pdf_url, excel_filename)


