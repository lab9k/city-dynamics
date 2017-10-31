from django.views.generic import TemplateView
#from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from cityDynamics.api.models import LengteGewicht
from cityDynamics.api.serializers import MeldingSerializer

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'index.html'



class MeldingViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Employee objects """
    queryset = LengteGewicht.objects.all()
    serializer_class = MeldingSerializer
