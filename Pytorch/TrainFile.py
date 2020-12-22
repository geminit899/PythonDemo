import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

class TrainFile():
    def __init__(self, super_param):
        self.super_param = super_param

    def get_model(self):
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
        return Net()

    def get_optimizer(self, model, learning_rate):
        return optim.SGD(model.parameters(), lr=learning_rate, momentum=self.super_param['momentum'])

    def transform(self):
        train_dataset = datasets.MNIST(root='./minist_data/', train=True, transform=transforms.ToTensor(),
                                       download=True)
        test_dataset = datasets.MNIST(root='./minist_data/', train=False, transform=transforms.ToTensor())

        return train_dataset, test_dataset

    def train(self, model, train_loader, optimizer):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = Variable(data), Variable(target)

            optimizer.zero_grad()
            output = model(data)

            loss = F.nll_loss(output, target)
            loss.backward()

            optimizer.step()

    def test(self, model, test_loader):
        test_loss = 0
        correct = 0

        for data, target in test_loader:
            data, target = Variable(data), Variable(target)
            output = model(data)

            test_loss += F.nll_loss(output, target).item()

            pred = output.data.max(1)[1]
            correct += pred.eq(target.data.view_as(pred)).cpu().sum()

        loss = round(test_loss, 2)
        acc = round((correct / len(test_loader.dataset)).__float__(), 2)
        return loss, acc
