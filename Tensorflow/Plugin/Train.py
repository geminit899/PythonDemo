from abc import abstractmethod, ABCMeta


class Train(metaclass=ABCMeta):
    # 抽象函数
    @abstractmethod
    def transform(self): pass
    def modal(self): pass
    def loss(self): pass
    def accuracy(self): pass
