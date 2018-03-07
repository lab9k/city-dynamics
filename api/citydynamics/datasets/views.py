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


class DateFilter(FilterSet):
    vanaf = filters.CharFilter(label='vanaf', method='vanaf_filter')
    tot = filters.CharFilter(label='tot', method='tot_filter')
    op = filters.CharFilter(label='op', method='op_filter')

    class Meta:
        model = models.Drukteindex
        fields = [
            'timestamp',
            'vanaf',
            'tot',
            'op',
            'vollcode'
        ]

    def vanaf_filter(self, queryset, _name, value):
        date = convert_to_date(value)
        if not date:
            raise ValidationError(
                'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')
        queryset = queryset.filter(timestamp__gte=date)

        return queryset

    def tot_filter(self, queryset, _name, value):
        date = convert_to_date(value)
        if not date:
            raise ValidationError(
                'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')
        queryset = queryset.filter(timestamp__lte=date)

        return queryset

    def op_filter(self, queryset, _name, value):
        date = convert_to_date(value)
        if not date:
            raise ValidationError(
                'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 26-10-2017-16-00-00')
        queryset = queryset.filter(timestamp=date)

        return queryset


class DrukteindexViewSet(rest.DatapuntViewSet):
    """
    Drukteindex API
    """

    serializer_class = serializers.DrukteIndexSerializer
    serializer_detail_class = serializers.DrukteIndexSerializer
    queryset = models.Drukteindex.objects.order_by("index")
    filter_class = DateFilter


class RecentIndexViewSet(rest.DatapuntViewSet):
    """
    Recent index API
    """

    serializer_class = serializers.RecentIndexSerializer
    serializer_detail_class = serializers.RecentIndexSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = models.Drukteindex.objects.all().order_by("index")

        vollcode = self.request.query_params.get('vollcode', None)
        if vollcode is not None:
            queryset = queryset.filter(vollcode=vollcode)

        timestamp_str = self.request.query_params.get('timestamp', None)

        if timestamp_str is None:
            timestamp_dt = datetime.now()

        if timestamp_str is not None:
            timestamp_dt = convert_to_date(timestamp_str)

        if timestamp_dt > convert_to_date('07-12-2017-00-00-00'):
            current_day = timestamp_dt.strftime("%A")
            if current_day == 'Friday':
                timestamp_dt = '02-12-2017-23-00-00'
            elif current_day == 'Saturday':
                timestamp_dt = '01-12-2017-23-00-00'
            elif current_day == 'Sunday':
                timestamp_dt = '03-12-2017-23-00-00'
            elif current_day == 'Monday':
                timestamp_dt = '04-12-2017-23-00-00'
            elif current_day == 'Tuesday':
                timestamp_dt = '05-12-2017-23-00-00'
            elif current_day == 'Wednesday':
                timestamp_dt = '06-12-2017-23-00-00'
            elif current_day == 'Thursday':
                timestamp_dt = '07-12-2017-23-00-00'
            timestamp_dt = convert_to_date(timestamp_dt)

        today = timestamp_dt.date()

        level = self.request.query_params.get('level', None)
        if level == 'day':
            queryset = queryset.filter(timestamp__date=today)
            # exclude = ('weekday',)

        if level == 'week':
            yesterday = today - timedelta(days=1)
            previous_week = yesterday - timedelta(days=7)
            queryset = queryset.filter(
                timestamp__gte=previous_week, timestamp__lt=yesterday)
            current_hour = timestamp_dt.hour
            queryset = queryset.filter(timestamp__hour=current_hour)

        return queryset


class BuurtcombinatieViewset(viewsets.ModelViewSet):
    """
    ViewSet for retrieving buurtcombinatie polygons
    """

    queryset = models.Buurtcombinatie.objects.all()
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
            #.order_by("naam")
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

    queryset = models.RealtimeGoogle.objects.all()
