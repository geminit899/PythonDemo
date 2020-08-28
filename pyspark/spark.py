import os
import sys
import select
import socket
import traceback
import gc
import time
import pickle
from errno import EINTR
from socket import AF_INET, SOCK_STREAM, SOMAXCONN

from pyspark.serializers import read_int, write_int, UTF8Deserializer, PickleSerializer, BatchedSerializer

utf8_deserializer = UTF8Deserializer()
deserializer = BatchedSerializer(PickleSerializer())

class SpecialLengths(object):
    END_OF_DATA_SECTION = -1
    PYTHON_EXCEPTION_THROWN = -2
    TIMING_DATA = -3
    END_OF_STREAM = -4
    NULL = -5
    START_ARROW_STREAM = -6

def write_iterator(iterator, of):
    import pyarrow as pa
    import pandas as pd

    time.sleep(3)

    writer = None
    try:
        for series in iterator:
            pickle.dumps([series])
            df = pd.DataFrame(series.asDict(), index=[0])
            batch = pa.RecordBatch.from_pandas(df)
            if writer is None:
                writer = pa.RecordBatchStreamWriter(of, batch.schema)
            writer.write_batch(batch)
            of.flush()
        write_int(SpecialLengths.END_OF_STREAM, of)
        of.flush()
    finally:
        if writer is not None:
            writer.close()

def worker(sock):
    infile = os.fdopen(os.dup(sock.fileno()), "rb", 65536)
    outfile = os.fdopen(os.dup(sock.fileno()), "wb", 65536)

    # the path of this files
    local_unzip_path = utf8_deserializer.loads(infile)

    # add the unzip files path to sys path
    sys.path.append(local_unzip_path)
    from pythonCompute import compute as func

    input_rdd = []
    while True:
        len = read_int(infile)
        if len == SpecialLengths.END_OF_DATA_SECTION:
            break
        input_rdd.extend(pickle.loads(infile.read(len), encoding="bytes"))

    datas = func(input_rdd)
    write_iterator(datas, outfile)

    return 0


def manager():
    # Create a new process group to corral our children
    os.setpgid(0, 0)

    # Create a listening socket on the AF_INET loopback interface
    listen_sock = socket.socket(AF_INET, SOCK_STREAM)
    listen_sock.bind(('127.0.0.1', 0))
    listen_sock.listen(max(1024, SOMAXCONN))
    listen_host, listen_port = listen_sock.getsockname()

    print(listen_port)

    # sent listen_port back to the process run this .py
    stdout_bin = os.fdopen(sys.stdout.fileno(), 'wb', 4)
    write_int(listen_port, stdout_bin)
    stdout_bin.flush()

    # Initialization complete
    try:
        while True:
            try:
                ready_fds = select.select([0, listen_sock], [], [], 1)[0]
            except select.error as ex:
                if ex[0] == EINTR:
                    continue
                else:
                    raise

            if listen_sock in ready_fds:
                try:
                    sock, _ = listen_sock.accept()
                except OSError as e:
                    if e.errno == EINTR:
                        continue
                    raise

                # launch a worker process
                try:
                    while True:
                        code = worker(sock)
                        if code:
                            # wait for closing
                            try:
                                while sock.recv(1024):
                                    pass
                            except Exception:
                                pass
                            break
                        gc.collect()
                except:
                    traceback.print_exc()
                    os._exit(1)
                else:
                    os._exit(0)

    finally:
        os._exit(1)


if __name__ == '__main__':
    manager()