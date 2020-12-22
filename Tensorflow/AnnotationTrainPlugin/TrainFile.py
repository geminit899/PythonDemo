# tensorflow 1.x
# import tensorflow as tf
# tensorflow 2.x
import tensorflow.compat.v1 as tf
tf.disable_eager_execution()
tf.disable_v2_behavior()


class TrainFile():
    def __init__(self, x, y, keep_prob, super_param):
        self.x = x
        self.y = y
        self.keep_prob = keep_prob
        self.super_param = super_param

    def variables(self):
        self.weights = {
            'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
            'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
            'wd1': tf.Variable(tf.random_normal([7 * 7 * 64, 1024])),
            'out': tf.Variable(tf.random_normal([1024, 10]))
        }
        self.biases = {
            'bc1': tf.Variable(tf.random_normal([32])),
            'bc2': tf.Variable(tf.random_normal([64])),
            'bd1': tf.Variable(tf.random_normal([1024])),
            'out': tf.Variable(tf.random_normal([10]))
        }

    def transform(self, files, annotations, categories):
        # tensorflow 1.x
        # from tensorflow.examples.tutorials.mnist import input_data
        # tensorflow 2.x
        from tensorflow_core.examples.tutorials.mnist import input_data
        mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
        batch_x, batch_y = mnist.train.next_batch(10000)
        return [batch_x, batch_y]

    def modal(self):
        def conv2d(x, W, b, strides=1):
            x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
            x = tf.nn.bias_add(x, b)
            return tf.nn.relu(x)

        def maxpool2d(x, k=2):
            return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1], padding='SAME')

        def conv_net(x, weights, biases, dropout):
            x = tf.reshape(x, shape=[-1, 28, 28, 1])

            conv1 = conv2d(x, weights['wc1'], biases['bc1'])
            conv1 = maxpool2d(conv1, k=2)

            conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
            conv2 = maxpool2d(conv2, k=2)

            fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
            fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
            fc1 = tf.nn.relu(fc1)
            fc1 = tf.nn.dropout(fc1, dropout)

            out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
            return out
        self.pred = conv_net(self.x, self.weights, self.biases, self.keep_prob)
        return tf.train.AdamOptimizer(learning_rate=float(self.super_param['learning_rate'])).minimize(self.loss())

    def loss(self):
        return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.pred, labels=self.y))

    def accuracy(self):
        correct_prediction = tf.equal(tf.argmax(self.pred, 1), tf.argmax(self.y, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
