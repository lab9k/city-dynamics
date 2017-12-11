from rest_framework.serializers import ModelSerializer
from citydynamics.api.models import Drukteindex


class DrukteindexSerializer(ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Drukteindex
        # geo_field = 'wkb_geometry'
        fields = ('naam', 'vollcode', 'drukte_index')
