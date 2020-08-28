import tensorflow as tf
import os
from tensorflow_core.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

if __name__ == '__main__':
    tfVersion = tf.__version__
    if tfVersion.startswith('1'):
        pass
    elif tfVersion.startswith('2'):
        import tensorflow.compat.v1 as tf

        tf.disable_eager_execution()
        tf.disable_v2_behavior()
    else:
        raise Exception('tensorflow版本有问题：' + tfVersion)

    x = tf.placeholder(tf.float32)
    y = tf.placeholder(tf.float32)
    keep_prob = tf.placeholder(tf.float32)

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


    weights = {
        'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
        'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
        'wd1': tf.Variable(tf.random_normal([7 * 7 * 64, 1024])),
        'out': tf.Variable(tf.random_normal([1024, 10]))
    }
    biases = {
        'bc1': tf.Variable(tf.random_normal([32])),
        'bc2': tf.Variable(tf.random_normal([64])),
        'bd1': tf.Variable(tf.random_normal([1024])),
        'out': tf.Variable(tf.random_normal([10]))
    }

    pred = conv_net(x, weights, biases, keep_prob)
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.002).minimize(loss)
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    if not os.path.exists(os.path.join(os.getcwd(), 'storeModal')):
        os.makedirs(os.path.join(os.getcwd(), 'storeModal'))

    with tf.device('/cpu:0'):
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            tf.summary.scalar("loss", loss)
            tf.summary.scalar("accuracy", accuracy)
            merged_summary_op = tf.summary.merge_all()

            summary_writer = tf.summary.FileWriter('./log/example/ccc', graph=tf.get_default_graph())
            saver = tf.train.Saver()

            for i in range(50):
                batch_x, batch_y = mnist.train.next_batch(128)
                sess.run([optimizer], feed_dict={x: batch_x, y: batch_y, keep_prob: 0.9})
                if i % 10 == 0:
                    loss_train, acc_train, summary = sess.run([loss, accuracy, merged_summary_op], feed_dict={x: batch_x, y: batch_y, keep_prob: 1.})
                    summary_writer.add_summary(summary, i)
                    summary_writer.flush()
                    print('Iter ' + str(i) + ', Minibatch Loss= ' + '{:.2f}'.format(loss_train) + ', Accuracy= ' + '{:.2f}'.format(acc_train))

            summary_writer.close()

            id = 'HTSC-1263878'
            savePath = os.path.join(os.getcwd(), 'storeModal', id, 'result')
            saver.save(sess, savePath, global_step=200)
