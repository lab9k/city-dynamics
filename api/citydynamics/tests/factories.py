# Python
# Packages
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


class BuurtcombinatieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurtcombinatie

    vollcode = fuzzy.FuzzyText()
    naam = fuzzy.FuzzyText()


class BuurtcombinatieIndexFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BuurtCombinatieDrukteindex

    index = fuzzy.FuzzyInteger(low=0, high=99900090000000)
    # vollcode = factory.SubFactory(BuurtcombinatieFactory)
    #  naam = fuzzy.FuzzyText()
    hour = fuzzy.FuzzyInteger(low=0, high=24)
    weekday = fuzzy.FuzzyInteger(low=0, high=6)
    drukteindex = fuzzy.FuzzyFloat(low=0, high=1)
    # wkb_geometry_simplified = ...
