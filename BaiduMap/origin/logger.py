# -*- coding: utf-8 -*-
import os
import time


class LOGGER:
    def __init__(self):
        path = os.path.join(os.getcwd(), 'service.log')
        self.writer = open(path, mode='a')
        self.writer.write(self.get_suffix('INFO') + 'Logger created!\n')
        self.writer.flush()

    def get_suffix(self, type):
        suffix = ''
        suffix += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        suffix += ' - ' + type + ' - '
        return suffix

    def info(self, message):
        self.writer.write(self.get_suffix('INFO') + message + '\n')
        self.writer.flush()

    def error(self, message):
        self.writer.write(self.get_suffix('ERROR') + message + '\n')
        self.writer.flush()

    def close(self):
        self.writer.write(self.get_suffix('INFO') + 'Logger closed!')
        self.writer.flush()
        self.writer.close()


LOG = LOGGER()
