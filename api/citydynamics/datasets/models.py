from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from django.conf import settings


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
    wkb_geometry_simplified = models.GeometryField(
        srid=0, blank=True, null=True)

    class Meta:
        db_table = 'buurtcombinatie'


class Drukteindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    vollcode = models.TextField(blank=True, null=True)
    weekday = models.BigIntegerField(blank=True, null=True)
    hour = models.BigIntegerField(blank=True, null=True)
    alpha_live = models.FloatField(blank=True, null=True)
    alpha_week = models.FloatField(blank=True, null=True)
    gvb_buurt = models.FloatField(blank=True, null=True)
    gvb_stad = models.FloatField(blank=True, null=True)
    inwoners = models.FloatField(blank=True, null=True)
    werkzame_personen = models.FloatField(blank=True, null=True)
    studenten = models.FloatField(blank=True, null=True)
    bezoekers = models.FloatField(blank=True, null=True)
    verblijvers = models.FloatField(blank=True, null=True)
    oppervlakte_land_m2 = models.FloatField(blank=True, null=True)
    oppervlakte_land_water_m2 = models.FloatField(blank=True, null=True)
    verblijvers_ha_2016 = models.FloatField(blank=True, null=True)
    alpha = models.FloatField(blank=True, null=True)
    gvb = models.FloatField(blank=True, null=True)
    drukteindex = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'drukteindex_DUPLICAAT'


class BuurtCombinatieDrukteindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    vollcode = models.ForeignKey(
        'Buurtcombinatie',
        related_name='druktecijfers_bc', on_delete=models.DO_NOTHING)
    hour = models.IntegerField()
    weekday = models.IntegerField()
    drukteindex = models.FloatField()


class Hotspots(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.TextField(db_column='Hotspot', blank=True, null=True)
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)
    point_sm = models.GeometryField(srid=0, blank=True, null=True)


class HotspotsDrukteIndex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.ForeignKey(
        'Hotspots', related_name='druktecijfers', on_delete=models.DO_NOTHING)
    hour = models.IntegerField()
    weekday = models.IntegerField()
    drukteindex = models.FloatField()


class RealtimeGoogle(models.Model):

    place_id = models.TextField(db_index=True)
    scraped_at = models.DateTimeField(blank=True, null=True)
    name = models.TextField()
    data = JSONField()

    class Meta:
        db_table = f'google_raw_locations_realtime_current_{settings.ENVIRONMENT}'  # noqa
