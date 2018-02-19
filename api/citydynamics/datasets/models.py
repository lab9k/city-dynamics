from django.db import models
from django.contrib.gis.db import models
from rest_framework import serializers
from datetime import datetime
from django.contrib.gis.db import models as geo


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
        db_table = 'buurtcombinatie'


class Drukteindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    vollcode = models.TextField(blank=True, null=True)
    weekday = models.BigIntegerField(blank=True, null=True)
    hour = models.BigIntegerField(blank=True, null=True)
    google_live = models.FloatField(blank=True, null=True)
    google_week = models.FloatField(blank=True, null=True)
    gvb_buurt = models.FloatField(blank=True, null=True)
    gvb_stad = models.FloatField(blank=True, null=True)
    verblijversindex = models.FloatField(blank=True, null=True)
    google = models.FloatField(blank=True, null=True)
    gvb = models.FloatField(blank=True, null=True)
    drukte_index = models.FloatField(blank=True, null=True)


class Hotspots(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.TextField(db_column='Hotspot', blank=True, null=True)
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)
    point_sm = models.GeometryField(srid=0, blank=True, null=True)


class HotspotsDrukteIndex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.ForeignKey('Hotspots', related_name='druktecijfers', on_delete=models.DO_NOTHING)
    hour = models.IntegerField()
    # weekday = models.IntegerField()
    drukteindex = models.FloatField()
