from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from schoonmonitor.api.models import Melding


class MeldingSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Melding
        geo_field = 'Geom'
        fields = 'Hoofdrubriek', 'Subrubriek', 'Datummelding'