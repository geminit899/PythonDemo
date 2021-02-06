import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.transforms.functional import to_tensor
from torch.autograd import Variable
from tensorflow.keras.datasets import mnist
import numpy as np
from PIL import Image
import tensorflow as tf
import os
from sklearn.datasets import load_files
import pandas as pd

if __name__ == '__main__':
    epochs = 5
    batch_size = 64
    learning_rate = 0.01

    iii = np.array(Image.open('/home/geminit/图片/dm32_1440.jpg'))[:, :, 0]
    xxx = np.array([iii, iii])
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    dic1 = {'name': ['小明', '小红', '狗蛋', '铁柱', '111'],
            'age': [17, 20, 5, 40, 3], 'sex': ['男', '女', '女', '男', 'd']}  # 使用字典进行输入
    test_3 = pd.DataFrame(dic1)

    csv = pd.read_table('/home/geminit/work/train.csv', chunksize=10000, sep=',', encoding='gbk')
    # num表示总行数
    num = 0
    for chunk in csv:
        num += len(chunk)
    chunksize = int(0.7 * num)
    head, tail = os.path.split('/home/geminit/work/train.csv')
    data = pd.read_table('/home/geminit/work/train.csv', chunksize=chunksize, sep=',', encoding='gbk')
    i = 1
    for chunk in data:
        chunk.to_csv('/home/geminit/work/train_' + str(i) + '.csv', index=False)
        i += 1

    TRAIN_DATA_URL = 'https://storage.googleapis.com/tf-datasets/titanic/train.csv'
    train_file_path = tf.keras.utils.get_file('train.csv', TRAIN_DATA_URL)

    dataset = tf.keras.utils.get_file(fname='aclImdb.tar.gz',
                                      origin='http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz',
                                      extract=True)
    IMDB_DATADIR = os.path.join(os.path.dirname(dataset), 'aclImdb')
    train_data = load_files(os.path.join(IMDB_DATADIR, 'train'), shuffle=True)

    a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    b = np.array([[11, 22, 33], [44, 55, 66], [77, 88, 99]])
    c = np.array([[111, 222, 333], [444, 555, 666], [777, 888, 999]])
    d = np.array([[-11, -22, -33], [-44, -55, -66], [-77, -88, -99]])
    e = np.array([[101, 202, 330], [404, 505, 606], [707, 808, 909]])
    f = [to_tensor(Image.open('/home/geminit/图片/dm32_1440.jpg'))]
    f_loader = torch.utils.data.DataLoader(dataset=f, batch_size=2, shuffle=True)
    tensor = [(to_tensor(a), -1), (to_tensor(b), -2), (to_tensor(c), -3), (to_tensor(d), -4), (to_tensor(e), -5)]
    loader = torch.utils.data.DataLoader(dataset=tensor, batch_size=2, shuffle=True)
    for index, (data, y) in enumerate(loader):
        print(data)
        print(y)

    train_dataset = datasets.MNIST(root='./minist_data/', train=True, transform=transforms.ToTensor(), download=True)
    test_dataset = datasets.MNIST(root='./minist_data/', train=False, transform=transforms.ToTensor())

    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)


    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.l1 = nn.Linear(784, 520)
            self.l2 = nn.Linear(520, 320)
            self.l3 = nn.Linear(320, 240)
            self.l4 = nn.Linear(240, 120)
            self.l5 = nn.Linear(120, 10)

        def forward(self, x):
            x = x.view(-1, 784)
            x = F.relu(self.l1(x))
            x = F.relu(self.l2(x))
            x = F.relu(self.l3(x))
            x = F.relu(self.l4(x))
            return F.log_softmax(self.l5(x))


    model = Net()

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)


    def train():
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)

            loss = F.nll_loss(output, target)
            loss.backward()

            optimizer.step()


    def test(epoch):
        test_loss = 0
        correct = 0

        for data, target in test_loader:
            output = model(data)

            test_loss += F.nll_loss(output, target).item()

            pred = output.data.max(1)[1]
            correct += pred.eq(target.data.view_as(pred)).cpu().sum()

        print(
            'epoch: {}, loss: {:.2f}, accuracy: {:.2f}\n'.format(epoch, test_loss, correct / len(test_loader.dataset)))


    for epoch in range(1, epochs + 1):
        train()
        test(epoch)

    torch.save(model, 'just_a_test.pkl')
