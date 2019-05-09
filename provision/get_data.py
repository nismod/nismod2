#!/usr/bin/env python
"""Download data
"""
import boto3
import os
import subprocess
import sys


def main(remote_file, local_dir):
    """Download a remote file to a local directory, unzipping if necessary

    Uses credentials from `s3.ini` config file saved next to this script, which
    must contain your personal access key and secret key. Users are expected to
    have copied `template.s3.ini` and replaced the placeholder values.

        [profile nismod2-s3]
        aws_access_key_id = <your-access-key-id>
        aws_secret_access_key = <your-secret-access-key>
        region = eu-west-2
        output = json

    """
    local_file = os.path.join(local_dir, os.path.basename(remote_file))
    if os.path.exists(local_file):
        print("Skipping download of {}, {} already exists".format(remote_file, local_file))
    else:
        print("Downloading {} to {}".format(remote_file, local_dir))
        download(remote_file, local_dir)

    unpack(local_dir, local_file)


def download(remote_file, local_dir):
    """Download a remote file to a local directory
    """
    s3_ini = os.path.join(os.path.realpath(os.path.dirname(__file__)), 's3.ini')
    if not os.path.isfile(s3_ini):
        red = '\033[0;31m'
        nc = '\033[0m'  # No Color
        message = """\
        {red}No AWS config file {s3_ini} found.{nc}
        {red}Do you have s3 access credentials? Have you copied template.s3.ini?{nc}""".format(
            red=red,
            nc=nc,
            s3_ini=s3_ini
        )
        print(message)
        raise Exception

    # Ensure the local_dir exists
    print("Creating directory", local_dir)
    os.makedirs(local_dir, exist_ok=True)

    # Download data from s3
    try:
        # Set environment variables
        os.environ['AWS_CONFIG_FILE'] = s3_ini
        os.environ['AWS_PROFILE'] = 'nismod2-s3'

        # Set local location for downloaded file
        local_file = os.path.join(local_dir, os.path.basename(remote_file))

        # Retrieve file from s3 bucket
        s3_resource = boto3.resource('s3')
        s3_resource.Object('nismod2-data', remote_file).download_file(local_file)

    # Print message and quit
    except Exception as ex:
        red = '\033[0;31m'
        nc = '\033[0m'  # No Color
        msg = """\
{red}Unable to download {remote_file} from nismod2-data s3 bucket.{nc}
{red}Make sure s3.ini file contains the correct credentials and that{nc}
{red}the requested file exists in the s3 bucket.{nc}
        """.format(
            red=red,
            nc=nc,
            remote_file=remote_file
        )
        print(msg)
        raise ex


def unpack(local_dir, local_file):
    """Unpack downloaded ZIP files
    """
    subprocess.run(['unzip', '-o', local_file, '-d', local_dir])


if __name__ == '__main__':
    try:
        print("Called with", sys.argv)
        REMOTE = sys.argv[1]
        LOCAL = sys.argv[2]
    except IndexError:
        exit("Usage: python {} <remote_file> <local_dir>".format(__file__))
    main(REMOTE, LOCAL)
