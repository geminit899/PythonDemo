from hdfs import InsecureClient

if __name__ == '__main__':
    hdfs_url = 'http://192.168.0.114:50070'
    hdfs = InsecureClient(hdfs_url, root='/', user='hdfs', timeout=1000)