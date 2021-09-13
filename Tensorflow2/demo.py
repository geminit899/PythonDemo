import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


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


if __name__ == '__main__':
    inputs = keras.Input(shape=(784,), name="digits")
    x = layers.Dense(64, activation="relu", name="dense_1")(inputs)
    x = layers.Dense(64, activation="relu", name="dense_2")(x)
    outputs = layers.Dense(10, activation="softmax", name="predictions")(x)
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=0.01),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=[keras.metrics.SparseCategoricalAccuracy(), CategoricalTruePositives()],
    )

    from tensorflow.python.keras.utils.data_utils import get_file

    path = get_file(
        fname='mnist.npz',
        cache_dir='./',
        origin='mnist.npz')
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']

    # Preprocess the data (these are NumPy arrays)
    x_train = x_train.reshape(60000, 784).astype("float32") / 255
    x_test = x_test.reshape(10000, 784).astype("float32") / 255
    y_train = y_train.astype("float32")
    y_test = y_test.astype("float32")
    # Reserve 10,000 samples for validation
    x_val = x_train[-10000:]
    y_val = y_train[-10000:]
    train_x = x_train[:-10000]
    train_y = y_train[:-10000]

    compares = []
    print('train start.')
    class CustomCallback(tf.keras.callbacks.Callback):
        def __init__(self, compares):
            super().__init__()
            self.compares = compares

        def on_epoch_end(self, epoch, logs=None):
            compare = {'epoch': epoch + 1}
            compare.update(logs)
            self.compares.append(compare)
            # save model compare
            print('Epoch ' + str(epoch + 1) + ' saving.')
    model.fit(train_x, train_y, batch_size=256, epochs=5, callbacks=[CustomCallback(compares)])
    print(str(compares))
