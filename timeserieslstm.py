# -*- coding: utf-8 -*-
"""timeserieslstm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1C5Xc9bNV8Me8MXYSqYLLl0ZL9OGc8bzV

##Fajri Yanti



>M03 - Time Series LSTM Project
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from pandas.plotting import register_matplotlib_converters
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

df = pd.read_csv('london.csv',
                  parse_dates=['timestamp'],
                  index_col='timestamp')
df.head()

df.shape

df.info()

df['hour'] = df.index.hour
df['day_month'] = df.index.day
df['day_week'] = df.index.dayofweek
df['month'] = df.index.month

data_train= int(len(df) * .7)
data_test = len(df) - data_train
train, test = df.iloc[0:data_train], df.iloc[data_train:len(df)]
print(len(train), len(test))

columns = ['t1', 't2', 'hum', 'wind_speed']
transformer = RobustScaler()
transformer = transformer.fit(train[columns].to_numpy())
train.loc[:, columns] = transformer.transform(
  train[columns].to_numpy()
)
test.loc[:, columns] = transformer.transform(
  test[columns].to_numpy()
)

cnt_transformer = RobustScaler()
cnt_transformer = cnt_transformer.fit(train[['cnt']])
train['cnt'] = cnt_transformer.transform(train[['cnt']])
test['cnt'] = cnt_transformer.transform(test[['cnt']])

def ds_new(X, y, time_steps=1):
    X1, y1 = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        X1.append(v)
        y1.append(y.iloc[i + time_steps])
    return np.array(X1), np.array(y1)

time_steps = 10

X_train, y_train = ds_new(train, train.cnt, time_steps)
X_test, y_test = ds_new(test, test.cnt, time_steps)
print(X_train.shape, y_train.shape)

model = keras.Sequential()
model.add(
  keras.layers.Bidirectional(
    keras.layers.LSTM(
      units=128,
      input_shape=(X_train.shape[1], X_train.shape[2])
    )
  )
)
model.add(keras.layers.Dropout(rate=0.2))
model.add(keras.layers.Dense(units=1))
model.compile(loss='mse', 
              optimizer=Adam(learning_rate=0.001),
              metrics=['mean_absolute_error'])

history = model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    shuffle=False
)

plt.figure(figsize=(15,7))
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='validation')
plt.legend()

y_predict = model.predict(X_test)

y_train_reshape = cnt_transformer.inverse_transform(y_train.reshape(1, -1))
y_test_reshape = cnt_transformer.inverse_transform(y_test.reshape(1, -1))
y_predict_reshape = cnt_transformer.inverse_transform(y_predict)

plt.figure(figsize=(20, 20))
plt.plot(y_test_reshape.flatten(), label='true')
plt.plot(y_predict_reshape.flatten(), label='predicted')
plt.legend()

