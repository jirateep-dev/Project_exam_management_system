# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-15 05:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database_management', '0013_auto_20180125_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dateexam',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
