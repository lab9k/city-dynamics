import requests
import datetime
import json

import expiringdict
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
# from django.db.models import Avg
from datapunt_api import rest
from . import models
from . import serializers
import logging

log = logging.getLogger(__name__)


def convert_to_date(input_date):
    try:
        date_obj = datetime.strptime(input_date, '%d-%m-%Y-%H-%M-%S')
    except ValueError:
        log.exception("Got an invalid date value")
        date_obj = None
    return date_obj


class BuurtcombinatieViewset(viewsets.ModelViewSet):
    """
    ViewSet for retrieving buurtcombinatie polygons
    """

    queryset = models.Buurtcombinatie.objects.order_by('naam')
    serializer_class = serializers.BuurtcombinatieSerializer


class DrukteindexBuurtcombinatieViewset(rest.DatapuntViewSet):
    """
    Buurtcombinatie drukteindex API
    """

    serializer_class = serializers.BCIndexSerializer
    serializer_detail_class = serializers.BCIndexSerializer

    filter_fields = (
        'druktecijfers_bc__weekday',
    )

    def get_queryset(self):

        queryset = (
            models.Buurtcombinatie.objects
            .prefetch_related('druktecijfers_bc')
            .order_by("naam")
        )

        vollcode = self.request.query_params.get('vollcode', None)
        if vollcode is not None:
            queryset = queryset.filter(hotspot=vollcode)

        return queryset


class HotspotViewset(viewsets.ModelViewSet):
    """
    ViewSet for retrieving hotspot polygons
    """

    queryset = models.Hotspots.objects.order_by('hotspot')
    serializer_class = serializers.HotspotSerializer


class DrukteindexHotspotViewset(rest.DatapuntViewSet):
    """
    Hotspot drukteindex API
    """

    serializer_class = serializers.HotspotIndexSerializer
    serializer_detail_class = serializers.HotspotIndexSerializer

    filter_fields = (
        'druktecijfers__weekday',
    )

    def get_queryset(self):

        queryset = (
            models.Hotspots.objects
            .prefetch_related('druktecijfers')
            .order_by("hotspot")
        )

        hotspot = self.request.query_params.get('hotspot', None)
        if hotspot is not None:
            queryset = queryset.filter(hotspot=hotspot)

        return queryset


class RealtimeFilter(FilterSet):

    realtime = filters.CharFilter(
        method="realtime_filter", label="realtime", name="realtime")

    class Meta:
        model = models.RealtimeGoogle
        fields = (
            'place_id',
            'scraped_at',
            'name',
            'realtime',
        )

    def realtime_filter(self, queryset, filter_name, value):
        try:
            float(value)
        except ValueError:
            raise ValidationError(
                f'{filter_name} field must be an float value.')

        qs = queryset.filter(**{'data__Real-time__gt': float(value)})
        return qs


class RealtimeGoogleViewset(rest.DatapuntViewSet):
    """
    Quantillion scraped data
    """
    serializer_class = serializers.RealtimeGoogleSerializer
    serializer_detail_class = serializers.RealtimeGoogleSerializer

    queryset = models.RealtimeGoogle.objects.order_by('name')

    filter_class = RealtimeFilter


class HistorianFilter(FilterSet):

    class Meta:
        model = models.RealtimeHistorian
        fields = (
            'place_id',
            'scraped_at',
            'name',
            'source',
        )


class HistorianViewset(rest.DatapuntViewSet):
    """
    Previous scraped data of external endpoints
    saved here for future analysis
    """
    serializer_class = serializers.HistorianSerializerList
    serializer_detail_class = serializers.HistorianSerializer

    queryset = models.RealtimeHistorian.objects.order_by('scraped_at')

    filter_class = HistorianFilter


PROXY_URLS = {
    # 'events': 'http://api.simfuny.com/app/api/2_0/events?callback=__ng_jsonp__.__req1.finished&offset=0&limit=25&sort=popular&search=&types[]=unlabeled&dates[]=today',  # noqa
    'events': 'http://api.simfuny.com/app/api/2_0/events?callback=__ng_jsonp__.__req8.finished&offset=0&limit=25&sort=popular&search=&types[]=unlabeled&dates[]=today&startDate=&endDate=&hidelongterm=1',  # noqa
    'parking_garages': 'http://opd.it-t.nl/data/amsterdam/ParkingLocation.json',    # noqa
    'traveltime': 'http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson',  # noqa
    'ovfiets': 'http://fiets.openov.nl/locaties.json',  # noqa
}

PARSING_DATA = {
    'parking_garages': 'geojson',
    'traveltime': 'geojson',
    'events': 'cleanup',
    'ovfiets': 'geojson',
}


def cleanup(api_response):
    """Cleanup some api cruft

    Return jons from response.
    """
    junk = "__ng_jsonp__.__req1.finished("
    junk = "__ng_jsonp__.__req8.finished("

    cleaned = ""

    # if api_response.startswith(junk):
    cleaned = api_response[len(junk):]

    tailjunk = ");"
    if cleaned.endswith(tailjunk):
        cleaned = cleaned[:-len(tailjunk)]

    return json.loads(cleaned)


cache = expiringdict.ExpiringDict(max_len=100, max_age_seconds=60)


def get_latest(api_source):

    try:
        latest = (
            models.RealtimeHistorian.objects
            .order_by('scraped_at')
            .filter(source=api_source).first()
        )
    except models.RealtimeHistorian.DoesNotExist:
        return None

    if not latest:
        return None

    if (datetime.datetime.now() - latest.scraped_at).seconds > 300:
        return None

    return latest.data


def store(api_source, data):
    """
    Store realtime suggestion
    """
    r = models.RealtimeHistorian.objects.create(
        scraped_at=datetime.datetime.now(),
        source=api_source,
        data=data,
    )
    r.save()


@api_view(['GET', ])
def api_proxy(request):
    """Proxy API to avoid cors headers. with a x minute cache.

    provide ?api=events, parking_garages, traveltime

    Historical data needs to be loaded later.
    """
    api_source = request.GET.get('api')

    options = list(PROXY_URLS.keys())

    r400 = Response(
        {"message": f"api parameters needs to be one of {options}"}, 400)

    r500 = Response(
        {"message": f"remote api failed"}, 500)

    if not api_source:
        return r400

    if api_source not in options:
        return r400

    # Get the lastest known realtime information
    data = get_latest(api_source)

    if data:
        log.info('From cache!')
        return Response(data)

    response = requests.get(PROXY_URLS[api_source])

    if response.status_code != 200:
        log.error('EXTERNAL API FAILED: %s', PROXY_URLS[api_source])
        return r500

    if api_source in PARSING_DATA:
        if PARSING_DATA[api_source] == 'geojson':
            data = response.json()
        if PARSING_DATA[api_source] == 'cleanup':
            data = cleanup(response.text)
    else:
        data = response.text

    if not data:
        log.error('EXT API DATA MISSING %s %s', api_source, data)
        # 598 (Informal convention) Network read timeout error
        return Response([], status_code=598)

    store(api_source, data)

    return Response(data)
