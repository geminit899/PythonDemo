import sys
import os
import zipfile
import importlib
import struct
import tensorflow as tf


def write_int(value, stream):
    stream.write(struct.pack("!i", value))


def write_with_length(obj, stream):
    write_int(len(obj), stream)
    stream.write(obj)


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

        # get storage type and hdfs url (if is)
        self.storage_type = read_utf8(infile)
        self.hdfs_url = read_utf8(infile)

        # get the modal's save path
        self.result_save_path = read_utf8(infile)
        self.summary_save_path = read_utf8(infile)
        self.compare_save_path = read_utf8(infile)
        self.modal_name = read_utf8(infile)

        # get super_param
        super_param_str = read_int(infile)
        self.super_param = eval(super_param_str)

        # get cpu and gpu
        self.device = read_utf8(infile)

        # get the source
        self.source = eval(read_utf8(infile))

        self.tmp_dir = os.path.join(os.getcwd(), 'train-tmp', self.modal_name)
        self.tmp_result = os.path.join(self.tmp_dir, 'result')
        self.tmp_summary = os.path.join(self.tmp_dir, 'summary')
        if not os.path.exists(self.tmp_result):
            os.makedirs(self.tmp_result)
        if not os.path.exists(self.tmp_summary):
            os.makedirs(self.tmp_summary)

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

        transformed_data = train.transform(self.read())

        with tf.device(self.device):
            session = tf.InteractiveSession()
            session.run(tf.initialize_all_variables())

            saver = tf.train.Saver()

            tf.summary.scalar('loss', train.loss())
            tf.summary.scalar('accuracy', train.accuracy())
            merged_summary_op = tf.summary.merge_all()
            summary_writer = tf.summary.FileWriter(self.tmp_summary, graph=tf.get_default_graph())

            compare = {
                'loss': 0,
                'accuracy': 0
            }
            for i in range(1, int(self.super_param['epochs']) + 1):
                batch_x, batch_y = self.get_batch(transformed_data, i, int(self.super_param['batchSize']))
                session.run([train.modal()],
                            feed_dict={x: batch_x, y: batch_y, keep_prob: int(self.super_param['dropout'])})
                if i % 10 == 0:
                    _, loss, acc, summ = session.run([train.modal(), train.loss(), train.accuracy(), merged_summary_op],
                                             feed_dict={x: batch_x, y: batch_y, keep_prob: 1})
                    summary_writer.add_summary(summ, i)
                    compare['loss'] = loss
                    compare['accuracy'] = acc

            summary_writer.close()

            saver.save(session, os.path.join(self.tmp_result, 'result'), global_step=int(self.super_param['epochs']))
            self.save(compare)

            self.stop()

    def read(self):
        files = []
        annotations = []
        file_array = self.source['fileArray']
        categories = self.source['categories']
        for file in file_array:
            path = file['path']
            annotations.append(file['annotations'])
            if self.storage_type == "file":
                f = open(path, mode='rb')
                files.append(f.read())
                f.close()
            elif self.storage_type == "hdfs":
                from hdfs import InsecureClient
                fs = InsecureClient(self.hdfs_url, root="/", user="hdfs", timeout=1000)
                with fs.read(path) as reader:
                    files.append(reader.read())
        return files, annotations, categories

    def save(self, compare):
        zip_file = os.path.join(self.tmp_dir, 'result.zip')
        make_zip(self.tmp_result, zip_file)
        self.copy_file_to_remote(zip_file, self.result_save_path)

        if self.storage_type == "file":
            f = open(self.compare_save_path, mode='w', encoding="utf-8")
            f.write(str(compare))
            f.close()
        elif self.storage_type == "hdfs":
            from hdfs import InsecureClient
            fs = InsecureClient(self.hdfs_url, root="/", user="hdfs", timeout=1000)
            fs.write(self.compare_save_path, str(compare), overwrite=True, append=False)

        for root, dirs, files in os.walk(self.tmp_summary):
            for file in files:
                self.copy_file_to_remote(os.path.join(root, file), self.summary_save_path)

    def copy_file_to_remote(self, local_path, remote_path):
        f = open(local_path, mode='rb')
        data = f.read()
        f.close()

        if self.storage_type == "file":
            f = open(remote_path, mode='wb')
            f.write(data)
            f.close()
        elif self.storage_type == "hdfs":
            from hdfs import InsecureClient
            fs = InsecureClient(self.hdfs_url, root="/", user="hdfs", timeout=1000)
            fs.write(remote_path, data, overwrite=True, append=False)

    def stop(self):
        os.rmdir(self.tmp_dir)
