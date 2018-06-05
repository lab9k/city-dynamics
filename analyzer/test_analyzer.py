"""
Unit tests for scripts/modules in the Analyzer

This module implements a list of unit tests for modules in the analyzer.
Most importantly, this modules (should) test the functionality of
main.py, process.py and hotspots_drukteindex.py.

This module is compatible pytest. It should automatically be ran as a
test in the Jenkins continuous integration cycle.
"""


##############################################################################
# Import public modules
from pytest import approx
import unittest
import pandas as pd
import numpy as np
import copy

# Import modules to test
import process

from main import vollcodes_m2_land


class testMain(unittest.TestCase):
    """Test the main.py module."""

    def test_main(self):
        """Run a set of unit tests for main.py."""
        pass


class testProcess(unittest.TestCase):
    """Test the process.py module."""

    def test_process(self):
        """Run a set of unit tests for process.py."""
        dbconfig = 'test'

        # 1. Create mini-table in database
        # 2. Test import_table
        # 2. Test import_data (import mini-table twice)

        # Create Process instance to test functions of Process class
        x = process.Process(dbconfig)
        x.name = "Test"

        # Test: Process > import_table
        table = x.import_table('gvb')
        assert len(table) > 0

        # Test: Process > import_data
        x.import_data(
            ['gvb'],
            ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])

        assert len(x.data) > 0

        # Test: Process > rename
        x.rename({'halte': 'test'})
        assert len(x.data.test) > 0
        x.rename({'test': 'halte'})

        # Test: Process > normalize
        x.normalize('incoming')
        x.normalize(['lat', 'lon'])
        assert min(x.data.incoming) == approx(0.0)
        assert max(x.data.incoming) == approx(1.0)
        assert min(x.data.lat) == approx(0.0)
        assert max(x.data.lat) == approx(1.0)
        assert min(x.data.lon) == approx(0.0)
        assert max(x.data.lon) == approx(1.0)

        # Test: Process > normalize_acreage
        csv = pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')
        haltes = list(csv['station'])
        indx = x.data.halte.isin(haltes)
        gvb_buurt = x.data.loc[np.logical_not(indx), :]
        grouped = gvb_buurt.groupby(['vollcode', 'weekday', 'hour'])
        x.data = grouped['incoming'].mean().reset_index()

        opervlakten_buurt = list(vollcodes_m2_land.items())
        m2 = pd.DataFrame(
            opervlakten_buurt, columns=['vollcode', 'oppervlakte_land_m2'])

        col = 'incoming'
        before = copy.deepcopy(x.data)
        # Merge to remove entries which also fall away in normalization
        before = before.merge(m2)

        x.normalize_acreage(col)
        after = x.data.merge(m2)
        after[col] = after[col] * after.oppervlakte_land_m2

        # Check whether all entries are the same after "un-normalizing" them.
        for i in range(0, len(before)):
            assert before[col][i] == approx(after[col][i])


if __name__ == "__main__":
    """Running this script as a stand-alone module should run
    all the tests and complete them without failures."""
    print("Starting tests now...")
    testMain.test_main()
    testProcess.test_process()
    print("Testing completed.")
