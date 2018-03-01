# Python
# Packages
from datetime import datetime
from datetime import timezone
import factory
from factory import fuzzy

# Project
from citydynamics.datasets import models


class DrukteindexFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Drukteindex

    index = fuzzy.FuzzyInteger(low=10000000000000, high=19000009999999)
    timestamp = fuzzy.FuzzyDateTime(
        datetime(2016, 1, 1, tzinfo=timezone.utc),
        datetime(2017, 1, 1, tzinfo=timezone.utc))
    vollcode = fuzzy.FuzzyText()
    weekday = fuzzy.FuzzyInteger(0, 6)
    hour = fuzzy.FuzzyFloat(0, 23)

    # google_live = fuzzy.FuzzyFloat(0, 1)
    # google_week = fuzzy.FuzzyFloat(0, 1)
    gvb_buurt = fuzzy.FuzzyFloat(0, 1)
    gvb_stad = fuzzy.FuzzyFloat(0, 1)
    verblijvers = fuzzy.FuzzyFloat(0, 1)
    # google = fuzzy.FuzzyFloat(0, 1)
    gvb = fuzzy.FuzzyFloat(0, 1)
    drukte_index = fuzzy.FuzzyFloat(0, 1)


class HotspotsFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Hotspots

    index = fuzzy.FuzzyInteger(low=0)
    hotspot = fuzzy.FuzzyText()
    latitude = fuzzy.FuzzyFloat(low=0)
    longitude = fuzzy.FuzzyFloat(low=0)
    # point_sm = fuzzy.GeometryField()


