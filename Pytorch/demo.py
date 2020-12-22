import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

if __name__ == '__main__':
    epochs = 6
    batch_size = 64
    learning_rate = 0.01

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

        print('epoch: {}, loss: {:.2f}, accuracy: {:.2f}\n'.format(epoch, test_loss, correct / len(test_loader.dataset)))

    for epoch in range(1, epochs):
        train()
        test(epoch)
