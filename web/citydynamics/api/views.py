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

class GvbViewSet(rest.DatapuntViewSet):
    """
    Amazing api
    """

    queryset = models.Gvb.objects.all()
    serializer_class = serializers.GvbSerializer
    serializer_detail_class = serializers.GvbSerializer

    #filter_class = CijfersFilter

    #ordering_fields = ('jaar', 'buurt', 'variabele')
    #ordering = ('-jaar', 'buurt', 'variabele')