import pyspark.sql.types as t
import pyarrow as pa
import pandas as pd
import os
import time
import socket
from socket import AF_INET, SOCK_STREAM, SOMAXCONN
import select
from pyspark.serializers import write_int


class SpecialLengths(object):
    END_OF_DATA_SECTION = -1
    PYTHON_EXCEPTION_THROWN = -2
    TIMING_DATA = -3
    END_OF_STREAM = -4
    NULL = -5
    START_ARROW_STREAM = -6


if __name__ == '__main__':
    # Create a listening socket on the AF_INET loopback interface
    listen_sock = socket.socket(AF_INET, SOCK_STREAM)
    listen_sock.bind(('127.0.0.1', 0))
    listen_sock.listen(max(1024, SOMAXCONN))
    listen_host, listen_port = listen_sock.getsockname()

    print(listen_port)

    while True:
        ready_fds = select.select([0, listen_sock], [], [], 1)[0]
        if listen_sock in ready_fds:
            sock, _ = listen_sock.accept()
            infile = os.fdopen(os.dup(sock.fileno()), "rb", 65536)
            outfile = os.fdopen(os.dup(sock.fileno()), "wb", 65536)

            writer = None
            try:
                rdds = [t.Row(name='tyx', age=22, gender='man'), t.Row(name='xxr', age=23, gender='man')]
                for rdd in rdds:
                    df = pd.DataFrame(rdd.asDict(), index=[0])
                    batch = pa.RecordBatch.from_pandas(df)
                    if writer is None:
                        writer = pa.RecordBatchStreamWriter(outfile, batch.schema)
                    writer.write_batch(batch)
                    outfile.flush()
                write_int(SpecialLengths.END_OF_STREAM, outfile)
                outfile.flush()
            finally:
                if writer is not None:
                    writer.close()



