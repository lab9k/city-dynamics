from django.contrib import admin
from citydynamics.api.models import Buurtcombinatie
from citydynamics.api.models import Gvb
from citydynamics.api.models import Drukteindex
# from leaflet.admin import LeafletGeoAdmin

# Change header name
admin.site.site_header = 'citydynamics'

# Register your models here.



# //////////////////////////////////////////////
# Main Project
# /////////////////////////////////////////////


# class BeeldmaatlattenAdmin(LeafletGeoAdmin, admin.ModelAdmin):
#     list_projects = ('name')
#     #inlines = [WerkorderInline, ProjectPlanInline]


admin.site.register(Buurtcombinatie)
admin.site.register(Drukteindex)



