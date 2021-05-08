import os
import sys
from tensorboard import program
from tensorboard.backend import application
from tensorboard import default


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    log_dir = sys.argv[3]

    import tensorboard as tbVersion
    if tbVersion.__version__.startswith('1'):
        # Tensorflow1 1.10 or above series
        from tornado import web
        from tornado import httpserver
        from tornado import ioloop
        from tornado.wsgi import WSGIContainer

        class TensorboardManger(dict):
            def create_tb_app(self, logdir, reload_interval, purge_orphaned_data):
                argv = [
                    "",
                    "--logdir", logdir,
                    "--reload_interval", str(reload_interval),
                    "--purge_orphaned_data", str(purge_orphaned_data),
                ]
                tensorboard = program.TensorBoard()
                tensorboard.configure(argv)
                return application.standard_tensorboard_wsgi(
                    tensorboard.flags,
                    tensorboard.plugin_loaders,
                    tensorboard.assets_zip_provider)

            def new_instance(self, name, logdir, reload_interval):
                if name not in self:
                    purge_orphaned_data = True
                    reload_interval = reload_interval or 30
                    self[name] = create_tb_app(logdir=logdir, reload_interval=reload_interval,
                                               purge_orphaned_data=purge_orphaned_data)
                return self[name]


        class TensorboardHandler(web.RequestHandler):
            def get(self, taskId):
                if self.request.path.startswith('/' + taskId):
                    self.request.path = self.request.path[len('/' + taskId):]

                local_path = os.path.join(log_dir, taskId)
                tb_app = manager.new_instance(taskId, local_path, reload_interval=5)
                WSGIContainer(tb_app)(self.request)


        class TensorboardWebApplication(web.Application):
            def __init__(self):
                handlers = [
                    (r"/(?P<taskId>\w+)/.*", TensorboardHandler),
                ]
                super(TensorboardWebApplication, self).__init__(handlers)


        manager = TensorboardManger()
        web_app = TensorboardWebApplication()
        http_server = httpserver.HTTPServer(web_app)
        http_server.listen(port)
        ioloop.IOLoop.current().start()
    elif tbVersion.__version__.startswith('2'):
        # 2.x.x
        from werkzeug.serving import run_simple
        from tensorboard.uploader import uploader_main

        class DispatcherMiddleware(object):
            def __call__(self, environ, start_response):
                script = environ.get("PATH_INFO", "")
                path_info = ""
                while "/" in script:
                    pre, port = script.rsplit("/", 1)
                    if port.isnumeric():
                        app = PathDispathcher(port)
                        break
                    script, last_item = script.rsplit("/", 1)
                    path_info = "/%s%s" % (last_item, path_info)
                original_script_name = environ.get("SCRIPT_NAME", "")
                environ["SCRIPT_NAME"] = original_script_name + script
                environ["PATH_INFO"] = path_info
                return app(environ, start_response)


        class PathDispathcher(object):
            def __init__(self, taskId):
                self.taskId = taskId

            def get_application(self):
                argv = [
                    "",
                    "--logdir", os.path.join(log_dir, self.taskId),
                ]
                tensorboard = program.TensorBoard(
                    default.get_plugins() + default.get_dynamic_plugins(),
                    program.get_default_assets_zip_provider(),
                    subcommands=[uploader_main.UploaderSubcommand()])
                tensorboard.configure(argv)
                return application.standard_tensorboard_wsgi(tensorboard.flags,
                                                             tensorboard.plugin_loaders,
                                                             tensorboard.assets_zip_provider)

            def __call__(self, environ, start_response):
                app = self.get_application()
                return app(environ, start_response)

        run_simple(host, port, DispatcherMiddleware(), use_debugger=True, use_reloader=True)
    else:
        raise Exception('tensorboard：' + tbVersion.__version__)

