from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from django.db.models import Avg
import requests
import expiringdict

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
    # filter_class = HotspotF

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


class DrukteindexHotspotViewset(rest.DatapuntViewSet):
    """
    Hotspot drukteindex API
    """

    serializer_class = serializers.HotspotIndexSerializer
    serializer_detail_class = serializers.HotspotIndexSerializer
    # filter_class = HotspotF
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


class RealtimeGoogleViewset(rest.DatapuntViewSet):
    """
    Quantillion scraped data
    """
    serializer_class = serializers.RealtimeGoogleSerializer
    serializer_detail_class = serializers.RealtimeGoogleSerializer

    queryset = models.RealtimeGoogle.objects.order_by('name')


PROXY_URLS = {
    'events': 'http://api.simfuny.com/app/api/2_0/events?callback=__ng_jsonp__.__req1.finished&offset=0&limit=25&sort=popular&search=&types[]=unlabeled&dates[]=today',  # noqa
    'parking_garages': 'http://opd.it-t.nl/data/amsterdam/ParkingLocation.json',    # noqa
    'traveltime': 'http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson',  # noqa
}

PARSING_DATA = {
    'parking_garages': 'geojson',
    'traveltime': 'geojson',
}


cache = expiringdict.ExpiringDict(max_len=100, max_age_seconds=60)


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

    data = cache.get(api_source)

    if data:
        log.error('from cache!')

    if not data:
        # only allow 1 request every 60 seconds
        response = requests.get(PROXY_URLS[api_source])

        if response.status_code != 200:
            return r500

        if api_source in PARSING_DATA:
            data = response.json()
        else:
            data = response.text

        cache[api_source] = data

    return Response(data)
