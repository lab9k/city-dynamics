import pandas as pd
import os
from .parse_helper_functions import DatabaseInteractions
import logging

logger = logging.getLogger(__name__)


def main(conn, data_root, **config):
    """Parser for verblijversindex data."""

    logger.debug('Parsing verblijversindex...')

    folder_path = os.path.join(data_root, config['OBJECTSTORE_CONTAINER'])
    path = os.path.join(folder_path, config['FILENAME'])
    df = pd.read_excel(path, sheet_name=3)

    cols = ['wijk',
            'aantal inwoners',
            'aantal werkzame personen',
            'aantal studenten',
            'aantal  bezoekers (met correctie voor onderlinge overlap)',
            'som alle verblijvers',
            'oppervlakte land in vierkante meters',
            'oppervlakte land en water in vierkante meter',
            'verbl. Per HA (land) 2016']

    df = df[cols]

    # pandas.to_sql can't handle brackets within column names
    df.rename(columns={ 'wijk': 'vollcode',
                        'aantal inwoners': 'inwoners',
                        'aantal werkzame personen': 'werkzame_personen',
                        'aantal studenten': 'studenten',
                        'aantal  bezoekers (met correctie voor onderlinge overlap)': 'bezoekers',
                        'som alle verblijvers': 'verblijvers',
                        'oppervlakte land in vierkante meters': 'oppervlakte_land_m2',
                        'oppervlakte land en water in vierkante meter': 'oppervlakte_land_water_m2',
                        'verbl. Per HA (land) 2016': 'verblijvers_ha_2016'}, inplace=True)

    df = df.head(98)  # Remove last two rows (no relevant data there)

    df.to_sql('verblijversindex', con=conn, if_exists='replace')

    logger.debug('... done')
