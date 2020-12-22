import torch
from Pytorch.TrainFile import TrainFile

if __name__ == '__main__':
    epochs = 5
    batch_size = 64
    learning_rate = 0.01
    super_param = {
        'momentum': 0.5
    }

    train = TrainFile(super_param)
    train_dataset, test_dataset = train.transform()

    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)

    model = train.get_model()
    optimizer = train.get_optimizer(model, learning_rate)

    for epoch in range(1, epochs + 1):
        train.train(model, train_loader, optimizer)
        loss, acc = train.test(model, test_loader)
        print('epoch: {}, loss: {}, acc: {}'.format(epoch, loss, acc))
