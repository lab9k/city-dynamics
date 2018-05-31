import os
import pandas as pd

source_file = 'Samenvoegingverblijvers2016_Tamas.xlsx'


def parse(datadir, filename=source_file):
    """Parser for verblijversindex data."""

    path = os.path.join(datadir, filename)
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
    df.rename(
        columns={
            'wijk': 'vollcode',
            'aantal inwoners': 'inwoners',
            'aantal werkzame personen': 'werkzame_personen',
            'aantal studenten': 'studenten',
            'aantal  bezoekers (met correctie voor onderlinge overlap)': 'bezoekers',     # noqa
            'som alle verblijvers': 'verblijvers',
            'oppervlakte land in vierkante meters': 'oppervlakte_land_m2',
            'oppervlakte land en water in vierkante meter': 'oppervlakte_land_water_m2',   # noqa
            'verbl. Per HA (land) 2016': 'verblijvers_ha_2016'},
        inplace=True)

    df = df.head(98)  # Remove last two rows (no relevant data there)
    return df
