# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-09 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='all_parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='script_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_name', models.CharField(max_length=40)),
                ('script_path', models.CharField(max_length=100)),
                ('service_name', models.CharField(max_length=40)),
                ('server_name', models.CharField(max_length=40)),
                ('status', models.IntegerField(choices=[(1, '空闲中'), (2, '进行中')], default=1)),
                ('script_parameter', models.ManyToManyField(blank=True, to='script.all_parameter')),
            ],
        ),
    ]