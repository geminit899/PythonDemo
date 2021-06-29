import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import confusion_matrix


class CategoricalTruePositives(keras.metrics.Metric):
    def __init__(self, name="categorical_true_positives", **kwargs):
        super(CategoricalTruePositives, self).__init__(name=name, **kwargs)
        self.true_positives = self.add_weight(name="ctp", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.reshape(tf.argmax(y_pred, axis=1), shape=(-1, 1))
        values = tf.cast(y_true, "int32") == tf.cast(y_pred, "int32")
        values = tf.cast(values, "float32")
        if sample_weight is not None:
            sample_weight = tf.cast(sample_weight, "float32")
            values = tf.multiply(values, sample_weight)
        self.true_positives.assign_add(tf.reduce_sum(values))

    def result(self):
        return self.true_positives

    def reset_states(self):
        # The state of the metric will be reset at the start of each epoch.
        self.true_positives.assign(0.0)


class CustomCallback(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        compare = {'epoch': epoch}
        compare.update(logs)


if __name__ == '__main__':
    inputs = keras.Input(shape=(784,), name="digits")
    x = layers.Dense(64, activation="relu", name="dense_1")(inputs)
    x = layers.Dense(64, activation="relu", name="dense_2")(x)
    outputs = layers.Dense(10, activation="softmax", name="predictions")(x)
    model = keras.Model(inputs=inputs, outputs=outputs)


    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    # Preprocess the data (these are NumPy arrays)
    x_train = x_train.reshape(60000, 784).astype("float32") / 255
    x_test = x_test.reshape(10000, 784).astype("float32") / 255
    y_train = y_train.astype("float32")
    y_test = y_test.astype("float32")
    # Reserve 10,000 samples for validation
    x_val = x_train[-10000:]
    y_val = y_train[-10000:]
    x_train = x_train[:-10000]
    y_train = y_train[:-10000]

    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=1e-3),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=[keras.metrics.SparseCategoricalAccuracy(), CategoricalTruePositives()],
    )
    model.fit(x_train, y_train, batch_size=64, epochs=5, callbacks=[CustomCallback()])


    # results = model.evaluate(x_test, y_test, batch_size=128)

    predict_y = model.predict(x_test)
    true_classes = np.argmax(predict_y, 1)
    labels = range(len(set(true_classes)))
    cm = confusion_matrix(true_classes, y_test, labels=labels)
    cm_str = "["
    for i in range(0, len(cm)):
        cm_str += "["
        for j in range(0, len(cm[i])):
            cm_str += str(cm[i][j])
            if not j == len(cm[i]) - 1:
                cm_str += ","
        cm_str += "]"
    cm_str += "]"



    print(1)
