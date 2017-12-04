from django.views.generic import TemplateView
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from datapunt_api import rest
from . import models
from . import serializers


# # Create your views here.
# class HomePageView(TemplateView):
#     template_name = 'index.html'



# class MeldingViewSet(viewsets.ModelViewSet):
#     """ ViewSet for viewing and editing Employee objects """
#     queryset = LengteGewicht.objects.all()
#     serializer_class = MeldingSerializer

class DrukteindexViewSet(rest.DatapuntViewSet):
    """
    Drukteindex API
    """

    queryset = models.Drukteindex.objects.all()
    serializer_class = serializers.DrukteindexSerializer
    serializer_detail_class = serializers.DrukteindexSerializer

    #filter_class = CijfersFilter

    #ordering_fields = ('jaar', 'buurt', 'variabele')
    #ordering = ('-jaar', 'buurt', 'variabele')