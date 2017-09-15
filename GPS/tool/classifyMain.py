# coding=utf-8
import pandas as pd
import numpy as np
from sklearn.externals import joblib


def loadModelPredict(fea):
    rf = joblib.load('GPS/static/file/rf_model.m')
    # rf = joblib.load('../static/file/rf_model.m')
    TMLabel = []
    TMLabelPro = []
    for feature in fea:
        feaDataFrame = getDataFrame(feature)
        predictY = rf.predict(feaDataFrame)
        # [bike, bus, car, plane, train, walk]
        predictYProba = rf.predict_proba(feaDataFrame)
        TMLabel.append(predictY[0])
        # [bike, bus, car, plane, train, walk]
        TMLabelPro.append(getTMLabelProList(predictYProba[0]))
    return TMLabel, TMLabelPro


def getTMLabelProList(TMLabelPro):
    return (TMLabelPro[0], TMLabelPro[1], TMLabelPro[2], TMLabelPro[3], TMLabelPro[4], TMLabelPro[5])

def getDataFrame(feature):
    feaDataFrame = pd.DataFrame({'distance': [feature[0]],
                            '_85thV': [feature[1]],
                            'MaxV1': [feature[2]],
                            'MaxV2': [feature[3]],
                            'MedianV': [feature[4]],
                            'MinV': [feature[5]],
                            'MeanV': [feature[6]],
                            'Ev': [feature[7]],
                            'Dv':[feature[8]],
                            'HVR':[feature[9]],
                            'MVR':[feature[10]],
                            'LVR':[feature[11]],
                            '_85thA':[feature[12]],
                            'MaxA1':[feature[13]],
                            'MaxA2':[feature[14]],
                            'MedianA':[feature[15]],
                            'MinA':[feature[16]],
                            'MeanA':[feature[17]],
                            'Ea':[feature[18]],
                            'Da':[feature[19]],
                            'HAR':[feature[20]],
                            'MAR':[feature[21]],
                            'LAR':[feature[22]],
                            'TS':[feature[23]],
                            'ACR':[feature[24]],
                            'BSR':[feature[25]],
                            'ACP':[feature[26]],
                            'HCR':[feature[27]],
                            'SR':[feature[28]],
                            'VCR':[feature[29]]
                            })
    return feaDataFrame


if __name__ == '__main__':
    fea = [(348380.0762510932, 6.8362869799836403, 6.8362869799836403, 3.7106515760730199, 1.1264474092130501, 0.149696178908997, 2.4727220180208533, 2.4727220180208533, 6.3030894143421339, 0, 0, 0, 0.203922841813235, 0.203922841813235, 0.19783085539800099, 0.012480801693493899, 0.00013150286407463899, 0.083350829317234768, 0.083350829317234768, 0.0092292519921841482, 0, 0, 1, 0, 0.013474724004600933, 0, 0, 0.011307460394635973, 0.0101060430034507, 0.013474724004600933), 
    (213.3626015104968, 12.5234504780694, 12.5234504780694, 0.363414889139616, 0.28233244763530602, 0.0068210830096232297, 2.6412239948744913, 2.6412239948744913, 24.433845103153992, 0, 0, 0, 1.49786531651799, 1.49786531651799, 0.0184267690288362, 0.0034362248723825198, 0.000101290942877089, 0.30408343105720603, 0.30408343105720603, 0.35632371002952196, 0, 0, 0, 0, 0.035343495310686465, 0, 0, 0.010779757208036289, 0.035343495310686465, 0.02650762148301485), 
    (564.0193237033674, 1.0131921172712, 1.0131921172712, 0.87883856678578398, 0.50007669896738949, 0.085634322055182802, 0.520955306122307, 0.520955306122307, 0.11171854789194224, 0, 0, 1, 0.0098655626095260299, 0.0098655626095260299, 0.0077004546415161699, 0.0018827626778878952, 0.00046367136703072398, 0.0033732765319486055, 0.0033732765319486055, 1.0421442872083591e-05, 0, 0, 1, 0, 0.011508652491983278, 0, 0, 0.006442094120138719, 0.015344869989311038, 0.009590543743319399)]
    TMLabel, TMLabelPro = loadModelPredict(fea)
    print(TMLabel)
    print(TMLabelPro)