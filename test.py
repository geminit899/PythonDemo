import time


if __name__ == '__main__':
    for i in range(5):
        if i == 3:
            i = 0
        print(i)
        time.sleep(1)

