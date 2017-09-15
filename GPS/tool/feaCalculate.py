# coding=utf-8
import logging
import func
import numpy as np
import datetime
import json

logger = logging.getLogger('GPSLog')
vth1 = 5.2  # divide velocity into low and middle level
vth2 = 16  # divide velocity into middle and high level
ath1 = 0.3  # divide acceleration into low and middle level
ath2 = 1.0  # divide acceleration into middle and high level

perTh1 = 0.75  # 75% of velocity and acceleration
perTh2 = 0.85  # 85% of velocity and acceleration
perTh3 = 0.95  # 95% of velocity and acceleration
Ar = 0.25  # ACR threshold value

# not sure
lowVth = 0.36  # near 0 point veloctiy
lowAth = 0.1  # near 0 point acceleration
# busDistTh = 50  # the distance between bus top and low velocity point
busDistTh = 20  # the distance between bus top and low velocity point

degreeTh = 15  # the bais of angle (feaature HCR and ACP)
Vr = 0.36  # VCR threshold value
Vs = 3.2  # SR threshold value

LSRth = 1  # LSR（the ratio of points with a speed of less than 1m/s）


def feaCalculation(points):
    pointList = []
    for point in points:
        temp = (point.id, point.latitude, point.longitude, point.day_time,
            point.velocity, point.acceleration, point.distance, point.true_label, point.tp)
        pointList.append(temp)
    # logger.info('[feaCalculate.feaCalculation]' + str(pointList))
    segmentList, segmentsFea = getSegment(pointList)
    return segmentList, segmentsFea

'''
从原始集合中获取特征集合
'''
def getSegment(pointList):
    segmentsFea = []
    segmentList = []
    segment = []
    for point in pointList:
        if point[8] == 1:
            #新生成一段
            tempFea = getAllFea(segment)
            segmentsFea.append(tempFea)
            segmentList.append(segment) # 返回segment轨迹点集合
            segment = []
        segment.append(point)
    # 处理最后一段
    lastFea = getAllFea(segment)
    segmentsFea.append(lastFea)
    segmentList.append(segment)
    return segmentList, segmentsFea



'''
获取segment的所有特征集合
velocity features:
      (85thV,MaxV1,MaxV2,MedianV,MinV,MeanV,Ev,Dv,HVR,MVR,LVR)
accelerometer features:
      (85thA,MaxA1,MaxA2,MedianA,MinA,MeanA,Ea,Da,HAR,MAR,LAR)
behavior features:
      (TS,ACR,BSR,ACP,HCR,SR,VCR)
'''
def getAllFea(segment):
    vfea = getVFeature(segment)
    afea = getAFeature(segment)
    TS = getTS(segment)
    ACR = getACR(segment)
    # print(ACR)
    # BSR = getBSR(segment, '../static/file/busInfo.txt')
    BSR = getBSR(segment, 'GPS/static/file/busInfo.txt')
    # print(BSR)
    ACP = getACP(segment)
    # print('ACP:' + str(ACP))
    HCR = getHCR(segment)
    # print('HCR:' + str(HCR))
    SR = getSR(segment)
    # print('SR:' + str(SR))
    VCR = getVCR(segment)
    # print('VCR:' + str(VCR))
    behaviorFea = (TS, ACR, BSR, ACP, HCR, SR, VCR)
    allFea = vfea + afea + behaviorFea
    # print(allFea)
    return allFea


def getVFeature(segment):
    """
        Args: segment: such as
                [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
                  0,    1,       2,        3,       4,        5,          6,        7,       8
        Returns:
               distance, 85thV, MaxV1, MaxV2, MedianV, MinV, MeanV, Ev, Dv, HVR, MVR, LVR
    """
    vSet = []
    hNum = 0
    mNum = 0
    lNum = 0
    dist = 0.0
    for point in segment:
        cur = point[4]
        vSet.append(cur)
        if cur <= vth1:
            lNum += 1
        elif cur >= vth2:
            hNum += 1
        else:
            mNum += 1
        dist = dist + point[6]
    vSetArray = np.array(vSet)
    vSetArray.sort()
    vLen = len(vSetArray)
    # caculate 75% velocity
    _75thIndex = round(vLen * perTh1)
    if _75thIndex >= vLen:
        _75thIndex = vLen - 2
    _75thV = vSetArray[int(_75thIndex)]
    # caculate 85% velocity
    _85thIndex = round(vLen * perTh2)
    if _85thIndex >= vLen:
        _85thIndex = vLen - 2
    _85thV = vSetArray[int(_85thIndex)]
    # caculate 95% velocity
    _95thIndex = round(vLen * perTh3)
    if _95thIndex >= vLen:
        _95thIndex = vLen - 2
    _95thV = vSetArray[int(_95thIndex)]

    MaxV1 = vSetArray[-1]
    MaxV2 = vSetArray[-2]
    MedianV = np.median(vSetArray)
    MinV = vSetArray[0]
    MeanV = np.mean(vSetArray)
    Ev = np.mean(vSetArray)
    Dv = np.var(vSetArray)
    HVR = hNum / vLen
    MVR = mNum / vLen
    LVR = lNum / vLen
    # res = (_75thV, _85thV, _95thV, MaxV1, MaxV2,
    #        MedianV, MinV, MeanV, Ev, Dv, HVR, MVR, LVR)
    res = (dist, _85thV, MaxV1, MaxV2, MedianV, MinV, MeanV, Ev, Dv, HVR, MVR, LVR)
    return res


def getAFeature(segment):
    """
     Args: segment: such as
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           85thA, MaxA1, MaxA2, MedianA, MinA, MeanA, Ea, Da, HAR, MAR, LAR
    """
    aSet = []
    hNum = 0
    mNum = 0
    lNum = 0
    for point in segment:
        cur = point[5]
        aSet.append(cur)
        if cur <= ath1:
            lNum += 1
        elif cur >= ath2:
            hNum += 1
        else:
            mNum += 1
    aSetArray = np.array(aSet)
    aSetArray.sort()
    aLen = len(aSetArray)
    # caculate 75% acceleration
    _75thIndex = round(aLen * perTh1)
    if _75thIndex >= aLen:
        _75thIndex = aLen - 2
    _75thA = aSetArray[int(_75thIndex)]
    # caculate 75% acceleration
    _85thIndex = round(aLen * perTh2)
    if _85thIndex >= aLen:
        _85thIndex = aLen - 2
    _85thA = aSetArray[int(_85thIndex)]
    MaxA1 = aSetArray[-1]
    MaxA2 = aSetArray[-2]
    MedianA = np.median(aSetArray)
    MinA = aSetArray[0]
    MeanA = np.mean(aSetArray)
    Ea = np.mean(aSetArray)
    Da = np.var(aSetArray)
    HAR = hNum / aLen
    MAR = mNum / aLen
    LAR = lNum / aLen
    # res = (_75thA, _85thA, MaxA1, MaxA2, MedianA,
    #        MinA, MeanA, Ea, Da, HAR, MAR, LAR)
    res = (_85thA, MaxA1, MaxA2, MedianA,
           MinA, MeanA, Ea, Da, HAR, MAR, LAR)
    return res


def getTS(segment):
    """
    Args: segment: such as
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           1: denotes T_busy (7:00-10:00 am 16:00-21:00)
           0: denotes T_idle
    """
    busyNum = 0
    idleNum = 0
    for point in segment:
        cur = point[3]
        t = datetime.datetime.strptime(cur, '%Y/%m/%d %H:%M:%S')
        h = t.hour
        if h >= 7 and h < 10 or h >= 16 and h < 20:
            busyNum += 1
        else:
            idleNum += 1
    if busyNum >= idleNum:
        return 1
    else:
        return 0


def getACR(segment):
    """
    Args: segment: such as,
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           ACR value of segment
    """
    pre = segment[0]
    index = 1
    distSum = 0.0
    segLen = len(segment)
    num = 0
    while index < segLen:
        cur = segment[index]
        distSum += cur[6]
        if pre[5] == 0:
            ARate = 1
        else:
            ARate = abs(cur[5] - pre[5]) / pre[5]
        if ARate >= Ar:
            num += 1
        pre = cur
        index += 1
    if distSum == 0.0:
        return num
    else:
        return num / distSum


def getBSR(segment, busInfoPath):
    """
    Args: segment: such as,
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
          busInfoPath: bus information file
    Returns:
           BSR value of segment
    """

    # open bus information file
    busInfoFile = open(busInfoPath)
    try:
        allLines = busInfoFile.readlines()
    finally:
        busInfoFile.close()

    # get BSR value
    segLen = len(segment)
    num = 0
    lowNum = 0
    index = 0
    while index < segLen:
        cur = segment[index]
        min = 999999
        # if cur[5] < lowVth and cur[6] < lowAth:
        if cur[4] < lowVth:
            # get near 0 point
            lowNum += 1
            for line in allLines:
                line = line.strip('\n')
                lineList = line.split(',')
                busLat = lineList[0]
                busLon = lineList[1]
                tempDist = func.getDistance(
                    cur[1], cur[2], float(busLat), float(busLon))
                if tempDist < min:
                    min = tempDist
            if min < busDistTh:
                num += 1
        index += 1
    if lowNum == 0:
        return 0
    else:
        return num / lowNum

def getACP(segment):
    """
    Args: segment: such as,
           [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           ACP (angle change percent) value of segment
    """
    segLen = len(segment)
    index = 2
    num = 0
    pre = segment[1]
    preDegree = func.getDegree(segment[0][1], segment[0][2], pre[1], pre[2])
    while index < segLen:
        cur = segment[index]
        curDegree = func.getDegree(pre[1], pre[2], cur[1], cur[2])
        if abs(curDegree - preDegree) >= degreeTh:
            num += 1
        preDegree = curDegree
        pre = cur
        index += 1
    return num / segLen


def getHCR(segment):
    """
    Args: segment: such as, 
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           HCR (heading change rate) value of segment
    """
    segLen = len(segment)
    index = 2
    num = 0
    distSum = 0.0
    pre = segment[1]
    preDegree = func.getDegree(segment[0][1], segment[0][2], pre[1], pre[2])
    while index < segLen:
        cur = segment[index]
        distSum += cur[6]
        curDegree = func.getDegree(pre[1], pre[2], cur[1], cur[2])
        if abs(curDegree - preDegree) >= degreeTh:
            num += 1
        preDegree = curDegree
        pre = cur
        index += 1
    if distSum == 0.0:
        return num
    else:
        return num / distSum


def getSR(segment):
    """
    Args: segment: such as,
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           SR (stop rate) value of segment
    """
    num = 0
    distSum = 0.0
    index = 0
    segLen = len(segment)
    while index < segLen:
        cur = segment[index]
        if index != 0:
            distSum += cur[6]
        if cur[4] < Vs:
            num += 1
        index += 1
    if distSum == 0.0:
        return num
    else:
        return num / distSum


def getVCR(segment):
    """
    Args: segment: such as,
            [(id,latitude,longitude,day_time,velocity,accelerometer,distance,true_label, tp)]
              0,    1,       2,        3,       4,        5,          6,        7,       8
    Returns:
           VCR (velocity change rate) value of segment
    """
    pre = segment[0]
    index = 1
    distSum = 0.0
    segLen = len(segment)
    num = 0
    while index < segLen:
        cur = segment[index]
        distSum += cur[6]
        if pre[4] == 0:
            VRate = 1
        else:
            VRate = abs(cur[4] - pre[4]) / pre[4]
        if VRate >= Vr:
            num += 1
        pre = cur
        index += 1
    if distSum == 0.0:
        return num
    else:
        return num / distSum


if __name__ == '__main__':
    points = [(19L, 39.81815, 119.48115, u'2008/05/01 12:08:03', 6.83628697998364, 0.000131502864074639, 348083.224159827, u'none', 0L), (20L, 39.8178166666667, 119.480866666667, u'2008/05/01 12:08:31', 1.12644740921305, 0.203922841813235, 31.5405274579654, u'walk', 0L), 
    (21L, 39.8179333333333, 119.480316666667, u'2008/05/01 12:15:20', 0.149696178908997, 0.00238814481736932, 61.2257371737798, u'walk', 0L), (22L, 39.8177166666667, 119.480916666667, u'2008/05/01 12:15:38', 3.71065157607302, 0.197830855398001, 66.7917283693144, u'walk', 0L), 
    (23L, 39.8181666666667, 119.479683333333, u'2008/05/01 12:19:52', 0.54052794592556, 0.0124808016934939, 137.294098265092, u'walk', 0L), (24L, 39.8178, 119.480583333333, u'2008/05/01 12:20:00', 12.5234504780694, 1.49786531651799, 100.187603824556, u'walk', 1L), 
    (25L, 39.8181, 119.480766666667, u'2008/05/01 12:31:18', 0.0301010765185114, 0.0184267690288362, 20.4085298795507, u'walk', 0L), (26L, 39.8185166666667, 119.481083333333, u'2008/05/01 12:32:55', 0.363414889139616, 0.00343622487238252, 35.2512442465427, u'walk', 0L), 
    (27L, 39.81895, 119.481433333333, u'2008/05/01 12:35:13', 0.282332447635306, 0.000587553923944272, 38.9618777736722, u'walk', 0L), (28L, 39.8187166666667, 119.4816, u'2008/05/01 13:20:33', 0.00682108300962323, 0.000101290942877089, 18.5533457861752, u'walk', 0L), 
    (29L, 39.8183, 119.481216666667, u'2008/05/01 13:21:47', 0.57665472648182, 0.00770045464151617, 42.6724497596547, u'walk', 1L), (30L, 39.8184333333333, 119.480716666667, u'2008/05/01 13:26:39', 0.190615732626836, 0.00132205134881844, 55.6597939270362, u'walk', 0L), 
    (31L, 39.8181833333333, 119.481066666667, u'2008/05/01 13:28:11', 0.423498671452959, 0.00253133629158829, 38.9618777736722, u'walk', 0L), (32L, 39.81775, 119.479566666667, u'2008/05/01 13:31:21', 0.878838566785784, 0.0023965257649096, 166.979327689299, u'walk', 0L), 
    (33L, 39.8174166666667, 119.4787, u'2008/05/01 13:33:18', 0.824589016843189, 0.000463671367030724, 96.4769149706531, u'walk', 0L), (34L, 39.8171666666667, 119.477416666667, u'2008/05/01 13:35:39', 1.0131921172712, 0.0013376106413334, 142.860088535239, u'walk', 0L), 
    (35L, 39.8164833333333, 119.477283333333, u'2008/05/01 13:37:04', 0.174619295461485, 0.00986556260952603, 14.8426401142262, u'walk', 0L), (36L, 39.8160166666667, 119.477333333333, u'2008/05/01 13:38:09', 0.0856343220551828, 0.00136899959086619, 5.56623093358688, u'walk', 0L)]
    # getAllFea(points)
    segmentsFea = getSegment(points)
    print(segmentsFea)