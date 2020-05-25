# -*- coding: utf-8 -*-
from tornado import web
from tornado import ioloop
from tornado.wsgi import WSGIContainer

from tensorboard import program
from tensorboard.backend import application

if __name__ == '__main__':
    argv = [
        "",
        "--logdir", '/Users/geminit/PycharmProjects/PythonDemo/Tensorflow/log/example',
        "--reload_interval", str(30),
        "--purge_orphaned_data", str(True),
    ]
    tensorboard = program.TensorBoard()
    tensorboard.configure(argv)
    app = application.standard_tensorboard_wsgi(
                tensorboard.flags,
                tensorboard.plugin_loaders,
                tensorboard.assets_zip_provider)

    class MainHandler(web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    server = web.Application([
        (r"/tt", MainHandler),
        (r"/ss", WSGIContainer(app)),
    ])
    server.listen(8888)
    ioloop.IOLoop.current().start()


