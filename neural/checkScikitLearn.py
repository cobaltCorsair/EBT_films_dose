# -*- coding: utf8 -*-
import os
from database import dbProxy as dbProxy
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sklearn
print(sklearn.__version__)
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer
from sklearn.pipeline import make_pipeline


client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']
data1 = dbProxy.getData4CalibrationCurveWithDoseHighLimit(collectionTifProvider, facility='Co-60 (MRRC)',
                                                  ebtLotNo='05062003',
                                                  hoursAfterIrrad=24, doseLimit=50.0)

print(data1)
x = []
y = []
for i in data1:
    x.append(data1[i])
    y.append(i)

print (x)
xTrain = np.array(x)
xTrain = xTrain[:, np.newaxis]
y = np.array(y)

model = make_pipeline(SplineTransformer(n_knots=4, degree=3), Ridge(alpha=1e-3))
model.fit(xTrain, y)

plt.plot(x, y, '*')
xPlot = np.linspace(0.0, 0.7, 100)
xPlot = xPlot[:, np.newaxis]
yPlot = model.predict(xPlot)
plt.plot(xPlot, yPlot, label="B-spline")

f1 = interp1d(x, y)
plt.plot(np.linspace(0.03, 0.7, 100), f1(np.linspace(0.03, 0.7, 100)), label="interp1d")

plt.show()