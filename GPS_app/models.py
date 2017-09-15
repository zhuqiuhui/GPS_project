# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Points(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    day_time = models.CharField(max_length=50)
    true_label = models.CharField(max_length=50)
    velocity = models.FloatField(default=0.0)
    acceleration = models.FloatField(default=0.0)
    distance = models.FloatField(default=0.0)
    specification_label = models.CharField(max_length=50, default='')
    tp = models.IntegerField(default=0)

class Segments(models.Model):
    start_point_id = models.IntegerField()
    end_point_id = models.IntegerField()
    true_label = models.CharField(max_length=50)
    infer_label = models.CharField(max_length=50)
        
