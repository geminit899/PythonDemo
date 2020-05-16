import tensorflow as tf
import importlib

if __name__ == '__main__':
    super_param = {
        'drop_out': 1,
        'learning_rate': 0.01,
        'epochs': 500,
        'batch_size': 128
    }

    x = tf.placeholder(tf.float32)
    y = tf.placeholder(tf.float32)
    keep_prob = tf.placeholder(tf.float32)

    module = importlib.import_module('TrainImpl')
    TrainImpl = getattr(module, 'TrainImpl')
    test = TrainImpl(x, y, keep_prob, super_param)
    mnist = test.transform()
    test.variables()
    optimizer = test.modal()
    loss = test.loss()
    accuracy = test.accuracy()

    with tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)

        for i in range(super_param['epochs']):
            batch_x, batch_y = mnist.train.next_batch(super_param['batch_size'])
            _, loss_train, acc_train = sess.run([optimizer, loss, accuracy], feed_dict={x: batch_x, y: batch_y, keep_prob: super_param['drop_out']})
            print('Iter ' + str(i) + ', Minibatch Loss= ' + '{:.2f}'.format(loss_train) + ', Training Accuracy= ' + '{:.2f}'.format(acc_train))


