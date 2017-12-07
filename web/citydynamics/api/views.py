from django.views.generic import TemplateView
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.serializers import ValidationError

from datapunt_api import rest
from . import models
from . import serializers
import datetime
import django_filters

def convert_to_date(input_date):
    try:
        date_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d-%H-%M-%S')
    except:
        date_obj = None
    return date_obj

class DateFilter(FilterSet):
    #datetime = django_filters.DateTimeFilter(action=filter_on_date)

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
            raise ValidationError('Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 2017-10-26-16-00-00')
        queryset = queryset.filter(timestamp__gte=date)

        return queryset

    def tot_filter(self, queryset, _name, value):
        date = convert_to_date(value)
        if not date:
            raise ValidationError('Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 2017-10-26-16-00-00')
        queryset = queryset.filter(timestamp__lte=date)

        return queryset

    def op_filter(self, queryset, _name, value):
        date = convert_to_date(value)
        if not date:
            raise ValidationError('Please insert a datetime Year-Month-Day-Hour-Minute-Second, like: 2017-10-26-16-00-00')
        queryset = queryset.filter(timestamp=date)

        return queryset


class DrukteindexViewSet(rest.DatapuntViewSet):
    """
    Drukteindex API
    """

    serializer_class = serializers.DrukteindexSerializer
    serializer_detail_class = serializers.DrukteindexSerializer
    queryset = models.Drukteindex.objects.all()
    filter_class = DateFilter

    # def get_queryset(self):
    #     queryset = models.Drukteindex.objects.all()
    #     datetime = self.request.query_params.get('datetime', None)
    #     if datetime is not None:
    #         queryset = models.Drukteindex.objects.filter(timestamp=datetime)
    #     return queryset


    # def get_queryset(self, *args, **kwargs):
    #     _, queryset =  self._get_filter_and_queryset_by_date(self.queryset, self.request)
    #     return queryset

    # def _get_filter_and_queryset_by_date(self, queryset, request):
    #     adjacent_filter = {}

    #     start_date = convert_to_date(request, 'vanaf')
    #     if start_date is not None:
    #         adjacent_filter['vanaf'] = start_date
    #         queryset = queryset.filter(timestamp__gte=start_date)

    #     end_date = convert_to_date(request, 'tot')
    #     if end_date is not None:
    #         adjacent_filter['tot'] = end_date
    #         queryset = queryset.filter(timestamp__lt=end_date)

    #     on_date = convert_to_date(request, 'op')
    #     if end_date is not None:
    #         adjacent_filter['op'] = on_date
    #         queryset = queryset.filter(timestamp=on_date)

    #     return adjacent_filter, queryset


# def filter_on_date(queryset, value):
#     #assert False
#     if not value:
#         return queryset
#     date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
#     return queryset.filter(timestamp = date)



