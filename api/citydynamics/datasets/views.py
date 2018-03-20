from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.serializers import ValidationError
from rest_framework import viewsets
# from django.db.models import Avg

from datapunt_api import rest
from . import models
from . import serializers
from datetime import datetime, timedelta
import logging

log = logging.getLogger(__name__)


def convert_to_date(input_date):
    try:
        date_obj = datetime.strptime(input_date, '%d-%m-%Y-%H-%M-%S')
    except ValueError:
        log.exception("Got an invalid date value")
        date_obj = None
    return date_obj


# class DateFilter(FilterSet):
#     vanaf = filters.CharFilter(label='vanaf', method='vanaf_filter')
#     tot = filters.CharFilter(label='tot', method='tot_filter')
#     op = filters.CharFilter(label='op', method='op_filter')
#
#     class Meta:
#         model = models.Drukteindex
#         fields = [
#             'timestamp',
#             'vanaf',
#             'tot',
#             'op',
#             'vollcode'
#         ]
#
#     def vanaf_filter(self, queryset, _name, value):
#         date = convert_to_date(value)
#         if not date:
#             raise ValidationError(
#                 'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')  # noqa
#         queryset = queryset.filter(timestamp__gte=date)
#
#         return queryset
#
#     def tot_filter(self, queryset, _name, value):
#         date = convert_to_date(value)
#         if not date:
#             raise ValidationError(
#                 'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')  # noqa
#         queryset = queryset.filter(timestamp__lte=date)
#
#         return queryset
#
#     def op_filter(self, queryset, _name, value):
#         date = convert_to_date(value)
#         if not date:
#             raise ValidationError(
#                 'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')   # noqa
#         queryset = queryset.filter(timestamp=date)
#
#         return queryset


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
