import sys
import numpy as np
import torch
from torch.autograd import Variable
import copy

from utils import set_random_seed, get_minibatches_idx, analyze_terminal_scaling_laws
from imbalanced_data import load_imbalanced_data_from_pickle
from train_models import build_model, simple_test_batch
from representation_analysis import analyze_representations_imbalance

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.set_default_tensor_type('torch.cuda.FloatTensor')


def training_dynamic_analysis(trainloader, model, loss_function, optimizer, config):
    model.train()
    rate_reduction_matrix = []
    loss_list = []
    for epoch in range(config['epoch_num']):
        if epoch == int(config['epoch_num'] / 3):
            for g in optimizer.param_groups:
                g['lr'] = config['lr'] / 10
            print('divide current learning rate by 10')
        elif epoch == int(config['epoch_num'] * 2 / 3):
            for g in optimizer.param_groups:
                g['lr'] = config['lr'] / 100
            print('divide current learning rate by 10')
        total_loss = 0
        minibatches_idx = get_minibatches_idx(len(trainloader), minibatch_size=config['simple_train_batch_size'],
                                              shuffle=True)
        for minibatch in minibatches_idx:
            inputs = torch.Tensor(np.array([list(trainloader[x][0].cpu().numpy()) for x in minibatch]))
            targets = torch.Tensor(np.array([list(trainloader[x][1].cpu().numpy()) for x in minibatch]))
            inputs, targets = Variable(inputs.cuda()).squeeze(1), Variable(targets.long().cuda()).squeeze()
            optimizer.zero_grad()
            outputs = model(inputs).squeeze()
            loss = loss_function(outputs, targets)
            total_loss += loss * len(minibatch)
            loss.backward()
            optimizer.step()
        total_loss /= len(trainloader)
        print('epoch:', epoch, 'loss:', total_loss)
        loss_list.append(total_loss.item())
    rate_reduction_list = analyze_representations_imbalance(trainloader, copy.deepcopy(model), config)
    rate_reduction_matrix.append(rate_reduction_list)
    return rate_reduction_matrix

def run_dynamic_analysis():
    data_option = sys.argv[1].split('=')[1]
    model_option = sys.argv[2].split('=')[1]
    layer_num = int(sys.argv[3].split('=')[1])
    hidden_size = int(sys.argv[4].split('=')[1])
    measure_option = sys.argv[5].split('=')[1]
    optimization = sys.argv[6].split('=')[1]
    lr = float(sys.argv[7].split('=')[1])
    config = {'dir_path': 'save', 'data': data_option, 'model': model_option,
              'simple_train_batch_size': 128, 'simple_test_batch_size': 100, 'epoch_num': 600,
              'momentum': 0.9, 'weight_decay': 5e-4,
              't1': 5, 'big_class_sample_size': 2500, 'small_class_sample_size': 500, 'R': '5',
              'normalization': None, 'eps': None, 'measure': measure_option, 'class_num': 10,
              'layer_num': layer_num, 'input_size': 100, 'hidden_size': hidden_size, 'optimization': optimization}
    if config['optimization'] == 'sgd':
        config['lr'] = lr
    elif config['optimization'] == 'adam':
        config['lr'] = lr
    else:
        config['lr'] = lr
    if data_option == 'fashion_mnist' or data_option == 'cfm' or data_option == 'cc':
        config['color_channel'] = 1
    else:
        config['color_channel'] = 3
    model_path = config['dir_path'] + '/models/' + config['data'] + '_' + config['model'] + '_' \
                 + str(config['layer_num']) + '_' + str(config['hidden_size']) + '_' + config['optimization'] + \
                 '_' + str(config['lr']) + '_imbalanced.pt'
    terminal_layer_path = config['dir_path'] + '/figures/' + config['data'] + '_' + config['model'] + '_' \
                          + str(config['layer_num']) + '_' + str(config['hidden_size']) + '_' + config['measure'] \
                          + '_' + config['optimization'] + '_' + str(config['lr']) + \
                          '_imbalanced_terminal_layer_regression.png'

    set_random_seed(666)
    print('load data from pickle')
    train_data, test_data = load_imbalanced_data_from_pickle(config)
    print('build model')
    model, loss_function, optimizer = build_model(config)
    print('training dynamics analysis')
    rate_reduction_matrix = training_dynamic_analysis(train_data, model, loss_function, optimizer, config)
    print('plot representation dynamic')
    analyze_terminal_scaling_laws(rate_reduction_matrix[-1], terminal_layer_path)
    print('save model')
    torch.save(model.state_dict(), model_path)
    print('load model')
    model.load_state_dict(torch.load(model_path))
    train_res = simple_test_batch(train_data, model, config)
    test_res = simple_test_batch(test_data, model, config)
    print('train accuracy', train_res)
    print('test accuracy', test_res)


if __name__ == '__main__':
    run_dynamic_analysis()
