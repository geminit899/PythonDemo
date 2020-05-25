from tensorboard import program
from multiprocessing import Process

def fix_port():
    argv = [
        "",
        "--logdir", '/Users/geminit/PycharmProjects/PythonDemo/Tensorflow/log/example',
        '--port', str(6055),
    ]
    tensorboard = program.TensorBoard()
    tensorboard.configure(argv)
    print(tensorboard.main())

def none_fix_port():
    def new_process():
        port = 6005
        while True:
            argv = [
                "",
                "--logdir", '/Users/geminit/PycharmProjects/PythonDemo/Tensorflow/log/example',
                '--port', str(port),
            ]
            tensorboard = program.TensorBoard()
            tensorboard.configure(argv)
            tensorboard.main()
            port += 1
    for i in range(1):
        p = Process(target=new_process)
        p.start()


if __name__ == '__main__':
    fix_port()
