import sys
import os
import zipfile
import importlib
import struct
import shutil
import tensorflow as tfVersion
if tfVersion.__version__.startswith('1'):
    pass
elif tfVersion.__version__.startswith('2'):
    import tensorflow.compat.v1 as tf
    tf.disable_eager_execution()
    tf.disable_v2_behavior()
else:
    raise Exception('tensorflow版本不支持：' + tfVersion.__version__)

def write_int(value, stream):
    stream.write(struct.pack("!i", value))


def read_int(stream):
    length = stream.read(4)
    if not length:
        raise EOFError
    return struct.unpack("!i", length)[0]


def read_utf8(stream):
    length = read_int(stream)
    if length == -1:
        raise EOFError
    elif length == -5:
        return None
    s = stream.read(length)
    return s.decode("utf-8")


def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
            zipf.write(pathfile, arcname)
    zipf.close()


class TensorflowRunner:
    def __init__(self, infile):
        # get the path of unzip python files, and load it as a class named train.
        local_unzip_path = read_utf8(infile)
        class_name = read_utf8(infile)
        sys.path.append(local_unzip_path)
        module = importlib.import_module(class_name)
        self.TrainImpl = getattr(module, class_name)

        # get the modal's save path
        self.result_save_path = read_utf8(infile)
        self.compare_save_path = read_utf8(infile)
        self.modal_name = read_utf8(infile)

        # get super_param
        super_param_str = read_utf8(infile)
        self.super_param = eval(super_param_str)

        # get the source
        self.source = eval(read_utf8(infile))

        python_tmp_dir = os.path.join(os.getcwd(), 'data', 'Annotation', 'Annotation-Train', 'tensorflow-tmp')
        self.tmp_dir = os.path.join(python_tmp_dir, self.modal_name)
        self.tmp_result = os.path.join(self.tmp_dir, 'result')
        if not os.path.exists(self.tmp_result):
            os.makedirs(self.tmp_result)


    def get_batch(self, batch, epoch, batch_size):
        batch_x = []
        batch_y = []
        length = len(batch[0])
        start_index = (epoch - 1) * batch_size % length
        for i in range(batch_size):
            index = (start_index + i) % length
            batch_x.append(batch[0][index])
            batch_y.append(batch[1][index])
        return batch_x, batch_y

    def run(self):
        x = tf.placeholder(tf.float32)
        y = tf.placeholder(tf.float32)
        keep_prob = tf.placeholder(tf.float32)

        train = self.TrainImpl(x, y, keep_prob, self.super_param)
        train.variables()

        files, annotations, categories = self.read()
        transformed_data = train.transform(files, annotations, categories)

        trainModal = train.modal()
        trainLoss = train.loss()
        trainAccuracy = train.accuracy()

        session = tf.InteractiveSession()
        session.run(tf.initialize_all_variables())

        saver = tf.train.Saver()

        compares = []
        for i in range(1, int(self.super_param['epochs']) + 1):
            batch_x, batch_y = self.get_batch(transformed_data, i, int(self.super_param['batchSize']))
            session.run([trainModal],
                        feed_dict={x: batch_x, y: batch_y, keep_prob: float(self.super_param['dropout'])})
            if i % 10 == 0 or i == int(self.super_param['epochs']):
                _, loss, acc = session.run([trainModal, trainLoss, trainAccuracy],
                                           feed_dict={x: batch_x, y: batch_y, keep_prob: 1})
                compare = {
                    'epoch': i,
                    'loss': round(loss, 2),
                    'accuracy': round(acc, 2)
                }
                compares.append(compare)
                self.saveCompare(compares)
        # save model result
        saver.save(session, os.path.join(self.tmp_result, 'result'), global_step=int(self.super_param['epochs']))
        zip_file = os.path.join(self.tmp_dir, 'result.zip')
        make_zip(self.tmp_result, zip_file)
        self.copy_file_to_remote(zip_file, self.result_save_path)

        self.stop()

    def read(self):
        files = []
        annotations = []
        file_array = self.source['fileArray']
        categories = self.source['categories']
        self.storage_type = self.source['storageType']
        self.hdfs_url = self.source['host']
        for file in file_array:
            path = file['path']
            annotations.append(file['annotations'])
            data = self.read_from_file(path)
            files.append(data)
        return files, annotations, categories

    def saveCompare(self, compares):
        compare = {
            'compares': compares
        }
        # save model compare
        self.write_to_file(bytes(str(compare), encoding='utf-8'), self.compare_save_path)

    def read_from_file(self, path):
        if self.storage_type == "file":
            f = open(path, mode='rb')
            data = f.read()
            f.close()
            return data
        elif self.storage_type == "hdfs":
            from hdfs import InsecureClient
            fs = InsecureClient(self.hdfs_url, root="/", user="hdfs", timeout=1000)
            with fs.read(path) as reader:
                return reader.read()

    def write_to_file(self, data, path):
        if self.storage_type == "file":
            dir = path[0:path.rindex("/")]
            if not os.path.exists(dir):
                os.makedirs(dir)
            f = open(path, mode='wb')
            f.write(data)
            f.close()
        elif self.storage_type == "hdfs":
            from hdfs import InsecureClient
            fs = InsecureClient(self.hdfs_url, root="/", user="hdfs", timeout=1000)
            fs.write(path, data, overwrite=True, append=False)

    def copy_file_to_remote(self, local_path, remote_path):
        data = self.read_from_file(local_path)
        self.write_to_file(data, remote_path)

    def stop(self):
        shutil.rmtree(self.tmp_dir)
