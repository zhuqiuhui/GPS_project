# coding=utf-8
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from tool.FileTools import handle_upload_file
from tool.feaCalculate import feaCalculation
from django.shortcuts import render
from django.shortcuts import render_to_response
import logging
import json
from django.core import serializers
import sys
sys.path.append("../")
from GPS_app import models
from tool.classifyMain import loadModelPredict


logger = logging.getLogger('GPSLog')


'''
上传文件处理
'''
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upload_file(request.FILES.get('file', None))
            ftemp = request.FILES.get('file', None)
            print('ftemp: ', ftemp)
            return HttpResponseRedirect('/success/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form':form})


'''
上传成功跳转处理
'''
def uploadFileResult(request):
    result = u'成功......'
    return render(request, 'success.html', {'result':result})


def table(request):
    table_form=forms.SignupForm()
    return render(request,'table.html',{'form':table_form})


def mainFrame(request):
    return render(request, 'main.html')

def mainFooter(request):
    return render(request, 'footer.html')

def mainTop(request):
    return render(request, 'top.html')

def mainLeft(request):
    return render(request, 'left.html')

def mainRight(request):
    return render(request, 'right.html')

def importGPS(request):
    return render(request, 'importGPS.html')

def importGPSSubmit(request):
    file_obj = request.FILES.get('GPS_file', None)
    if file_obj == None:
        logger.warn("file not existing in the request")
        return render(request, 'importGPSfail.html')
    handle_upload_file(request.FILES.get('GPS_file', None))
    return render(request, 'importGPSsuccess.html')

def displayGPSByDate(request):
    return render(request, 'displayGPS_01.html')

def displayGPSByDateSubmit(request):
    if 'targetDate' in request.GET:
        searchDate = request.GET['targetDate']
        logger.info('[view.displayGPSByDateSubmit]' + str(searchDate))
        newStr = replaceDate(searchDate)
        # 根据日期查询数据库
        points = models.Points.objects.filter(day_time__contains=newStr)
        logger.info('[view.displayGPSByDateSubmit]' + str(len(points)))
        return render(request, 'displayGPS_01_res.html', {'searchDate':searchDate, 'points':serializers.serialize('json', list(points))})
    else:
        return render(request, 'displayGPS_01_fail.html')

def replaceDate(targetDate):
    l = list(targetDate)
    l[4] = '/'
    l[7] = '/'
    newDateStr = ''.join(l)
    return newDateStr

def displayGPSById(request):
    return render(request, 'displayGPS_02.html')

def displayGPSByIdSubmit(request):
    if 'startId' in request.GET and 'endId' in request.GET:
        startIdStr = request.GET['startId']
        endIdStr = request.GET['endId']
        logger.info('[view.displayGPSByIdSubmit]' + startIdStr + "---" + endIdStr)
        points = models.Points.objects.filter(id__gte=int(startIdStr), id__lte=int(endIdStr))
        return render(request, 'displayGPS_02_res.html', {'startIdStr':startIdStr, 'endIdStr':endIdStr, 'points':serializers.serialize('json', list(points))})
    return render(request, 'displayGPS_02_fail.html')


def feaAnalysis(request):
    return render(request, 'feaAnalysis.html')

def feaAnalysisSubmit(request):
    if 'targetDate' in request.GET:
        searchDate = request.GET['targetDate']
        logger.info('[view.feaAnalysisSubmit]' + str(searchDate))
        newStr = replaceDate(searchDate)
        # 根据日期查询数据库
        points = models.Points.objects.filter(day_time__contains=newStr)
        logger.info('[view.feaAnalysisSubmit]' + str(len(points)))
        # 根据GPS轨迹点集合计算特征
        _, fea = feaCalculation(points)
        logger.info('[view.feaAnalysisSubmit]' + str(len(fea)))
        return render_to_response('feaAnalysis_res.html', {'searchDate':searchDate, 'points':serializers.serialize('json', list(points)), 'fea':json.dumps(fea)})
    else:
        return render_to_response('feaAnalysis_fail.html')

def inferTM(request):
    return render(request, 'inferTM.html')

def inferTMSubmit(request):
    if 'targetDate' in request.GET:
        searchDate = request.GET['targetDate']
        logger.info('[view.inferTMSubmit]' + str(searchDate))
        newStr = replaceDate(searchDate)
        # 根据日期查询数据库
        points = models.Points.objects.filter(day_time__contains=newStr)
        logger.info('[view.inferTMSubmit]' + str(len(points)))
        # 根据GPS轨迹点集合计算特征
        segmentList, fea = feaCalculation(points)
        logger.info('[view.inferTMSubmit]' + str(len(fea)))
        # [bike, bus, car, plane, train, walk]
        TMLabel, TMLabelPro = loadModelPredict(fea)
        return render_to_response('inferTM_res.html', 
            {'searchDate':searchDate, 'points':serializers.serialize('json', list(points)), 
            'segmentList':json.dumps(segmentList),
            # 'segmentList':serializers.serialize('json', list(segmentList)),
            'TMLabel':json.dumps(TMLabel), 'TMLabelPro':json.dumps(TMLabelPro)})
    else:
        return render_to_response('inferTM_fail.html')
