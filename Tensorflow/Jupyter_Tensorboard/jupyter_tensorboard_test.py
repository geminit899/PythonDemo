import sys
import time
import logging
import json

from tornado import web
from tornado.wsgi import WSGIContainer

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import path_regex

class TensorboardHandler(IPythonHandler):

    @web.authenticated
    def get(self, name, path):

        if path == "":
            uri = self.request.path + "/"
            if self.request.query:
                uri += "?" + self.request.query
            self.redirect(uri, permanent=True)
            return

        self.request.path = (
            path if self.request.query
            else "%s?%s" % (path, self.request.query))

        manager = self.settings["tensorboard_manager"]
        if name in manager:
            tb_app = manager[name].tb_app
            WSGIContainer(tb_app)(self.request)
        else:
            raise web.HTTPError(404)


class TensorboardErrorHandler(IPythonHandler):
    pass

if __name__ == '__main__':
    sys.argv = ["--port=6005", "--ip=127.0.0.1", "--no-browser", "--debug"]
    from notebook.notebookapp import NotebookApp

    nb_app = NotebookApp()
    nb_app.log_level = logging.DEBUG
    nb_app.ip = '127.0.0.1'
    # TODO: Add auth check tests
    nb_app.token = ''
    nb_app.password = ''
    nb_app.disable_check_xsrf = True
    nb_app.initialize()

    global notebook_dir
    # notebook_dir should be root_dir of contents_manager
    notebook_dir = nb_app.contents_manager.root_dir

    web_app = nb_app.web_app
    base_url = web_app.settings['base_url']

    try:
        from .tensorboard_manager import manager
    except ImportError:
        nb_app.log.info("import tensorboard error, check tensorflow install")
        handlers = [
            (ujoin(
                base_url, r"/tensorboard.*"),
             TensorboardErrorHandler),
        ]
    else:
        web_app.settings["tensorboard_manager"] = manager
        from . import api_handlers

        handlers = [
            (ujoin(
                base_url, r"/tensorboard/(?P<name>\w+)%s" % path_regex),
             TensorboardHandler),
            (ujoin(
                base_url, r"/api/tensorboard"),
             api_handlers.TbRootHandler),
            (ujoin(
                base_url, r"/api/tensorboard/(?P<name>\w+)"),
             api_handlers.TbInstanceHandler),
        ]

    web_app.add_handlers('.*$', handlers)
    nb_app.log.info("jupyter_tensorboard extension loaded.")
