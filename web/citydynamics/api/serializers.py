from rest_framework.serializers import ModelSerializer
from citydynamics.api.models import Drukteindex


class DrukteIndexSerializer(ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Drukteindex
        # geo_field = 'wkb_geometry'
        fields = ('vollcode', 'drukte_index')

class RecentIndexSerializer(ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Drukteindex
        fields = ('drukte_index', 'timestamp')