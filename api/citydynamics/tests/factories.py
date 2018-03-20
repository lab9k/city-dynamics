# Python
# Packages
from datetime import datetime
from datetime import timezone
import factory
from factory import fuzzy

# Project
from citydynamics.datasets import models


class HotspotsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Hotspots

    index = fuzzy.FuzzyInteger(low=0)
    hotspot = fuzzy.FuzzyText()
    lat = fuzzy.FuzzyFloat(low=0)
    lon = fuzzy.FuzzyFloat(low=0)
    # point_sm = fuzzy.GeometryField()
