"""
Restore and backup scripts
"""
import os
import logging
import datetime
import argparse

from slurp_api import ENDPOINT_MODEL
import models

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def rename_dump(filepath):
    """
    Give an indication of timeseries/environemnt of the database dump
    """
    filepath = filepath[0]

    if not os.path.isfile(filepath):
        raise(ValueError("File not found {filepath}"))

    session = models.Session()
    realtime_model = ENDPOINT_MODEL['realtime']
    expected_model = ENDPOINT_MODEL['expected']
    realtime_count = session.query(realtime_model).count()
    expected_count = session.query(expected_model).count()

    log.debug('Realtime Count %d', realtime_count)
    log.debug('Expected Count %d', expected_count)

    now = datetime.datetime.now()
    # last - first date
    prefix = filepath.split('.')[0]
    new_name = f'{prefix}{now}expected{expected_count}-realtime{realtime_count}.dump'
    log.debug(f'renameing to {new_name}')

    os.rename(filepath, new_name)


def main(args):
    """
    """
    pass


if __name__ == '__main__':

    desc = "Restore Scrape goolge quantillion api data"
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        '--rename_dump',
        type=str,
        help="rename given database dump",
        nargs=1
    )

    inputparser.add_argument(
        '--restore',
        type=str,
        default=False,
        nargs=1,
        help="restore given dump"
    )

    args = inputparser.parse_args()
    main(args)
