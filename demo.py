import os
import random
import numpy as np
from pyspark import Row
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from hdfs import InsecureClient


def load_mnist(local_path):
    fs = InsecureClient('http://htsp.htdata.com:50070', root="/", user="yarn", timeout=1000)
    with fs.read('/cdap/file/mnist.npz') as reader:
        mnist = reader.read()
        f = open(local_path, mode='wb')
        f.write(mnist)
        f.close()


def compute(rdd):
    path = os.path.join(os.getcwd(), 'mnist.npz')
    load_mnist(path)
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
    # Preprocess the data (these are NumPy arrays)
    x_train = x_train.reshape(60000, 784).astype("float32") / 255
    y_train = y_train.astype("float32")
    # slice mnist into 10 peaces, get random 1
    index = random.randint(0, 9)
    start_index = index * 6000
    end_index = (index + 1) * 6000
    x_train = x_train[start_index:end_index]
    y_train = y_train[start_index:end_index]

    inputs = keras.Input(shape=(784,), name="digits")
    x = layers.Dense(64, activation="relu", name="dense_1")(inputs)
    x = layers.Dense(64, activation="relu", name="dense_2")(x)
    outputs = layers.Dense(10, activation="softmax", name="predictions")(x)
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=0.01),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=[keras.metrics.SparseCategoricalAccuracy()],
    )

    acc = []
    class CustomCallback(tf.keras.callbacks.Callback):
        def __init__(self, acc):
            super().__init__()
            self.acc = acc

        def on_epoch_end(self, epoch, logs=None):
            self.acc.append(logs['sparse_categorical_accuracy'])

    model.fit(x_train, y_train, batch_size=128, epochs=5, callbacks=[CustomCallback(acc)])
    acc_percent = str(round(acc[len(acc) - 1], 4) * 100) + '%'
    result = [Row(offset=1, body=acc_percent)]
    return result

