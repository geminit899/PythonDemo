import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable
from torchvision.transforms import ToTensor
from sklearn.metrics import confusion_matrix

if __name__ == '__main__':
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
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    training_data = datasets.FashionMNIST(root="data", train=True, download=True, transform=ToTensor())
    test_data = datasets.FashionMNIST(root="data", train=False, download=True, transform=ToTensor())

    train_loader = torch.utils.data.DataLoader(dataset=training_data, batch_size=128, shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=128, shuffle=False)

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = Variable(data), Variable(target)

        optimizer.zero_grad()
        output = model(data)

        loss = F.nll_loss(output, target)
        loss.backward()

        optimizer.step()


    for data, target in test_loader:
        data, target = Variable(data), Variable(target)
        predict_y = model(data)
        print(1)

