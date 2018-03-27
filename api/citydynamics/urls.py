"""ibprojecten URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import collections

# Added to open Files on dev server
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers, views, reverse, response

from citydynamics.datasets.views import BuurtcombinatieViewset
from citydynamics.datasets.views import DrukteindexHotspotViewset
from citydynamics.datasets.views import RealtimeGoogleViewset
from citydynamics.datasets.views import DrukteindexBuurtcombinatieViewset
from citydynamics.datasets.views import api_proxy


# stack overflow hack
# http://stackoverflow.com/questions/18817988/using-django-rest-frameworks-browsable-api-with-apiviews

class HybridRouter(routers.DefaultRouter):
    def __init__(self, *args, **kwargs):
        super(HybridRouter, self).__init__(*args, **kwargs)
        self._api_view_urls = {}

    def add_api_view(self, name, url):
        self._api_view_urls[name] = url

    def remove_api_view(self, name):
        del self._api_view_urls[name]

    @property
    def api_view_urls(self):
        ret = {}
        ret.update(self._api_view_urls)
        return ret

    def get_urls(self):
        urls = super(HybridRouter, self).get_urls()
        for api_view_key in self._api_view_urls.keys():
            urls.append(self._api_view_urls[api_view_key])
        return urls

    def get_api_root_view(self, **kwargs):
        # Copy the following block from Default Router
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_view_urls = self._api_view_urls

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = {}
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse.reverse(
                        url_name, request=request, format=format)

                # In addition to what had been added, now add the APIView urls
                for api_view_key in api_view_urls.keys():
                    ret[api_view_key] = reverse.reverse(
                        api_view_urls[api_view_key].name,
                        request=request, format=format)

                # sort the damn thing
                od = collections.OrderedDict(sorted(ret.items()))

                return response.Response(od)

        return APIRoot.as_view()


router = HybridRouter()
router.register('buurtcombinatie', BuurtcombinatieViewset, 'buurtcombinatie')
router.register(
    'buurtcombinatie_drukteindex', DrukteindexBuurtcombinatieViewset, 'buurtcombinatie_drukteindex')
router.register('hotspots', DrukteindexHotspotViewset, 'hotspots')
router.register('realtime', RealtimeGoogleViewset, 'realtime')

router.add_api_view(
        'apiproxy',
        url(r'apiproxy', api_proxy, name='apiproxy'))


urlpatterns = router.urls

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^status/', include('health.urls', namespace='health')),
]


# To open Files on development server add this:
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
