import time


if __name__ == '__main__':
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(t)
