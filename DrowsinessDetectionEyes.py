import numpy as np
import os
import random
import time

from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D

import cv2

# read training images
DATADIR = "./train/"
# CATEGORIES = os.listdir(DATADIR)
CATEGORIES = ["Closed", "Open"]
IMG_SIZE = 100

training_data = []
for category in CATEGORIES:
    path = os.path.join(DATADIR, category)  # path to cats or dogs dir
    class_num = CATEGORIES.index(category)
    for img in os.listdir(path):
        try:
            img_array = cv2.imread(os.path.join(path, img),
                                   cv2.IMREAD_GRAYSCALE)  # colour is not specific in this use-case
            new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
            training_data.append([new_array, class_num])
        except Exception as e:
            pass

random.shuffle(training_data)

X = []  # features
y = []  # labels

for features, label in training_data:
    X.append(features)
    y.append(label)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)  # -1 is default, last 1 for grey scale
y = np.array(y)
y = to_categorical(y)

batch_size = 64
epochs = 20
num_classes = 4

# compare different architectures
dense_layers = [1]
layer_sizes = [16, 32]
conv_layers = [3, 5]

model = [Sequential() for i in range(len(dense_layers) * len(layer_sizes) * len(conv_layers))]
idx = 0

for dense_layer in dense_layers:
    for layer_size in layer_sizes:
        for conv_layer in conv_layers:
            # analyse model
            NAME = 'Drowsiness_Detection_Model_{}_{}_conv_{}_nodes_{}_dense_{}'.format(idx, conv_layer, layer_size,
                                                                                       dense_layer, int(time.time()))
            print(NAME)

            # input layer
            model[idx].add(Conv2D(layer_size, (3, 3), input_shape=X.shape[1:]))
            model[idx].add(Activation('relu'))
            model[idx].add(MaxPooling2D(pool_size=(2, 2)))

            # hidden convulational layers (='filters')
            for l in range(conv_layer - 1):
                model[idx].add(Conv2D(layer_size, (3, 3)))
                model[idx].add(Activation('relu'))
                model[idx].add(MaxPooling2D(pool_size=(2, 2)))

            # hidden dense (=fully connected) layers
            model[idx].add(Flatten())
            for l in range(dense_layer):
                model[idx].add(Dense(layer_size))
                model[idx].add(Activation('relu'))

            # output layer
            model[idx].add(Dense(len(CATEGORIES)))
            model[idx].add(Activation('sigmoid'))

            model[idx].compile(loss='binary_crossentropy',
                               optimizer='adam',
                               metrics=['accuracy'])

            model[idx].fit(X, y, batch_size=4, epochs=5,
                           validation_split=0.2)  # appropriate batch size depends on size of data set
            idx += 1

model[0].save('drowsinessEyeCnn.model')