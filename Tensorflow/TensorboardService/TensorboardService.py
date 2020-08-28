# -*- coding: utf-8 -*-
import os
import importlib

from tornado import web
from tornado import httpserver
from tornado import ioloop
from tornado.wsgi import WSGIContainer


def file_scp(local_path, taskId):
    import paramiko
    remote_path = config['path']
    t = paramiko.Transport((config['host'], config['port']))
    t.connect(username=config['username'], password=config['password']) # 登录远程服务器
    sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议

    remote_files = sftp.listdir(remote_path)
    for file in remote_files:  # 遍历读取远程目录里的所有文件
        if file.split('-')[0] == taskId:
            remote_file = os.path.join(remote_path, file)
            local_file_path = os.path.join(local_path, file)
            if not os.path.exists(local_file_path):
                os.mkdir(local_file_path)
            local_file = os.path.join(local_file_path, 'events.out.tfevents.' + file)
            sftp.get(remote_file, local_file)

    t.close()


def hdfs_scp(local_path, taskId):
    from hdfs import InsecureClient
    remote_path = config['path']
    hdfs = InsecureClient('http://' + config['host'] + ':' + config['port'], root='/', user='hdfs', timeout=1000)
    remote_files = hdfs.list(remote_path)
    for file in remote_files:  # 遍历读取远程目录里的所有文件
        if file.split('-')[0] == taskId:
            remote_file = os.path.join(remote_path, file)
            local_file_path = os.path.join(local_path, file)
            if not os.path.exists(local_file_path):
                os.mkdir(local_file_path)
            local_file = os.path.join(local_file_path, 'events.out.tfevents.' + file)
            with hdfs.read(remote_file) as reader:
                hdfs_data = reader.read()
            write_file = open(local_file, mode='wb')
            write_file.write(hdfs_data)
            write_file.close()


class TensorboardHandler(web.RequestHandler):
    def get(self, taskId):
        if self.request.path.startswith('/' + taskId + '/htsc'):
            self.request.path = self.request.path[len('/' + taskId + '/htsc'):]
        elif self.request.path.startswith('/' + taskId):
            self.request.path = self.request.path[len('/' + taskId):]

        local_path = os.path.join(tmp_dir, 'log', taskId)
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        if self.request.path == '/data/plugins_listing':
            if config['type'] == 'file':
                file_scp(local_path, taskId)
            elif config['type'] == 'hdfs':
                hdfs_scp(local_path, taskId)

        tb_app = self.settings["manager"].new_instance(taskId, local_path, reload_interval=5)
        WSGIContainer(tb_app)(self.request)


class TensorboardWebApplication(web.Application):
    def __init__(self):
        handlers = [
            (r"/(?P<taskId>\w+)/.*", TensorboardHandler),
        ]
        super(TensorboardWebApplication, self).__init__(handlers)


if __name__ == '__main__':
    read_config = open('./config.json', mode='r')
    config = eval(read_config.read())
    read_config.close()

    tmp_dir = os.path.join(os.getcwd(), 'train-tmp')

    web_app = TensorboardWebApplication()

    module = importlib.import_module('tensorflow_manager')
    manager = getattr(module, 'manager')
    web_app.settings["manager"] = manager

    http_server = httpserver.HTTPServer(web_app)
    http_server.listen(6005)
    ioloop.IOLoop.current().start()