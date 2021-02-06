import json


class Name:
    def get(self):
        pass


if __name__ == '__main__':
    # read from file
    read_file = open('/home/geminit/work/content.txt', mode='rb')
    file_data = read_file.read()
    read_file.close()

    for i in range(1, 50):
        write_file = open('/home/geminit/work/Auto-Text/' + str(i) + '.txt', mode='wb')
        write_file.write(file_data)
        write_file.close()
