from django.contrib.gis.db import models
from django.http import HttpResponse, JsonResponse

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from citydynamics.api.models import Gvb

# class MeldingSerializer(GeoFeatureModelSerializer):
#     """ A class to serialize locations as GeoJSON compatible data """

#     class Meta:
#         model = LengteGewicht
#         geo_field = 'Geom'
#         fields = 'Hoofdrubriek', 'Subrubriek', 'Datummelding'


# class GvbSerializer(GeoFeatureModelSerializer):
#     """ A class to serialize locations as GeoJSON compatible data """

#     class Meta:
#         model = Gvb
#         #geo_field = 'geom'
#         fields = ('halte', 'timestamp', 'incoming', 'outgoing')

class GvbSerializer(serializers.ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Gvb
        #geo_field = 'geom'
        fields = ('halte', 'timestamp', 'incoming', 'outgoing')