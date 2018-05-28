

def load_areas():
    """Load 'stadsdeel' and 'buurtcombinatie' tables into database."""
    pg_str = db_int.get_postgresql_string()
    LoadLayers.load_layers(pg_str)