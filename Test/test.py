import os
from util import test


if __name__ == '__main__':
    for i in range(5):
        print(i)
        try:
            pid = os.fork()
        except:
            pass

        if pid == 0:
            test()
            os._exit(0)
    print("over")
