"""Unit tests for scripts/modules in the Analyzer"""


##############################################################################
# Import public modules
from pytest import approx
import unittest
import pandas as pd
import numpy as np
import copy
import q

# Import modules to test
import main
import process

##############################################################################
# Global variables
vollcodes_m2_land = {'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0, 'A04': 370827.0,
                     'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0, 'A08': 288812.0, 'A09': 429920.0,
                     'B10': 9365503.0, 'E12': 218000.0, 'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0,
                     'E16': 173372.0, 'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0,
                     'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0, 'E38': 193750.0,
                     'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0, 'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0,
                     'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0, 'F78': 567032.0, 'F79': 737444.0,
                     'F80': 5695263.0, 'F81': 678581.0, 'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0,
                     'F85': 622215.0, 'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0,
                     'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0, 'K44': 321894.0,
                     'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0, 'K48': 464700.0, 'K49': 419051.0,
                     'K52': 462443.0, 'K53': 125127.0, 'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0,
                     'K91': 1018235.0, 'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0,
                     'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0, 'M35': 1524659.0,
                     'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0, 'M57': 1777311.0, 'M58': 1553531.0,
                     'N60': 604294.0, 'N61': 489380.0, 'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0,
                     'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0, 'N70': 680151.0,
                     'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0, 'N74': 391998.0, 'T92': 691673.0,
                     'T93': 1310109.0, 'T94': 1817539.0, 'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0,
                     'T98': 2310156.0}

##############################################################################
class testMain(unittest.TestCase):
    """Test the main.py module."""

    def test_main(self):
        pass

##############################################################################
class testProcess(unittest.TestCase):
    """Test the process.py module."""

    def test_process(self):
        dbconfig = 'docker'

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
        x.import_data(['gvb'], ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])
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
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = x.data.halte.isin(haltes)
        gvb_buurt = x.data.loc[np.logical_not(indx), :]
        x.data = gvb_buurt.groupby(['vollcode', 'weekday', 'hour'])['incoming'].mean().reset_index()

        m2 = pd.DataFrame(list(vollcodes_m2_land.items()), columns=['vollcode', 'oppervlakte_land_m2'])

        col = 'incoming'
        before = copy.deepcopy(x.data)
        before = before.merge(m2)  # Merge to remove entries which also fall away in normalization

        x.normalize_acreage(col)
        after = x.data.merge(m2)
        after[col] = after[col] * after.oppervlakte_land_m2

        # Check whether all entries are the same after "un-normalizing" them.
        for i in range(0, len(before)):
            assert before[col][i] == approx(after[col][i])

##############################################################################

if __name__ == "__main__":
    testMain.test_main()
    testProcess.test_process()