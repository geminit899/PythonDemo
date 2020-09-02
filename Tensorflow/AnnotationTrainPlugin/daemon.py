import os
import sys
import socket
import struct
import time
from socket import AF_INET, SOCK_STREAM, SOMAXCONN


def write_int(value, stream):
    stream.write(struct.pack("!i", value))


def write_with_length(obj, stream):
    write_int(len(obj), stream)
    stream.write(obj)


if __name__ == '__main__':
    # Create a listening socket on the AF_INET loopback interface
    listen_sock = socket.socket(AF_INET, SOCK_STREAM)
    listen_sock.bind(('127.0.0.1', 0))
    listen_sock.listen(max(1024, SOMAXCONN))
    listen_host, listen_port = listen_sock.getsockname()

    # sent listen_port back to the process run this .py
    stdout_bin = os.fdopen(sys.stdout.fileno(), 'wb', 4)
    write_int(listen_port, stdout_bin)
    stdout_bin.flush()

    # connect to java
    sock, _ = listen_sock.accept()
    infile = os.fdopen(os.dup(sock.fileno()), "rb", 65536)
    outfile = os.fdopen(os.dup(sock.fileno()), "wb", 65536)

    try:
        # init TensorflowRunner
        from tensorflowRunner import TensorflowRunner
        runner = TensorflowRunner(infile)
        runner.run()
    except:
        write_int(-1, outfile)
        write_with_length(str(sys.exc_info()).encode("utf-8"), outfile)
        runner.stop()
    else:
        write_int(1, outfile)
    outfile.flush()
    time.sleep(3)
    sock.close()
