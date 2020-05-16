from hdfs import InsecureClient

file_read_path = '/Users/geminit/Documents/Geminit/Image/Pic/IMG_0885.JPG'
file_write_path = '/Users/geminit/Desktop/test.jpg'
hdfs_url = 'http://192.168.0.114:50070'
hdfs_path = '/test/test.jpg'

# read from file
read_file = open(file_read_path, mode='rb')
file_data = read_file.read()
read_file.close()

# write to hdfs
write_hdfs = InsecureClient(hdfs_url, root='/', user='hdfs', timeout=1000)
write_hdfs.write(hdfs_path, file_data, overwrite=True, append=False)

# read from hdfs
read_hdfs = InsecureClient(hdfs_url, root='/', user='hdfs', timeout=1000)
with read_hdfs.read(hdfs_path) as reader:
    hdfs_data=reader.read()

# write to file
write_file = open(file_write_path, mode='wb')
write_file.write(hdfs_data)
write_file.close()

