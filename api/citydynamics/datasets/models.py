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


class BuurtCombinatieDrukteindex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    vollcode = models.ForeignKey(
        'Buurtcombinatie',
        related_name='druktecijfers_bc', on_delete=models.DO_NOTHING)
    hour = models.IntegerField()
    weekday = models.IntegerField()
    drukteindex = models.FloatField()


class GVB(models.Model):
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
    stadsdeelcode = models.CharField(max_length=255, blank=True, null=True)
    hotspot = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'gvb'


class Hotspots(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    is_alpha_hotspot = models.BigIntegerField(blank=True, null=True)
    alpha_hotspot_name = models.TextField(blank=True, null=True)
    polygon = models.GeometryField(srid=0, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    centroid = models.GeometryField(srid=0, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    stadsdeelcode = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'hotspots'


class HotspotsDrukteIndex(models.Model):
    index = models.BigIntegerField(primary_key=True)
    hotspot = models.ForeignKey(
        'Hotspots', related_name='druktecijfers', on_delete=models.DO_NOTHING)
    hour = models.IntegerField()
    weekday = models.IntegerField()
    drukteindex = models.FloatField()


class RealtimeAnalyzer(models.Model):
    scraped_at = models.DateTimeField(blank=True, null=False, auto_now_add=True)
    ov_fiets_crowdedness_score = models.FloatField(blank=True, null=True)
    ndw_crowdedness_score = models.FloatField(blank=True, null=True)
    pr_crowdedness_score = models.FloatField(blank=True, null=True)
    knmi_crowdedness_score = models.FloatField(blank=True, null=True)
    weercijfer = models.FloatField(blank=True, null=True)
    combined_crowdedness_score = models.FloatField(blank=True, null=True)
    diff = models.FloatField(blank=True, null=True)
    alp_mean = models.FloatField(blank=True, null=True)
    alp_count = models.FloatField(blank=True, null=True)
    diff = models.FloatField(blank=True, null=True)
    w_fiets = models.FloatField(blank=True, null=True)
    w_ndw = models.FloatField(blank=True, null=True)
    w_pr = models.FloatField(blank=True, null=True)
    w_knmi = models.FloatField(blank=True, null=True)
    w_weer = models.FloatField(blank=True, null=True)


class RealtimeGoogle(models.Model):

    place_id = models.TextField(db_index=True)
    scraped_at = models.DateTimeField(blank=True, null=True)
    name = models.TextField()
    data = JSONField()

    class Meta:
        db_table = f'google_raw_locations_realtime_current_{settings.ENVIRONMENT}'   # noqa


class RealtimeHistorian(models.Model):
    """
    From serveral realtime endpoints keep data here
    for analyzing purpose
    """

    place_id = models.TextField(db_index=True)
    scraped_at = models.DateTimeField(blank=True, null=False, auto_now_add=True)
    name = models.TextField(null=True)
    source = models.CharField(max_length=40, null=False)
    data = JSONField()
