# url_fetch.py
# download a file from URL
# Copyright (C) 2020-2026 University of California
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


'''Download file at url to filename.'''

def url_fetch(url, filename, verbose=False, timeout=30):
    '''Download file at url to filename.

    This function downloads content from a URL and saves it to a local file.
    It includes comprehensive error handling for network issues, HTTP errors,
    and file I/O problems.

    Parameters
    ----------
    url : str
        URL of file to be downloaded. Must start with http://, https://, or ftp://

    filename : str
        Name of local file to save downloaded content

    verbose : bool, default=False
        If True, print status messages during download

    timeout : int, default=30
        Request timeout in seconds. Increase for large files or slow connections.

    Returns
    -------
    nothing

    Raises
    ------
    ValueError
        If url or filename is invalid or empty
    requests.exceptions.Timeout
        If request exceeds timeout period
    requests.exceptions.ConnectionError
        If connection to server fails
    requests.exceptions.HTTPError
        If HTTP request returns error status
    requests.exceptions.RequestException
        If other request errors occur
    IOError
        If file cannot be written to disk

    Examples
    --------
    >>> url_fetch('https://example.com/data.csv', 'local_data.csv', verbose=True)
      Downloading from https://example.com/data.csv
      Saved to local_data.csv (1,234 bytes)

    >>> # Handle timeout for large file
    >>> url_fetch('https://example.com/large.zip', 'data.zip', timeout=120)

    Notes
    -----
    - SSL certificate verification is enabled for security
    - HTTP error status codes (4xx, 5xx) will raise HTTPError
    - Connection errors are reported with helpful messages
    '''
    import requests

    # Input validation
    if not isinstance(url, str) or not url.strip():
        raise ValueError(
            f"url must be a non-empty string, got {repr(url)}"
        )

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError(
            f"filename must be a non-empty string, got {repr(filename)}"
        )

    # Validate URL format
    if not url.startswith(('http://', 'https://', 'ftp://')):
        raise ValueError(
            f"url must start with 'http://', 'https://', or 'ftp://'. "
            f"Got: '{url}'"
        )

    if verbose:
        print(f'  Downloading from {url}')

    # Download with comprehensive error handling
    try:
        # Make request with timeout and SSL verification enabled
        r = requests.get(url, timeout=timeout, verify=True)

        # Raise exception for HTTP errors (4xx, 5xx status codes)
        r.raise_for_status()

    except requests.exceptions.Timeout:
        raise requests.exceptions.Timeout(
            f"Request to {url} timed out after {timeout} seconds. "
            f"Try increasing the timeout parameter or check your network connection."
        ) from None

    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError(
            f"Failed to connect to {url}. "
            f"Check your network connection and verify the URL is correct. "
            f"Original error: {str(e)}"
        ) from e

    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"HTTP error {r.status_code} when requesting {url}: {r.reason}. "
            f"The server returned an error response."
        ) from e

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Unexpected error downloading from {url}: {str(e)}"
        ) from e

    # Write file with error handling
    try:
        with open(filename, 'wb') as f:
            f.write(r.content)
    except IOError as e:
        raise IOError(
            f"Failed to write downloaded content to '{filename}': {str(e)}. "
            f"Check that the directory exists and you have write permissions."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error writing file '{filename}': {str(e)}"
        ) from e

    if verbose:
        print(f'  Saved to {filename} ({len(r.content):,} bytes)')

