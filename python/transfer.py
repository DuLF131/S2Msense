import numpy as np
import torch
from plot import plot_confusion_matrix
import random
from tqdm import tqdm
from torch.nn import Conv2d
from torch import nn
from S2Msense_classifier import S2Msense
from data_loader import get_train_test_loaders_real,get_train_test_loaders_sim
import copy
# %%
batch_size = 16
iterations = 3
epochs = 200
k_disc = 1
k_clf = 8
K = 4
# 替换为实际路径
ROOT_DIR = "E:\\Simulation\\sim\\1221_3person"  # 替换为实际路径
ROOT_DIR2 = "E:\\Simulation\\real\\threeperson"
ROOT_DIR3 = "E:\\Simulation\\real\\1204_train1"

BATCH_SIZE = 8
MODEL_FILE = 'C:\\Users\\Administrator\\Downloads\\dual recognition_tworgb\\python\\sim_model\\bestmodel_singleori_class_K_1103=4_all_acc=88.33333587646484_actacc=69.16667175292969_resnet18.pth'  # pretrained model using simulated dataset
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def loop_iterable(iterable):
    while True:
        yield from iterable

class Discriminator(nn.Module):
    def __init__(self, input_size=256, hidden_size1=20, hidden_size2=10):
        super(Discriminator, self).__init__()
        self.conv = Conv2d(512,256,7,7,0)

        self.layer1 = nn.Linear(input_size, hidden_size1)
        self.relu1 = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size1, hidden_size2)
        self.relu2 = nn.ReLU()
        self.output_layer = nn.Linear(hidden_size2, 1)

    def forward(self, x):
        x = self.conv(x)
        x = x.squeeze(-1).squeeze(-1)
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.layer2(x)
        x = self.relu2(x)
        x = self.output_layer(x)
        return x

def set_requires_grad(model, requires_grad=True):
    for param in model.parameters():
        param.requires_grad = requires_grad

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
set_seed()
source_model2 = S2Msense(K).to(device).eval()
weight = torch.load(MODEL_FILE, map_location=device)
source_model2.load_state_dict(weight)



source_model1 = S2Msense(K).to(device).eval()
weight = torch.load(MODEL_FILE, map_location=device)
source_model1.load_state_dict(weight)
source_model3 = source_model1.extractor
set_requires_grad(source_model1, requires_grad=False)
set_requires_grad(source_model3, requires_grad=False)

target_model1 = S2Msense(K).to(device)
weight = torch.load(MODEL_FILE, map_location=device)
target_model1.load_state_dict(weight)
target_model3 = target_model1.extractor
set_requires_grad(target_model1, requires_grad=False)
set_requires_grad(target_model3, requires_grad=False)

discriminator = Discriminator().to(device)

trainloader_source= get_train_test_loaders_sim(
    root_dir=ROOT_DIR,
    batch_size=BATCH_SIZE,
    n=K
)
trainloader_target = get_train_test_loaders_real(
    root_dir=ROOT_DIR3,
    batch_size=BATCH_SIZE,
    n=K
)
testloader_target1 = get_train_test_loaders_real(
    root_dir=ROOT_DIR2,
    batch_size=BATCH_SIZE,
    n=K
)


source_dataset = trainloader_source.dataset
target_dataset = trainloader_target.dataset



discriminator_optim = torch.optim.Adam(discriminator.parameters(), lr=1e-4, betas=(0.5, 0.999))
target_optim = torch.optim.Adam(target_model3.parameters(), lr=1e-6, betas=(0.5, 0.999))

criterion = nn.CrossEntropyLoss()
criterion_train = nn.BCEWithLogitsLoss()
reconstruction_loss = nn.MSELoss(reduction='sum')

disc_losses, disc_accuracies, disc_train_counter = [], [], []
clf_disc_losses, clf_disc_train_counter = [], []
clf_losses, clf_accuracies = [], []


best_acc = 0
for epoch in range(epochs):

    tqdm_bar = tqdm(range(iterations), desc=f'Training Epoch {epoch} ', total=iterations)
    disc_loss, disc_accuracy = 0, 0
    clf_disc_loss = 0
    test_loss, test_accuracy = 0, 0
    batch_iterator = zip(loop_iterable(trainloader_source), loop_iterable(trainloader_target))
    batch_iterator_target = loop_iterable(trainloader_target)
    for iter_idx in tqdm_bar:

        set_requires_grad(target_model1, requires_grad=False)
        set_requires_grad(target_model3, requires_grad=False)
        set_requires_grad(discriminator, requires_grad=True)

        for disc_idx in range(k_disc):
            batch_source, batch_target = next(batch_iterator)
            source_x, _, _, _ = batch_source
            target_x, _, _, _,_ = batch_target
            source_x, target_x = source_x.to(device), target_x.to(device)
            source_features = source_model3(source_x)
            target_features = target_model3(target_x)
            discriminator_x = torch.cat([source_features, target_features])
            discriminator_y = torch.cat(
                [torch.ones(source_x.shape[0], device=device), torch.zeros(target_x.shape[0], device=device)])
            preds = discriminator(discriminator_x).view(-1)
            loss = criterion_train(preds, discriminator_y)
            discriminator_optim.zero_grad()
            loss.backward()
            discriminator_optim.step()
            disc_loss += loss.item()
            disc_losses.append(loss.item())
            disc_batch_accuracy = ((preds > 0).long() == discriminator_y.long()).float().mean().item()
            disc_accuracy += disc_batch_accuracy
            disc_accuracies.append(disc_batch_accuracy)
        set_requires_grad(target_model1, requires_grad=False)
        set_requires_grad(target_model3, requires_grad=True)
        set_requires_grad(discriminator, requires_grad=False)
        for clf_idx in range(k_clf):
            batch_source, batch_target = next(batch_iterator)
            source_x, _, _, _ = batch_source
            target_x, _, _, _,_ = batch_target
            (target_x_l, labels_target, labels0_t, _,_) = next(batch_iterator_target)
            target_x = target_x.to(device)
            source_x = source_x.to(device)
            source_features = source_model3(source_x)
            target_features = target_model3(target_x)
            target_features = target_features.squeeze()
            source_features = source_features.squeeze()
            discriminator_y = torch.ones(target_x.shape[0], device=device)
            preds = discriminator(target_features)
            preds =preds.view(-1)
            loss = criterion_train(preds, discriminator_y)
            target_optim.zero_grad()
            loss.backward()
            target_optim.step()
            clf_disc_loss += loss.item()
            clf_disc_losses.append(loss.item())
        tqdm_bar.set_postfix(disc_loss=disc_loss / ((iter_idx + 1) * k_disc),
                             disc_accuracy=disc_accuracy / ((iter_idx+ 1) * k_disc),
                             clf_disc_loss=clf_disc_loss / ((iter_idx + 1) * k_clf))
        with torch.no_grad():
            correct = 0
            correct1 = 0
            total = 0
            result = np.zeros((K, K))
            result1 = np.zeros((4, 4))
            angle_predict = []
            angle_true = []
            angle_wrong_files = []
            action_wrong_files = []
            source_model2.extractor.load_state_dict(target_model3.state_dict())
            net = source_model2
            set_requires_grad(net, requires_grad=False)
            for data in testloader_target1:
                net.to(device)
                net.eval()
                images, labels, labels_action, labels_angle, data_path = data
                images, labels, labels_action, labels_angle = images.to(device), labels.to(device), labels_action.to(
                    device), labels_angle.to(device)
                outputs0 = net(images)
                outputs = 0
                _, predicted = torch.max(outputs0.data, 1)
                i = labels.cpu()
                j = predicted.cpu()
                for row, col in zip(i, j):
                    result[row, col] += 1

                total += labels.size(0)
                angle_wrong_indices = (predicted != labels).cpu().numpy()
                for i, wrong in enumerate(angle_wrong_indices):
                    if wrong:
                        angle_wrong_files.append(data_path[i])

                predicted1 = torch.argmax(outputs0.data, 1)
                m = labels_action.cpu()
                n = predicted1.cpu()

                for row, col in zip(m, n):
                    result1[row, col] += 1
                correct1 += (predicted1 == labels_action).sum()

            current1_acc = 100. * correct1 / total
            if current1_acc > best_acc:
                best_acc = current1_acc
                best_model = copy.deepcopy(net)

                cnf_matrix1 = result1
                attack_types1 = ['step', 'kick', 'fall', 'sit']
                plot_confusion_matrix(cnf_matrix1, classes=attack_types1, txt='action confusion1', normalize=True,
                                      title='Normalized confusion matrix')
                print(' Test Acc_act：%.3f%% ' % (current1_acc))
                torch.save(best_model.state_dict(), f'weights/0202_singleoritrain_complete_dacn_epoch_{epoch}_{current1_acc}.pth')
        # torch.save(target_model.state_dict(), f'weights/wisppn-20240411_adda1_epoch_{epoch}.pkl')
