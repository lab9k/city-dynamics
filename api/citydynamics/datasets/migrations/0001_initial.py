# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-20 10:42
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buurtcombinatie',
            fields=[
                ('ogc_fid', models.AutoField(primary_key=True, serialize=False)),
                ('gml_id', models.CharField(max_length=255)),
                ('id', models.CharField(blank=True, max_length=255, null=True)),
                ('vollcode', models.CharField(blank=True, max_length=255, null=True)),
                ('naam', models.CharField(blank=True, max_length=255, null=True)),
                ('display', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('uri', models.CharField(blank=True, max_length=255, null=True)),
                ('wkb_geometry', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('wkb_geometry_simplified', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=0)),
            ],
            options={
                'db_table': 'buurtcombinatie',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Hotspots',
            fields=[
                ('index', models.BigIntegerField(primary_key=True, serialize=False)),
                ('hotspot', models.TextField(blank=True, null=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lon', models.FloatField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=0)),
                ('vollcode', models.CharField(blank=True, max_length=255, null=True)),
                ('stadsdeelcode', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'hotspots',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RealtimeGoogle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_id', models.TextField(db_index=True)),
                ('scraped_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.TextField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'db_table': 'google_raw_locations_realtime_current_acceptance',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BuurtCombinatieDrukteindex',
            fields=[
                ('index', models.BigIntegerField(primary_key=True, serialize=False)),
                ('hour', models.IntegerField()),
                ('weekday', models.IntegerField()),
                ('drukteindex', models.FloatField()),
                ('vollcode', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='druktecijfers_bc', to='datasets.Buurtcombinatie')),
            ],
        ),
        migrations.CreateModel(
            name='HotspotsDrukteIndex',
            fields=[
                ('index', models.BigIntegerField(primary_key=True, serialize=False)),
                ('hour', models.IntegerField()),
                ('weekday', models.IntegerField()),
                ('drukteindex', models.FloatField()),
                ('hotspot', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='druktecijfers', to='datasets.Hotspots')),
            ],
        ),
    ]
