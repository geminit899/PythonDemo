from hdfs import InsecureClient

if __name__ == '__main__':
    data = {
        'compares': {
            'epoch': 1,
            'loss': 2,
            'accuracy': 3
        }
    }

    fs = InsecureClient("http://htsp.htdata.com:50070", root="/", user="hdfs", timeout=1000)
    fs.write("/cdap/namespaces/default/Train-Task-compare/1-1", bytes(str(data), encoding='utf-8'), overwrite=True, append=False)