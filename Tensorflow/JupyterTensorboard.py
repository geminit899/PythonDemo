from tensorboard import program
from tensorboard.backend import application
from tensorboard import default
from tensorboard.uploader import uploader_main

if __name__ == '__main__':
    argv = [
        "",
        "--logdir", '/home/geminit/pycharm/PythonDemo/Tensorflow/log/example',
    ]
    tensorboard = program.TensorBoard(
        default.get_plugins() + default.get_dynamic_plugins(),
        program.get_default_assets_zip_provider(),
        subcommands=[uploader_main.UploaderSubcommand()])
    tensorboard.configure(argv)
    app = application.standard_tensorboard_wsgi(tensorboard.flags,
                                                tensorboard.plugin_loaders,
                                                tensorboard.assets_zip_provider)
    server = tensorboard.server_class(app, tensorboard.flags)
    server.print_serving_message()
    port = server.port
    print(port)
    server.serve_forever()
