import csv
import sys
import os
import argparse
import django

import pandas as pd
import numpy as np

from datetime import datetime, date, time


# # parse arguments (now only datadir)
# parser = argparse.ArgumentParser()
# parser.add_argument('datadir', type=str, help='Local data directory.', nargs=1)
# args = parser.parse_args()

# add project dir to path
# may only be necessary for local dev?
project_dir = '/Users/rluijk/Documents/GemeenteAmsterdam/city-dynamics/web/'
sys.path.append(project_dir)

# add settings.py to environmental variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'schoonmonitor.settings'

# setup Django using settings
django.setup()

# import different models
# Note this somehow also invokes schoonmonitor/admin.py
from schoonmonitor.api.models import Melding

melding = Melding()
melding.__dict__
melding.save()








# # function to parse date,time in MORA data
# def datetime_parser(x):
#     datum, tijd = x.split()
#     day, month, year = datum.split('-')
#     hour, minute, second = tijd.split(':')
#     d = date(int(year), int(month), int(day))
#     t = time(int(hour), int(minute))
#     return datetime.combine(d, t)

# # function to read in mora data
# # def read_mora(filename):
# filename = 'data/MORA_data_data.csv'
# # open file
# file = csv.reader(open(filename, 'r', encoding='utf-8'), delimiter=';')

# # relevant columns
# fields = ['Lattitude', 'Longitude', 'Hoofdrubriek', 'Subrubriek', 'Datum melding', 'Tijdstip registratie melding']

# # inspect header, get index for relevant fields
# header = next(file)
# indx = np.where([col in fields for col in header])[0]

# # loop over rows
# # for row in file:
# # for i in range(10):
# row = next(file)
# melding = Melding()
# x = np.array(row)[indx]
# # melding.timestamp = datetime_parser(x[0] + ' ' + x[-1])
# # melding.id = 1
# # melding.hoofdrubriek = x[1]
# # melding.subrubriek = x[4]
# # melding.lat = x[2]
# # melding.lng = x[3]
# # melding.beschrijving = 'tekst'
# print(melding)
# melding.save()

# # class Melding(models.Model):
# #     hoofdrubriek = models.CharField(max_length=255)
# #     subrubriek = models.CharField(max_length=255)
# #     beschrijving = models.TextField()
# #     timestamp = models.DateTimeField()
# #     lat = models.CharField(max_length=255)
# #     lon = models.CharField(max_length=255)




# # read and edit data, then place it in database

# mora_path = os.path.join(args.datadir[0], 'MORA_data_data.csv')
# print(mora_path)
# read_mora(mora_path)

# # data = csv.reader(open('data/mora.csv'), delimiter = ';')
# # print(next(data)) # skip header
# # # for row in data:
# # #     print(row)
# # #     post = Beeldmaatlat()
# # #     post.crid = row[0]
# # #     post.Schouwronde = row[1], 