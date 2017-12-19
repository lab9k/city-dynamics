from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from datapunt_api import rest
from . import models
from . import serializers
import datetime

import logging

log = logging.getLogger(__name__)


def convert_to_date(input_date):
    try:
        date_obj = datetime.datetime.strptime(input_date, '%d-%m-%Y-%H-%M-%S')
        #date_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d-%H')
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

    # def datetime_filter(self, queryset, _name, value, **kwargs):
    #     date = convert_to_date(value)
    #     if not date:
    #         raise ValidationError(
    #             'Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 2017-10-26-16-00-00')
    #     log.debug(kwargs)
    #     queryset = queryset.filter(kwargs['timestamp'])

    #     return queryset

    # def op_filter(self, queryset, _name, value):
    #     queryset = datetime_filter(**{'timestamp':'date'})
    #     return queryset


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
    queryset = models.Drukteindex.objects.order_by("index")
    #filter_class = RecentIndexFilter

    # def latest_filter(self, queryset, _name, value):
    #     datetime = self.request.query_params.get('datetime', None)
    #     start_datetime = convert_to_date(datetime)
    #     end_datetime = start_datetime - datetime.timedelta(hours=24)
    #     queryset = queryset.filter(
    #         timestamp__range=(start_datetime, end_datetime))

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = models.Drukteindex.objects.all()

        vollcode = self.request.query_params.get('vollcode', None)
        if vollcode is not None:
            queryset = queryset.filter(vollcode=vollcode)

        timestamp_str = self.request.query_params.get('timestamp', None)

        if timestamp_str is None:
            timestamp_dt = datetime.datetime.now()

        if timestamp_str is not None:
            timestamp_dt = convert_to_date(timestamp_str)

        if timestamp_dt > convert_to_date('07-12-2017-00-00-00'):
            current_day = datetime.datetime.now().strftime("%A")
            if current_day == 'Friday':
                end_timestamp = '02-12-2017-23-00-00'
            elif current_day == 'Saturday':
                end_timestamp = '01-12-2017-23-00-00'
            elif current_day == 'Sunday':
                end_timestamp = '03-12-2017-23-00-00'
            elif current_day == 'Monday':
                end_timestamp = '04-12-2017-23-00-00'
            elif current_day == 'Tuesday':
                end_timestamp = '05-12-2017-23-00-00'
            elif current_day == 'Wednesday':
                end_timestamp = '06-12-2017-23-00-00'
            elif current_day == 'Thursday':
                end_timestamp = '07-12-2017-23-00-00'
            end_timestamp = convert_to_date(end_timestamp)

        else:
            end_timestamp = timestamp_dt

        start_timestamp = end_timestamp.replace(
            hour=1, minute=0, second=0, microsecond=0)
        # start_timestamp = end_timestamp - datetime.timedelta(hours=23)
        end_timestamp = end_timestamp + datetime.timedelta(days=1)
        end_timestamp = end_timestamp.replace(
            hour=0, minute=0, second=0, microsecond=0)

        queryset = queryset.filter(
            timestamp__range=(start_timestamp, end_timestamp))

        return queryset
