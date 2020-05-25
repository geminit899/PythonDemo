from tornado import web
from tornado import ioloop
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler

from tensorboard import program
from tensorboard.backend import application

import threading
import time

if __name__ == '__main__':
    def start_reloading_multiplexer(multiplexer, path_to_run, reload_interval):
        def _ReloadForever():
            current_thread = threading.currentThread()
            while not current_thread.stop:
                multiplexer.AddRunsFromDirectory('/Users/geminit/PycharmProjects/PythonDemo/Tensorflow/log/example', '')
                multiplexer.Reload()
                current_thread.reload_time = time.time()
                time.sleep(reload_interval)

        thread = threading.Thread(target=_ReloadForever)
        thread.reload_time = None
        thread.stop = False
        thread.daemon = True
        thread.start()
        return thread

    def TensorBoardWSGIApp(logdir, plugins, multiplexer, reload_interval,
                           path_prefix='', reload_task='auto'):
        path_to_run = application.parse_event_files_spec(logdir)
        if reload_interval >= 0:
            # We either reload the multiplexer once when TensorBoard starts up, or we
            # continuously reload the multiplexer.
            start_reloading_multiplexer(multiplexer, path_to_run, reload_interval)
        return application.TensorBoardWSGI(plugins, path_prefix)


    application.TensorBoardWSGIApp = TensorBoardWSGIApp

    argv = [
        "",
        "--logdir", '/Users/geminit/PycharmProjects/PythonDemo/Tensorflow/log/example',
        "--reload_interval", str(5),
        "--purge_orphaned_data", str(True),
    ]
    tensorboard = program.TensorBoard()
    tensorboard.configure(argv)
    app = application.standard_tensorboard_wsgi(
        tensorboard.flags,
        tensorboard.plugin_loaders,
        tensorboard.assets_zip_provider)

    wsgi_app = WSGIContainer(app)
    application = web.Application([
        (r".*", FallbackHandler, dict(fallback=wsgi_app))
    ])
    application.listen(6005)
    ioloop.IOLoop.current().start()
