# Generated by Django 2.0.5 on 2018-05-07 16:48

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RealtimeHistorian',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_id', models.TextField(db_index=True)),
                ('scraped_at', models.DateTimeField(blank=True)),
                ('name', models.TextField(null=True)),
                ('source', models.CharField(max_length=40)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.AlterModelTable(
            name='realtimegoogle',
            table='google_raw_locations_realtime_current_production',
        ),
    ]