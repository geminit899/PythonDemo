# -*- coding: utf-8 -*-
import sys
import logging


sys.argv = ["tensorboard"]

from tensorboard.backend import application   # noqa

try:
    # Tensorboard 0.4.x above series
    from tensorboard import default

    if hasattr(default, 'PLUGIN_LOADERS') or hasattr(default, '_PLUGINS'):
        # Tensorflow1 1.10 or above series
        logging.debug("Tensorboard 1.10 or above series detected")
        from tensorboard import program

        def create_tb_app(logdir, reload_interval, purge_orphaned_data):
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
    else:
        logging.debug("Tensorboard 0.4.x series detected")

        def create_tb_app(logdir, reload_interval, purge_orphaned_data):
            return application.standard_tensorboard_wsgi(
                logdir=logdir, reload_interval=reload_interval,
                purge_orphaned_data=purge_orphaned_data,
                plugins=default.get_plugins())

except ImportError:
    # Tensorboard 0.3.x series
    from tensorboard.plugins.audio import audio_plugin
    from tensorboard.plugins.core import core_plugin
    from tensorboard.plugins.distribution import distributions_plugin
    from tensorboard.plugins.graph import graphs_plugin
    from tensorboard.plugins.histogram import histograms_plugin
    from tensorboard.plugins.image import images_plugin
    from tensorboard.plugins.profile import profile_plugin
    from tensorboard.plugins.projector import projector_plugin
    from tensorboard.plugins.scalar import scalars_plugin
    from tensorboard.plugins.text import text_plugin
    logging.debug("Tensorboard 0.3.x series detected")

    _plugins = [
                core_plugin.CorePlugin,
                scalars_plugin.ScalarsPlugin,
                images_plugin.ImagesPlugin,
                audio_plugin.AudioPlugin,
                graphs_plugin.GraphsPlugin,
                distributions_plugin.DistributionsPlugin,
                histograms_plugin.HistogramsPlugin,
                projector_plugin.ProjectorPlugin,
                text_plugin.TextPlugin,
                profile_plugin.ProfilePlugin,
            ]

    def create_tb_app(logdir, reload_interval, purge_orphaned_data):
        return application.standard_tensorboard_wsgi(
            logdir=logdir, reload_interval=reload_interval,
            purge_orphaned_data=purge_orphaned_data,
            plugins=_plugins)


class TensorboardManger(dict):

    def new_instance(self, name, logdir, reload_interval):
        if name not in self:
            purge_orphaned_data = True
            reload_interval = reload_interval or 30
            self[name] = create_tb_app(logdir=logdir, reload_interval=reload_interval,
                                       purge_orphaned_data=purge_orphaned_data)
        return self[name]


manager = TensorboardManger()
