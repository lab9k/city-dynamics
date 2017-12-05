from django.db import models
from django.contrib.gis.db import models
from rest_framework import serializers
from datetime import datetime

# objects = models.GeoManager()

class Verblijversindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    wijk = models.TextField(blank=True, null=True)
    oppervlakte_m2 = models.FloatField(blank=True, null=True)
    verblijversindex = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'VERBLIJVERSINDEX'


class Buurt(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    gml_id = models.CharField(max_length=255)
    id = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.GeometryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buurt'


class Buurtcombinatie(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    gml_id = models.CharField(max_length=255)
    id = models.CharField(max_length=255, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.GeometryField(blank=True, null=True)
    wkb_geometry_simplified = models.GeometryField(srid=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buurtcombinatie'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Drukteindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    vollcode = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    normalized_x = models.FloatField(blank=True, null=True)
    normalized_y = models.FloatField(blank=True, null=True)
    oppervlakte_m2 = models.FloatField(blank=True, null=True)
    normalized_m2 = models.FloatField(blank=True, null=True)
    normalized_index = models.FloatField(blank=True, null=True)
    ogc_fid = models.BigIntegerField(blank=True, null=True)
    gml_id = models.TextField(blank=True, null=True)
    id = models.TextField(blank=True, null=True)
    naam = models.TextField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    uri = models.TextField(blank=True, null=True)
    wkb_geometry = models.TextField(blank=True, null=True)
    wkb_geometry_simplified = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'drukteindex'


class Functiekaart(models.Model):
    index = models.BigIntegerField(primary_key=True)
    objectnummer = models.BigIntegerField(db_column='OBJECTNUMMER', blank=True, null=True)  # Field name made lowercase.
    functie2_oms = models.TextField(db_column='FUNCTIE2_OMS', blank=True, null=True)  # Field name made lowercase.
    zaaknaam = models.TextField(db_column='ZAAKNAAM', blank=True, null=True)  # Field name made lowercase.
    functie2_eng = models.TextField(db_column='FUNCTIE2_ENG', blank=True, null=True)  # Field name made lowercase.
    functie1_id = models.TextField(db_column='FUNCTIE1_ID', blank=True, null=True)  # Field name made lowercase.
    functie1_oms = models.TextField(db_column='FUNCTIE1_OMS', blank=True, null=True)  # Field name made lowercase.
    functie1_eng = models.TextField(db_column='FUNCTIE1_ENG', blank=True, null=True)  # Field name made lowercase.
    functie2_id = models.TextField(db_column='FUNCTIE2_ID', blank=True, null=True)  # Field name made lowercase.
    laag = models.BigIntegerField(db_column='LAAG', blank=True, null=True)  # Field name made lowercase.
    adressen_lijst = models.TextField(db_column='ADRESSEN_LIJST', blank=True, null=True)  # Field name made lowercase.
    adressen_vot = models.TextField(db_column='ADRESSEN_VOT', blank=True, null=True)  # Field name made lowercase.
    adressen_aantal = models.BigIntegerField(db_column='ADRESSEN_AANTAL', blank=True, null=True)  # Field name made lowercase.
    oppervlakte_som = models.BigIntegerField(db_column='OPPERVLAKTE_SOM', blank=True, null=True)  # Field name made lowercase.
    oppervlakte_nul = models.BigIntegerField(db_column='OPPERVLAKTE_NUL', blank=True, null=True)  # Field name made lowercase.
    checkdatum = models.TextField(db_column='CHECKDATUM', blank=True, null=True)  # Field name made lowercase.
    zaak_id = models.BigIntegerField(db_column='ZAAK_ID', blank=True, null=True)  # Field name made lowercase.
    coords = models.TextField(db_column='COORDS', blank=True, null=True)  # Field name made lowercase.
    lng = models.TextField(db_column='LNG', blank=True, null=True)  # Field name made lowercase.
    lat = models.TextField(db_column='LAT', blank=True, null=True)  # Field name made lowercase.
    unnamed_19 = models.FloatField(db_column='Unnamed: 19', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'functiekaart'


class Gebiedsgerichtwerken(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    gml_id = models.CharField(max_length=255)
    id = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.GeometryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gebiedsgerichtwerken'


class Google(models.Model):
    index = models.BigIntegerField(primary_key=True)
    location = models.TextField(db_column='Location', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(blank=True, null=True)
    historical = models.FloatField(blank=True, null=True)
    live = models.FloatField(blank=True, null=True)
    place_id = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    types = models.TextField(blank=True, null=True)
    differences = models.FloatField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'google'


class GoogleWithBc(models.Model):
    index = models.BigIntegerField(primary_key=True)
    location = models.TextField(db_column='Location', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(blank=True, null=True)
    historical = models.FloatField(blank=True, null=True)
    live = models.FloatField(blank=True, null=True)
    place_id = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    types = models.TextField(blank=True, null=True)
    differences = models.FloatField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    stadsdeel_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'google_with_bc'


class Gvb(models.Model):
    index = models.BigIntegerField(primary_key=True)
    halte = models.TextField(blank=True, null=True)
    incoming = models.BigIntegerField(blank=True, null=True)
    outgoing = models.BigIntegerField(blank=True, null=True)
    day_numeric = models.BigIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gvb'


class GvbWithBc(models.Model):
    index = models.BigIntegerField(primary_key=True)
    halte = models.TextField(blank=True, null=True)
    incoming = models.BigIntegerField(blank=True, null=True)
    outgoing = models.BigIntegerField(blank=True, null=True)
    day_numeric = models.BigIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    stadsdeel_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gvb_with_bc'


class Mora(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hoofdrubriek = models.TextField(blank=True, null=True)
    subrubriek = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mora'


class MoraWithBc(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hoofdrubriek = models.TextField(blank=True, null=True)
    subrubriek = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    geom = models.GeometryField(srid=0, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    stadsdeel_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mora_with_bc'


class Stadsdeel(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    gml_id = models.CharField(max_length=255)
    id = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.GeometryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stadsdeel'


class Tellus(models.Model):
    index = models.BigIntegerField(primary_key=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    meetwaarde = models.BigIntegerField(blank=True, null=True)
    representatief = models.BigIntegerField(blank=True, null=True)
    richting = models.BigIntegerField(blank=True, null=True)
    richting_1 = models.TextField(db_column='richting 1', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    richting_2 = models.TextField(db_column='richting 2', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    timestamp_from = models.DateTimeField(db_column='timestamp from', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    timestamp_to = models.DateTimeField(db_column='timestamp to', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    geom = models.GeometryField(srid=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tellus'


class TellusWithBc(models.Model):
    index = models.BigIntegerField(primary_key=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    meetwaarde = models.BigIntegerField(blank=True, null=True)
    representatief = models.BigIntegerField(blank=True, null=True)
    richting = models.BigIntegerField(blank=True, null=True)
    richting_1 = models.TextField(db_column='richting 1', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    richting_2 = models.TextField(db_column='richting 2', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    timestamp_from = models.DateTimeField(db_column='timestamp from', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    timestamp_to = models.DateTimeField(db_column='timestamp to', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    geom = models.GeometryField(srid=0, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    stadsdeel_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tellus_with_bc'

