from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from citydynamics.api.models import Drukteindex, Buurtcombinatie


class DrukteIndexSerializer(ModelSerializer):

    class Meta:
        model = Drukteindex
        fields = ('vollcode', 'drukte_index')


class RecentIndexSerializer(ModelSerializer):

    class Meta:
        model = Drukteindex
        fields = ('drukte_index', 'timestamp', 'weekday')

class BuurtcombinatieSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Buurtcombinatie
        geo_field = 'wkb_geometry_simplified'
        fields = ('vollcode', 'naam')