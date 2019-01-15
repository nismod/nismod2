#!/usr/bin/env python
"""Download data
"""
import configparser
import os
import subprocess
import sys

import pysftp

def main(remote_file, local_dir):
    """Download a remote file to a local directory, unzipping if necessary

    Uses FTP_USERNAME, FTP_PASSWORD, FTP_HOST environment variables
    Or falls back to a `ftp.ini` config file saved next to this script:

        [ftp-config]
        ftp_host=<host>
        ftp_username=<username>
        ftp_password=<password>

    """
    # Read connection details
    if 'FTP_USERNAME' in os.environ and 'FTP_PASSWORD' in os.environ and \
            'FTP_HOST' in os.environ:
        ftp_username = os.environ['FTP_USERNAME']
        ftp_password = os.environ['FTP_PASSWORD']
        ftp_host = os.environ['FTP_HOST']
    else:
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.path.dirname(__file__), 'ftp.ini'))
        ftp_username = parser['ftp-config']['ftp_username']
        ftp_password = parser['ftp-config']['ftp_password']
        ftp_host = parser['ftp-config']['ftp_host']

    print("Downloading {} to {}".format(remote_file, local_dir))

    # Download data from server
    try:
        with pysftp.Connection(ftp_host, username=ftp_username, password=ftp_password) as conn:
            with pysftp.cd(local_dir):
                conn.get(remote_file)
    # Print message and quit
    except Exception as ex:
        RED='\033[0;31m'
        NC='\033[0m' # No Color
        msg = """\
{RED}Unable to download {remote_file} from {ftp_username}@{ftp_host}.{NC}
{RED}Make sure that the server is responsive, ftp environment vars are set{NC}
{RED}or the credentials in provision/ftp.ini are correct.{NC}
        """.format(
            RED=RED,
            NC=NC,
            remote_file=remote_file,
            ftp_username=ftp_username,
            ftp_host=ftp_host
        )
        print(msg)
        raise ex

    # Unpack downloaded ZIP files
    subprocess.run(['unzip', '-o', '{}/*.zip'.format(local_dir), '-d', '{}'.format(local_dir)])
    subprocess.run(['rm', '-f', '{}/*.zip'.format(local_dir)])

if __name__ == '__main__':
    try:
        REMOTE = sys.argv[1]
        LOCAL = sys.argv[2]
    except KeyError:
        exit("Usage: python {} <remote_file> <local_dir>".format(__file__))
    main(REMOTE, LOCAL)
