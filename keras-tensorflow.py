import csv
import os
import sys
import numpy as np
import pandas as pd
import operator

from keras.models import Sequential
from keras.layers import Dense, Activation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils.np_utils import to_categorical, normalize
from sklearn.utils import shuffle

dataPath = 'CleanedTrafficData'
resultPath = 'results_keras_tensorflow'
if not os.path.exists(resultPath):
    print('result path {} created.'.format(resultPath))
    os.mkdir(resultPath)
    
dep_var = 'Label'

cat_names = ['Dst Port', 'Protocol']
cont_names = ['Timestamp', 'Flow Duration', 'Tot Fwd Pkts',
              'Tot Bwd Pkts', 'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max',
              'Fwd Pkt Len Min', 'Fwd Pkt Len Mean', 'Fwd Pkt Len Std',
              'Bwd Pkt Len Max', 'Bwd Pkt Len Min', 'Bwd Pkt Len Mean',
              'Bwd Pkt Len Std', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean',
              'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Tot',
              'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
              'Bwd IAT Tot', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max',
              'Bwd IAT Min', 'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags',
              'Bwd URG Flags', 'Fwd Header Len', 'Bwd Header Len', 'Fwd Pkts/s',
              'Bwd Pkts/s', 'Pkt Len Min', 'Pkt Len Max', 'Pkt Len Mean',
              'Pkt Len Std', 'Pkt Len Var', 'FIN Flag Cnt', 'SYN Flag Cnt',
              'RST Flag Cnt', 'PSH Flag Cnt', 'ACK Flag Cnt', 'URG Flag Cnt',
              'CWE Flag Count', 'ECE Flag Cnt', 'Down/Up Ratio', 'Pkt Size Avg',
              'Fwd Seg Size Avg', 'Bwd Seg Size Avg', 'Fwd Byts/b Avg',
              'Fwd Pkts/b Avg', 'Fwd Blk Rate Avg', 'Bwd Byts/b Avg',
              'Bwd Pkts/b Avg', 'Bwd Blk Rate Avg', 'Subflow Fwd Pkts',
              'Subflow Fwd Byts', 'Subflow Bwd Pkts', 'Subflow Bwd Byts',
              'Init Fwd Win Byts', 'Init Bwd Win Byts', 'Fwd Act Data Pkts',
              'Fwd Seg Size Min', 'Active Mean', 'Active Std', 'Active Max',
              'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min']

def loadData(fileName):
    dataFile = os.path.join(dataPath, fileName)
    pickleDump = '{}.pickle'.format(dataFile)
    if os.path.exists(pickleDump):
        df = pd.read_pickle(pickleDump)
    else:
        df = pd.read_csv(dataFile)
        df = df.dropna()
        df = shuffle(df)
        df.to_pickle(pickleDump)
    return df

def multiclass_baseline_model(inputDim=-1):
    model = Sequential()
    model.add(Dense(79, activation='relu', input_shape=(inputDim,)))
    model.add(Dense(128, activation='relu'))
    
    model.add(Dense(3, activation='softmax')) #This is the output layer
    
    model.compile(optimizer='adam',
                 loss='categorical_crossentropy',
                 metrics=['accuracy'])
    return model

def binary_baseline_model():
    model = Sequential()
    model.add(Dense(79, activation='relu', input_shape=(79,)))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(64, activation='relu'))
    
    model.add(Dense(2, activation='softmax')) #Output layer
    
    model.compile(optimizer='adam',
                 loss='binary_crossentropy',
                 metrics=['accuracy'])
    return model

def experiment(dataFile, optimizer='adam', epochs=10, batch_size=10):
    seed = 7
    np.random.seed(seed)
    cvscores = []
    print('optimizer: {} epochs: {} batch_size: {}'.format(
        optimizer, epochs, batch_size))
    
    data = loadData(dataFile)
    data_y = data.pop('Label')
    
    #transform named labels into numerical values
    encoder = LabelEncoder()
    encoder.fit(data_y)
    data_y = encoder.transform(data_y)
    dummy_y = to_categorical(data_y)
    data_x = normalize(data.values)
    
    #define 5-fold cross validation test harness
    inputDim = len(data_x[0])
    print('inputdim = ', inputDim)
    fn_name="multiclass_baseline_model"
    model_name = "{}_{}_{}_{}_{}".format(dataFile, optimizer, epochs, batch_size, fn_name)
  
    #Separate out data
    X_train, X_test, y_train, y_test = train_test_split(data_x, dummy_y, test_size=0.2)
    
    #create model
    model = multiclass_baseline_model(inputDim)

    #train
    print("Training " + dataFile + "...")
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)
    
    #save model
    model.save(resultPath + "/models/" + model_name + ".model")
    
    scores = model.evaluate(X_test, y_test, verbose=1)
    acc, std_dev = results.mean()*100, results.std()*100
    print('Baseline: accuracy: {:.2f}%: std-dev: {:.2f}%'.format(acc, std_dev))
    
    resultFile = os.path.join(resultPath, dataFile)
    with open('{}.result'.format(resultFile), 'a') as fout:
        fout.write('accuracy: {:.2f} std-dev: {:.2f}\n'.format(acc, std_dev))
        
        
#Run experiments on these files
experiment('02-14-2018.csv')
experiment('02-15-2018.csv')
experiment('02-16-2018.csv')
experiment('02-22-2018.csv')
experiment('02-23-2018.csv')
experiment('03-01-2018.csv')
experiment('03-02-2018.csv')
