from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from citydynamics.datasets.models import Drukteindex, Buurtcombinatie
from citydynamics.datasets.models import Hotspots, HotspotsDrukteIndex
from citydynamics.datasets.models import RealtimeGoogle
import datetime


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


class CijferSerializer(ModelSerializer):

    h = serializers.IntegerField(source='hour')
    d = serializers.FloatField(source='drukteindex')

    class Meta:
        model = HotspotsDrukteIndex
        fields = (
            'h',
            'd',
        )


class HotspotIndexSerializer(ModelSerializer):

    # druktecijfers = CijferSerializer(many=True, read_only=True)

    coordinates = SerializerMethodField()
    druktecijfers = SerializerMethodField()

    def get_coordinates(self, obj):
        return [obj.latitude, obj.longitude]

    class Meta:
        model = Hotspots
        fields = (
            'index',
            'hotspot',
            'coordinates',
            'druktecijfers',
        )

    def get_druktecijfers(self, obj):
        weekday = datetime.datetime.today().weekday()
        cijfers = obj.druktecijfers.filter(weekday=weekday)

        return CijferSerializer(cijfers, many=True).data


class RealtimeGoogleSerializer(ModelSerializer):

    class Meta:
        model = RealtimeGoogle
        fields = (
            'scraped_at',
            'name',
            'place_id',
            'data'
        )


# class HotspotIndexSerializer(ModelSerializer):
#     coordinates = SerializerMethodField()
#
#     def get_coordinates(self, obj):
#         return [obj.latitude, obj.longitude]
#
#
#     class Meta:
#         model = Hotspots
#         fields = ('index', 'hotspot', 'coordinates', 'drukte')
