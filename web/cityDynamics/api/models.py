from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime


class LengteGewicht(models.Model):
	Lengte = models.CharField(max_length=255)
	Gewicht = models.CharField(max_length=255)

# objects = models.GeoManager()

# class Meta:
#     get_latest_by = "Aanmaakdatum_score"
