# from hdfs import InsecureClient

if __name__ == '__main__':
    file_read_path = '/home/geminit/work/ttt.sh'
    file_write_path = '/home/geminit/work/ttt.txt'
    hdfs_url = 'http://192.168.0.114:50070'
    hdfs_path = '/tyx/test/justatest/test.jpg'

    # read from file
    read_file = open(file_read_path, mode='rb')
    file_data = read_file.read()
    read_file.close()

    # # write to hdfs
    # write_hdfs = InsecureClient(hdfs_url, root='/', user='hdfs', timeout=1000)
    # write_hdfs.write(hdfs_path, file_data, overwrite=True, append=False)
    #
    # # read from hdfs
    # read_hdfs = InsecureClient(hdfs_url, root='/', user='hdfs', timeout=1000)
    # with read_hdfs.read(hdfs_path) as reader:
    #     hdfs_data = reader.read()

    # write to file
    write_file = open(file_write_path, mode='wb')
    write_file.write(file_data)
    write_file.close()

