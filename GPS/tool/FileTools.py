# coding=utf-8
import datetime
import logging
from django.db import connection
import func
import sys
sys.path.append("../../")
from GPS_app import models
# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GPS.settings")# project_name 项目名称
# django.setup()


logger = logging.getLogger('GPSLog')
N = 10  # contant value
M = 8  # contant value
pointNum = 21  # the least the point number of segment
distInterval = 150  # combining short segment
vThreshold = 1.6  # m/s
aThreshold = 0.8  # m/s2


def handle_upload_file(file):
    # Step 1：保存临时文件
    now = datetime.datetime.now()
    fileNameStr = 'GPS/uploadFile/GPS_traj_' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
    logger.info('[handle_upload_file] fileNameStr:' + fileNameStr)
    with open(fileNameStr, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    # Step 2：处理文件内容
    allPoints = readFile(fileNameStr)
    logger.info('[handle_upload_file] allPoints len:' + str(len(allPoints)))
    # Step 3: 换乘点检测
    insertPoints = findTransitionPoint(allPoints)
    # Step 4: 保存数据库
    saveGPSPoint(insertPoints)


def saveGPSPoint(insertPoints):
    for point in insertPoints:
        GPSPointObject = models.Points(latitude=point[0], longitude=point[1],
                                       day_time=point[2], true_label=point[3], 
                                       velocity=point[4], acceleration=point[5], 
                                       distance=point[6], specification_label=point[7],
                                       tp=point[8])
        GPSPointObject.save()


def readFile(filePath):
    file_object = open(filePath)
    try:
        all_the_text = file_object.readlines()
    finally:
        file_object.close()
    return all_the_text


"""
    找出单条轨迹的换乘点
    Args:
         segment: GPS points, such as
                 [(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk), 
                 (39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk)...]
    Returns:
         parameters: GPS point id which is in sudden change
                     such as:
                         [(732708)...]
                     if parameters is null, then len(parameters)=0
"""
def findTransitionPoint(allPoints):
    '''
    Step 1：根据上传的一条轨迹进行点标记（初始标记），得到如[(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk, 速度, 加速度, 距离, walk-point, 是否是换乘点)...]
    '''
    allPoints = getInitialPoints(allPoints)
    segment = []
    index = 0
    for point in allPoints:
        segment.append((index, point[7]))
        index = index + 1
    '''
    Step 2：根据上传的一条轨迹进行点标记修正
    '''
    modifiedPoints, segmentIndexLabel = modifyPlointLab(segment, allPoints)
    # print(modifiedPoints)
    '''
    Step 3：根据突然变化的点可能是潜在换乘点

    '''
    candidateTP = getSuddenChangePointId(segmentIndexLabel)
    '''
    Step 4：合并小于路段 150 米的路段
    '''
    insertPoints = combineSeg(modifiedPoints, candidateTP)
    print(insertPoints)
    return insertPoints


"""
    input:[(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk)...]
    output:[(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk, 速度, 加速度, 距离, walk-point, 0)...]
"""
def getInitialPoints(allPoints):
    pointLen = len(allPoints)
    resAllPoints = []
    i = 0
    prePoint = allPoints[i]
    while i < pointLen:
        curList = allPoints[i].strip('\n').split(',') # 去掉后面换行
        curTuple = (curList[0], curList[1], curList[2], curList[3])
        if i == 0:
            curTuple = curTuple + (0, 0, 0, 'none', 0)
            resAllPoints.append(curTuple)
            pre = curTuple
            i = i + 1
            continue
        if i == 1:
            # 计算 速度、距离
            distance = func.getDistance(float(pre[0]), float(pre[1]), float(curList[0]), float(curList[1]))
            timeInterval = func.getTimeInterval(pre[2], curList[2])
            v = distance / timeInterval
            curTuple = curTuple + (v, 0, distance, 'none', 0)
            resAllPoints.append(curTuple)
            pre = curTuple
            # print(curTuple)
            i = i + 1
            continue
        # 第3个点之后，计算速度、加速度、距离、point label
        distance = func.getDistance(float(pre[0]), float(pre[1]), float(curList[0]), float(curList[1]))
        timeInterval = func.getTimeInterval(pre[2], curList[2])
        v = distance / timeInterval
        a = abs(v - pre[4]) / timeInterval
        pointLabel = 'non-walk-point'
        if v < vThreshold and a < aThreshold:
            pointLabel = 'walk-point'
        if i == pointLen - 1:
            curTuple = curTuple + (v, a, distance, pointLabel, 0)
        else:
            curTuple = curTuple + (v, a, distance, pointLabel, 0)
        resAllPoints.append(curTuple)
        pre = curTuple
        # print(curTuple)
        i = i + 1
    return resAllPoints



def modifyPlointLab(segment, allPoints):
    """
    process every segment using greedy method.
    Args:
         segment: GPS points set, such as
                 [(732708, 'none'), (732709, 'non-walk-point')...]
    Returns:
         resAllPoints: [(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk, 速度, 加速度, 距离, walk-point, 0)...]
         segment: [(732708, 'walk-point')...]
    """
    # process segment whose GPS point number is lower than pointNum
    parameters = []
    if len(segment) < pointNum:
        for item1 in segment:
            parameters.append((item1[1], item1[0]))
        return parameters

    # processing
    index = 0
    segLen = len(segment)
    preSeg = []
    while func.isNotSame(preSeg, segment):
        preSeg = segment
        while index < segLen:
            if index < N:
                # processing left
                countNonWalk = 0
                countWalk = 0
                for item2 in segment[index + 1:index + N + 1]:
                    if item2[1] == 'walk-point':
                        countWalk += 1
                    if item2[1] == 'non-walk-point':
                        countNonWalk += 1
                if countWalk >= M:
                    te = (segment[index][0], 'walk-point')
                    segment[index] = te
                if countNonWalk >= M:
                    te = (segment[index][0], 'non-walk-point')
                    segment[index] = te
            elif index > segLen - N - 1:
                # processing right
                countNonWalk = 0
                countWalk = 0
                for item3 in segment[index - N:index]:
                    if item3[1] == 'walk-point':
                        countWalk += 1
                    if item3[1] == 'non-walk-point':
                        countNonWalk += 1
                if countWalk >= M:
                    te = (segment[index][0], 'walk-point')
                    segment[index] = te
                if countNonWalk >= M:
                    te = (segment[index][0], 'non-walk-point')
                    segment[index] = te
            else:
                # processing middle
                lcountNonWalk = 0
                lcountWalk = 0
                rcountNonWalk = 0
                rcountWalk = 0
                for item4 in segment[index - N:index]:
                    if item4[1] == 'walk-point':
                        lcountWalk += 1
                    if item4[1] == 'non-walk-point':
                        lcountNonWalk += 1
                for item5 in segment[index + 1:index + N + 1]:
                    if item5[1] == 'walk-point':
                        rcountWalk += 1
                    if item5[1] == 'non-walk-point':
                        rcountNonWalk += 1
                if lcountWalk >= M and rcountWalk >= M:
                    te = (segment[index][0], 'walk-point')
                    segment[index] = te
                if rcountNonWalk >= M and rcountNonWalk >= M:
                    te = (segment[index][0], 'non-walk-point')
                    segment[index] = te
            index += 1  # end while
    resAllPoints = []
    # print(segment)
    for item6 in segment:
        tempTuple = (allPoints[item6[0]][0], allPoints[item6[0]][1], 
                     allPoints[item6[0]][2], allPoints[item6[0]][3], 
                     allPoints[item6[0]][4], allPoints[item6[0]][5], 
                     allPoints[item6[0]][6], item6[1], allPoints[item6[0]][8])
        resAllPoints.append(tempTuple)
    return resAllPoints, segment


def getSuddenChangePointId(segment):
    """
        get GPS point id which is in the condition that sudden change.
        Args:
             segment: GPS points set, such as
                     [(732708, 'none'), (732709, 'non-walk-point')...]
        Returns:
             parameters: GPS point id which is in sudden change
                         such as:
                             [(732708)...]
                         if parameters is null, then len(parameters)=0
    """
    parameters = []
    if len(segment) < pointNum:
        return parameters
    index = 0
    segLen = len(segment)
    while index < segLen:
        if index >= N and index <= segLen - N - 1:
            lcountNonWalk = 0
            lcountWalk = 0
            rcountNonWalk = 0
            rcountWalk = 0
            for item2 in segment[index - N:index]:
                if item2[1] == 'walk-point':
                    lcountWalk += 1
                if item2[1] == 'non-walk-point':
                    lcountNonWalk += 1
            for item3 in segment[index + 1:index + N + 1]:
                if item3[1] == 'walk-point':
                    rcountWalk += 1
                if item3[1] == 'non-walk-point':
                    rcountNonWalk += 1
            if lcountWalk >= M and rcountNonWalk >= M:
                parameters.append((segment[index][0],))
                index += N
            if lcountNonWalk >= M and rcountWalk >= M:
                parameters.append((segment[index][0],))
                index += N
        index += 1
    return parameters



"""
   input: modifiedPoints: [(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk, 速度, 加速度, 距离, walk-point, 0)...]
          candidateTP: [(34)...] 存放在list中的索引
"""
def combineSeg(modifiedPoints, candidateTP):
    canLen = len(candidateTP)
    i = 0
    disSum = 0.0
    pre = 0
    TP = []
    while i < canLen:
        cur = candidateTP[i]
        disSum = disSum + getDistanceBetweenIndex(pre, cur[0], modifiedPoints)
        if disSum > distInterval:
            disSum = 0.0
            TP.append(cur)
        pre = cur
        i = i + 1
    insertPoints = getInsertPoints(modifiedPoints, TP)
    return insertPoints


def getDistanceBetweenIndex(fromIndex, toIndex, modifiedPoints):
    # print("fromIndex:" + str(fromIndex) + " toIndex:" + str(toIndex) + "len(modifiedPoints):" + str(len(modifiedPoints)))
    i = fromIndex;
    sumDist = 0.0
    while i <= toIndex:
        sumDist = sumDist + modifiedPoints[i][6]
        i = i + 1
    return sumDist


'''
[(39.9660666666667,116.352433333333,2008/04/30 21:49:35,walk, 速度, 加速度, 距离, walk-point, 0)...]
'''
def getInsertPoints(modifiedPoints, TP):
    TPList = []
    for tp in TP:
        TPList.append(int(tp[0]))
    i = 0
    insertPoints = []
    while i < len(modifiedPoints):
        cur = modifiedPoints[i]
        if existTP(i, TPList) == 1:
            tempTuple = (cur[0], cur[1], cur[2], cur[3], cur[4],
                cur[5], cur[6], cur[7], 1)
            # print(tempTuple)
            insertPoints.append(tempTuple)
        else:
            tempTuple = (cur[0], cur[1], cur[2], cur[3], cur[4],
                cur[5], cur[6], cur[7], 0)
            insertPoints.append(tempTuple)
        i = i + 1
    return insertPoints


def existTP(index, TPList):
    if index in TPList:
        return 1
    else:
        return 0


if __name__ == '__main__':
    # fileNameStr = '../uploadFile/GPS_traj_2017-09-05-14-46-17.txt'
    # allPoints = readFile(fileNameStr)
    # # print(allPoints)
    # insertPoints = findTransitionPoint(allPoints)
    t = [('39.9661166666667', '116.351733333333', '2008/04/30 21:48:43', 'walk', 0, 0, 0, 'walk-point', 0), ('39.9660666666667', '116.352433333333', '2008/04/30 21:49:35', 'walk', 1.498532645916858, 0, 77.92369758767661, 'walk-point', 0)]
    saveGPSPoint(t)
