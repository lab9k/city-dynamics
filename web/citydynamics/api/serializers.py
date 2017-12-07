from django.contrib.gis.db import models
from django.http import HttpResponse, JsonResponse

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField
from citydynamics.api.models import Drukteindex


class DrukteindexSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Drukteindex
        geo_field = 'wkb_geometry'
        fields = ('naam', 'vollcode', 'drukte_index')

