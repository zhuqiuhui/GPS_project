# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from . import models
import logging

logger = logging.getLogger('GPSLog')

# Create your views here.
def add(request):
    pass


def select(request):
    point_list = models.Points.objects.all()
    logger.info('[views.select] point_list:' + str(point_list))
    return render(request, 'showGPS.html', {'point_list':point_list})
