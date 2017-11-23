from django.db import models
from django.contrib.gis.db import models
from rest_framework import serializers
from datetime import datetime

# objects = models.GeoManager()

class Buurtcombinatie(models.Model):
    index = models.BigIntegerField(primary_key=True)
    objectnummer = models.BigIntegerField(db_column='OBJECTNUMMER', blank=True, null=True)  # Field name made lowercase.
    buurtcombinatie_code = models.TextField(db_column='Buurtcombinatie_code', blank=True, null=True)  # Field name made lowercase.
    buurtcombinatie = models.TextField(db_column='Buurtcombinatie', blank=True, null=True)  # Field name made lowercase.
    stadsdeel_code = models.TextField(db_column='Stadsdeel_code', blank=True, null=True)  # Field name made lowercase.
    opp_m2 = models.BigIntegerField(db_column='Opp_m2', blank=True, null=True)  # Field name made lowercase.
    coords = models.TextField(db_column='COORDS', blank=True, null=True)  # Field name made lowercase.
    lng = models.TextField(db_column='LNG', blank=True, null=True)  # Field name made lowercase.
    lat = models.TextField(db_column='LAT', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'buurtcombinatie'


class Gvb(models.Model):
    index = models.BigIntegerField(primary_key=True)
    halte = models.TextField(blank=True, null=True)
    incoming = models.BigIntegerField(blank=True, null=True)
    outgoing = models.BigIntegerField(blank=True, null=True)
    day_numeric = models.BigIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gvb'