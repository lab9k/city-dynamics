from rest_framework.serializers import ModelSerializer
from citydynamics.api.models import Drukteindex


class DrukteIndexSerializer(ModelSerializer):

    class Meta:
        model = Drukteindex
        # geo_field = 'wkb_geometry'
        fields = ('vollcode', 'drukte_index')


class RecentIndexSerializer(ModelSerializer):

    class Meta:
        model = Drukteindex
        fields = ('drukte_index', 'timestamp', 'weekday')
