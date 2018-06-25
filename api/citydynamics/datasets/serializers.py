from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from citydynamics.datasets.models import Buurtcombinatie
from citydynamics.datasets.models import BuurtCombinatieDrukteindex
from citydynamics.datasets.models import Hotspots, HotspotsDrukteIndex
from citydynamics.datasets.models import RealtimeGoogle
from citydynamics.datasets.models import RealtimeHistorian
import datetime


class BuurtcombinatieSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Buurtcombinatie
        geo_field = 'wkb_geometry_simplified'
        fields = ('vollcode', 'naam')


class BCCijferSerializer(ModelSerializer):

    h = serializers.IntegerField(source='hour')
    d = serializers.IntegerField(source='weekday')
    i = serializers.FloatField(source='drukteindex')

    class Meta:
        model = BuurtCombinatieDrukteindex
        fields = (
            'h',
            'd',
            'i',
        )


class BCIndexSerializer(ModelSerializer):

    druktecijfers_bc = SerializerMethodField()

    class Meta:
        model = Buurtcombinatie
        fields = (
            'ogc_fid',
            'naam',
            'vollcode',
            'druktecijfers_bc',
        )

    def get_druktecijfers_bc(self, obj):
        today_wkday = datetime.datetime.today().weekday()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_wkday = tomorrow.weekday()
        cijfers = obj.druktecijfers_bc.filter(weekday__in=[today_wkday, tomorrow_wkday])

        return BCCijferSerializer(cijfers, many=True).data


class HotspotSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    # coordinates = SerializerMethodField()

    # def get_coordinates(self, obj):
    #    return [obj.lat, obj.lon]

    class Meta:
        model = Hotspots
        # geo_field = 'polygon'
        geo_field = 'centroid'
        # fields = ('index', 'hotspot', 'coordinates',)
        fields = ('index', 'hotspot',)


class HotspotCijferSerializer(ModelSerializer):

    h = serializers.IntegerField(source='hour')
    d = serializers.IntegerField(source='weekday')
    i = serializers.FloatField(source='drukteindex')

    class Meta:
        model = HotspotsDrukteIndex
        fields = (
            'h',
            'd',
            'i',
        )


class HotspotIndexSerializer(ModelSerializer):

    druktecijfers = SerializerMethodField()

    class Meta:
        model = Hotspots
        fields = (
            'index',
            'hotspot',
            'druktecijfers',
        )

    def get_druktecijfers(self, obj):
        today_wkday = datetime.datetime.today().weekday()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_wkday = tomorrow.weekday()
        cijfers = obj.druktecijfers.filter(weekday__in=[today_wkday, tomorrow_wkday])

        return HotspotCijferSerializer(cijfers, many=True).data


class RealtimeGoogleSerializer(ModelSerializer):

    class Meta:
        model = RealtimeGoogle
        fields = (
            'scraped_at',
            'name',
            'place_id',
            'data',
        )


class HistorianSerializerList(ModelSerializer):
    """
    For external url endpoints store historial data
    """
    class Meta:
        model = RealtimeHistorian
        fields = (
            'scraped_at',
            'name',
            'source',
            'data',
        )


class HistorianSerializer(ModelSerializer):
    """
    For external url endpoints store historial data
    """

    class Meta:
        model = RealtimeHistorian
        fields = (
            'scraped_at',
            'name',
            'source',
            'place_id',
            'data',
        )
