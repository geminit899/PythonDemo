from abc import abstractmethod, ABCMeta


class Train(metaclass=ABCMeta):
    # 默认会声明四个变量：x, y, keep_prob, super_param
    # 实例化时，会将此四个变量传入，调用时直接使用 self.x 即可
    # 其中前三个为训练占位符，第四个为参数，通过 self.super_param['name'] 调用
    def __init__(self, x, y, keep_prob, super_param):
        self.x = x
        self.y = y
        self.keep_prob = keep_prob
        self.super_param = super_param

    # 用于用户创建其需要的变量
    @abstractmethod
    def variables(self): pass

    # 用于用户将标注文件转换为其模型训练所需的格式
    # 传入参数有三个，分别是files, annotations, categories，
    # 其中files是文件内容的list，annotations是标注的list，categories是标注类型的list。
    # 项目为文档时，annotations有两项，annotations[0]是labelCategories的list，annotations[1]是connectionCategories的list；
    #             categories也有两项，categories[0]是labels，categories[1]是connections。
    # 项目为图片时，annotations是annotationCategories的list,每一项都是当前category的annotations；
    #             categories也只有一项，categories[0]是图片标注种类list。
    #
    # 返回值应为一个二维数组 batch[[], []]，其中batch[0]是x的值，batch[1]是y的值，且batch[0]和batch[1]的长度一致。
    @abstractmethod
    def transform(self, files, annotations, categories): pass

    # 用于用户编写其训练代码，形成计算图
    @abstractmethod
    def modal(self): pass

    # 用于用户编写其损失函数
    @abstractmethod
    def loss(self): pass

    # 用于用户编写其获取精度的函数
    @abstractmethod
    def accuracy(self): pass
