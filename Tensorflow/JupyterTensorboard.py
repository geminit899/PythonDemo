# -*- coding: utf-8 -*-
from tornado import web
from tornado import ioloop

from tensorboard import program
from tensorboard.backend import application


if __name__ == '__main__':
    argv = [
        "",
        "--logdir", '/Users/geminit/PycharmProjects/PythonDemo/Tensorflow',
        "--reload_interval", str(30),
        "--purge_orphaned_data", str(True),
    ]
    tensorboard = program.TensorBoard()
    tensorboard.configure(argv)
    application = application.standard_tensorboard_wsgi(
                tensorboard.flags,
                tensorboard.plugin_loaders,
                tensorboard.assets_zip_provider)

    server = web.Application([
        (r".*", application),
    ])
    server.listen(8888)
    ioloop.IOLoop.current().start()


