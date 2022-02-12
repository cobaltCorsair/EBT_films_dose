# -*- coding: utf-8 -*-
import tensorflow as tf
from database import dbProxy as dbProxy
from pymongo import MongoClient
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import tensorflow as tf
#import high_order_layers.PolynomialLayers as poly

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

#model = tf.keras.Sequential()

interpFunc = interp1d(x, y)
def interpFunc2(od, a, b, c, d, e):
    func = np.poly1d([a,b,c, d, e])
    return func(od)


# mnist = tf.keras.datasets.mnist
#
# (x_train, y_train),(x_test, y_test) = mnist.load_data()
# x_train, x_test = (x_train / 128.0-1.0), (x_test / 128.0-1.0)
#
# units = 20
#
# basis = poly.b3
#
# model = tf.keras.models.Sequential([
#   tf.keras.layers.Flatten(input_shape=(28, 28)),
#   poly.Polynomial(units, basis=basis, shift=0.0),
#   tf.keras.layers.LayerNormalization(),
#   poly.Polynomial(units, basis=basis, shift=0.0),
#   tf.keras.layers.LayerNormalization(),
#   poly.Polynomial(units, basis=basis, shift=0.0),
#   tf.keras.layers.LayerNormalization(),
#   poly.Polynomial(units, basis=basis, shift=0.0),
#   tf.keras.layers.LayerNormalization(),
#   tf.keras.layers.Dense(10, activation='softmax')
# ])
#
# model.compile(optimizer='adam',
#               loss='sparse_categorical_crossentropy',
#               metrics=['accuracy'])
#
# model.fit(x_train, y_train, epochs=20, batch_size=10)
# model.evaluate(x_test, y_test)

#model = tf.keras.Sequential([tf.keras.layers.Flatten(input_shape=(1,)),
#    poly.Polynomial(50, basis=poly.b3, shift=0.0),
#    tf.keras.layers.LayerNormalization(),
#    tf.keras.layers.Dense(1, activation='softmax')
#])
# model = tf.keras.Sequential()
# xLr = model.add(tf.keras.layers.Input(shape=(1,)))
# yLr = model.add(tf.keras.layers.Dense(units=1, activation='linear'))
#model.add(tf.keras.layers.Dense(units=200, input_dim=1))
#model.add(tf.keras.layers.Dense(units=32, activation='relu'))
#model.add(tf.keras.layers.Dense(units=64, activation='relu'))
#model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))
# #model.add(tf.keras.layers.Activation('relu'))
# #model.add(tf.keras.layers.Dense(units=45))
# #model.add(tf.keras.layers.Activation('relu'))
# #model.add(tf.keras.layers.Dense(units=1))
# #model.add(tf.keras.layers.Dense(units=1))
# model.add(keras.layers.Activation('sigmoid'))
# model.add(keras.layers.Dense(units=250))
#
# model.add(keras.layers.Activation('tanh'))
# model.add(keras.layers.Dense(units=200))
#
# model.add(keras.layers.Activation('tanh'))
# model.add(keras.layers.Dense(units=150))
#
# model.add(keras.layers.Activation('tanh'))
# model.add(keras.layers.Dense(units=100))
#
# model.add(keras.layers.Activation('tanh'))
# model.add(keras.layers.Dense(units=50))
#
# model.add(keras.layers.Activation('linear'))
# model.add(keras.layers.Dense(units=1))
#
#model.compile(loss='mean_squared_error',
#              optimizer='sgd')
# loss_fn = tf.keras.losses.MeanSquaredError(reduction='sum_over_batch_size')
# model.compile(optimizer='adam',
#               #loss='sparse_categorical_crossentropy',
#               loss=loss_fn,
#               metrics=['accuracy'])
#
# #model.compile(#optimizer=tf.keras.optimizers.Adam(0.01),
# #              loss='mean_squared_error',
# #              #metrics=['accuracy']
# #              optimizer='sgd',
# #              )
#
# x1 = np.linspace(0.03, 0.7, 1000)
# y1 = interpFunc(x1)
# p_opt, p_cov = curve_fit(interpFunc2, x, y)
# y2 = interpFunc2(x1, *p_opt)
#
# x1 = x1 / np.max(x1)
# y2 = y2 / np.max(y2)
#
# model.fit(x1, y2, epochs=30, batch_size=50)
#
xTrain = np.linspace(0.0, 0.7, 100)
#
# loss_and_metrics = model.evaluate(x, y, batch_size=100)
#
# classes = model.predict(xTrain, batch_size=1)
#
# plt.plot(x, y, "*")
# plt.plot(xTrain, classes)
#
# #plt.plot(xTrain, interpFunc(xTrain))
# plt.show()
#feats = tf.estimator.infer_real_valued_columns_from_input(x)
feats = tf.contrib.learn.infer_real_valued_columns_from_input(xTrain)
#feats = [tf.feature_column.numeric_column(key = key) for key in x.columns]
# Building a 3-layer DNN with 50 units each.
classifier_tf = tf.estimator.DNNClassifier(feature_columns=feats,
                                               hidden_units=[50, 50, 50],
                                               n_classes=3)
classifier_tf.fit(x, y, steps=5000)

predictions = list(classifier_tf.predict(xTrain, as_iterable=True))
plt.plot(x, y, "*")
plt.plot(xTrain, predictions)
plt.show()