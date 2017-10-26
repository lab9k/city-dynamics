from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime


class Melding(models.Model):
    # hoofdrubriek = models.CharField(max_length=255, default='empty')
    subrubriek = models.CharField(max_length=255, default='empty')
    beschrijving = models.CharField(max_length=255, default='empty')
    lat = models.CharField(max_length=255, default='empty')
    lng = models.CharField(max_length=255, default='empty')
    # timestamp = models.DateTimeField()

# objects = models.GeoManager()

# class Meta:
#     get_latest_by = "Aanmaakdatum_score"
