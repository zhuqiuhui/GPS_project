import time
from math import *
import datetime
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

def getDistance(latA, lonA, latB, lonB):
    if latA == latB and lonA == lonB:
        return 0
    ra = 6378140  # radius of equator: meter
    rb = 6356755  # radius of polar: meter
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)

    pA = atan(rb / ra * tan(radLatA))
    pB = atan(rb / ra * tan(radLatB))
    temp = sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(radLonA - radLonB)
    if temp < -1 or temp > 1:
        return getDistance2(latA, lonA, latB, lonB)
    x = acos(temp)
    c1 = (sin(x) - x) * (sin(pA) + sin(pB))**2 / cos(x / 2)**2
    if sin(x / 2) == 0:
        return getDistance2(latA, lonA, latB, lonB)
    c2 = (sin(x) + x) * (sin(pA) - sin(pB))**2 / sin(x / 2)**2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    return distance


def getDistance2(latA, lonA, latB, lonB):
    """
    deal with the case which function getDistance could not handle
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    a = radLatA - radLatB
    b = radLonA - radLonB
    s = 2 * asin(sqrt(pow(sin(a / 2), 2) + cos(radLatA) *
                      cos(radLatB) * pow(sin(b / 2), 2)))
    s = s * 6378137
    s = round(s * 10000) / 10000
    return s


def getTimeInterval(timeStr1, timeStr2):
    """
    Args:
        timeStr1 and timeStr2 are the string of time,
        default: timeStr1 is before timeStr2
    Returns:
        the interval of timeStr1 and timeStr2 (type: seconds)
    """
    date1 = time.strptime(timeStr1, "%Y/%m/%d %H:%M:%S")
    date2 = time.strptime(timeStr2, "%Y/%m/%d %H:%M:%S")
    d1 = datetime.datetime(date1[0], date1[1], date1[
                           2], date1[3], date1[4], date1[5])
    d2 = datetime.datetime(date2[0], date2[1], date2[
                           2], date2[3], date2[4], date2[5])
    return (d2 - d1).seconds


def isNotSame(comp1, comp2):
    """
    compare if comp1 is same as comp2
    Args:
        comp1:
        comp2:
    Returns:
        1: comp1 is not same as comp2
        0: comp1 is same as comp2
    """
    if comp1 == comp2:
        return 0
    else:
        return 1

def getDegree(latA, lonA, latB, lonB):
    """
    Args:
        point p1(latA, lonA)
        point p2(latB, lonB)
    Returns:
        bearing between the two GPS points,
        default: the basis of heading direction is north
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng