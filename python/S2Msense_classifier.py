import copy
import random
import numpy as np
import torch
from plot import plot_confusion_matrix
from tensorboardX import SummaryWriter
from torch.nn import Conv2d
from torch.nn.parameter import Parameter
from data_loader import get_train_test_loaders_sim,get_train_test_loaders_real
import torch.nn as nn
from options import Options
from da_att import PAM_Module,CAM_Module
from torchvision.models.resnet import resnet18

class FeatureExtractor(nn.Module):
    def __init__(self, features,features1, pam, cam):
        super().__init__()
        self.features = features
        self.features1 = features1
        self.alpha = Parameter(torch.zeros(1))
        self.gamma = Parameter(torch.zeros(1))
        self.conv = Conv2d(in_channels=1024, out_channels=512, kernel_size=1)
        self.maxpool = nn.MaxPool2d(7)
        self.pam = pam
        self.cam = cam
        self.fc00 = nn.Linear(1024 * 7 * 7, 1024)
        self.ln = nn.LayerNorm([1024, 7, 7])
        self.bn = nn.BatchNorm2d(1024)
        self.bn1 = nn.BatchNorm2d(1024)
    def forward(self, x):
        feature0 = self.features(x[:,0:3,:,:])
        feature1 = self.features1(x[:,3:6,:,:])
        feature = torch.cat([feature0, feature1], dim=1)
        feature = self.bn1(feature)
        outpam = self.pam(feature)
        outcam = self.cam(feature)
        out = outcam*self.alpha+outpam*self.gamma+feature
        out = self.bn(out)

        return out
class FeatureExtractor1(nn.Module):
    def __init__(self, features, features1, pam, cam):
        super().__init__()
        self.features = features
        self.features1 = features1
        self.maxpool = nn.MaxPool2d(7)
        self.pam = pam
        self.cam = cam
        self.fc00 = nn.Linear(1024 * 7 * 7, 1024)
    def forward(self, x):
        out = self.features1(x[:,3:6,:,:])
        return out
class S2Msense(nn.Module):
    def __init__(self, num_classes):
        super(S2Msense, self).__init__()
        self.pam = PAM_Module(512)
        self.cam = CAM_Module(512)
        self.pam1 = PAM_Module(1024)
        self.cam1 = CAM_Module(1024)
        self.pam2 = PAM_Module(1024)
        self.cam2 = CAM_Module(1024)
        resnet = resnet18(pretrained=False)
        self.features = nn.Sequential(*list(resnet.children())[:-2])
        self.features1 = nn.Sequential(*list(resnet.children())[:-2])
        self.extractor = FeatureExtractor(self.features, self.features1, self.pam1, self.cam1)
        self.extractor1 = FeatureExtractor1(self.features, self.features1, self.pam1, self.cam1)
        self.maxpool = nn.MaxPool2d(7)
        self.maxpool2 = nn.MaxPool2d(7)
        self.avgpool1 = nn.AvgPool2d(7)
        self.avgpool2 = nn.AvgPool2d(7)
        self.conv = Conv2d(512, 512, 7, 7, 3)
        self.fc00 = nn.Linear(2 * 1024 * 7 * 7, 2 * 1024)
        self.fc01 = nn.Linear(2 * 1024, 1024)
        self.fc0 = nn.Linear(1024, 4)
        self.fc1 = nn.Linear(1024, 256)
        self.fc2 = nn.Linear(256, 120)
        self.fc3 = nn.Linear(120, 4)
        self.fc1_angle = nn.Linear(1024, 256)
        self.fc2_angle = nn.Linear(256, 120)
        self.fc3_angle = nn.Linear(120, num_classes)
        self.fc_angle = nn.Linear(1024, num_classes)
    def forward(self, x):
        out1 = self.extractor(x)
        out1 = self.maxpool(out1)
        out1 = out1.view(out1.size(0), -1)
        out1 = self.fc0(out1)
        return  out1



def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # 多GPU时
        torch.backends.cudnn.deterministic = True  # 确定性算法
        torch.backends.cudnn.benchmark = False  # 关闭自动优化
def run(device):

    train_losses = []
    train_accs = []
    test_accs = []
    set_seed()
    args = Options().initialize()
    # 替换为实际路径
    ROOT_DIR_sim = "train_simdata"
    ROOT_DIR_real = "test_realdata"
    BATCH_SIZE = 16
    patience = 100  # 早停

    writer = SummaryWriter('./logs_%s' % args.model)
    criterion = nn.CrossEntropyLoss()
    for K in range(4,5):
        best_acc = 0
        best_error = 200
        no_improve_count = 0
        trainloader= get_train_test_loaders_sim(
            root_dir=ROOT_DIR_sim,
            batch_size=BATCH_SIZE,
            n=K
        )

        testloader_target = get_train_test_loaders_real(
            root_dir=ROOT_DIR_real,
            batch_size=BATCH_SIZE,
            n=K
        )
        net = S2Msense(K).to(device)
        optimizer = torch.optim.Adam(net.parameters(), lr=1e-4)

        print("Start Training, %s!" % args.model)
        with open("acc.txt", "w") as f:
            with open("log.txt", "w")as f2:
                for epoch in range(0, args.Epoch):
                    print('\nEpoch: %d' % (epoch + 1))
                    net.train()
                    sum_loss = 0.0
                    correct = 0.0
                    correct1 = 0.0
                    total = 0.0
                    for i, data in enumerate(trainloader, 0):

                        inputs, labels, labels_action, labels_angle = data
                        inputs, labels, labels_action, labels_angle  = inputs.to(device), labels.to(device), labels_action.to(device), labels_angle.to(device)
                        optimizer.zero_grad()
                        outputs0= net(inputs)
                        loss_act = criterion(outputs0, labels_action)
                        _, predicted = torch.max(outputs0.data, 1)
                        loss = loss_act
                        loss.backward()
                        optimizer.step()
                        sum_loss += loss.item()
                        total += labels.size(0)
                        predicted1 = torch.argmax(outputs0.data, 1)
                        correct1 += predicted1.eq(labels_action.data).cpu().sum()
                    print('[epoch:%d, iter:%d] Loss: %.03f | Acc_act: %.3f%% '
                          % (epoch + 1, (i + 1), sum_loss / (i + 1), 100. * correct1 / total))
                    print("Waiting Test!")

                    train_loss = sum_loss / (i + 1)
                    train_acc = 100. * correct1 / total

                    with torch.no_grad():
                        correct1 = 0
                        total = 0
                        result1 = np.zeros((4,4))

                        for data in  testloader_target:
                            net.eval()
                            images, labels, labels_action, labels_angle,data_path = data
                            images, labels,labels_action, labels_angle = images.to(device), labels.to(device), labels_action.to(device), labels_angle.to(device)
                            outputs0= net(images)
                            total += labels.size(0)
                            predicted1 = torch.argmax(outputs0.data, 1)
                            m = labels_action.cpu()
                            n = predicted1.cpu()
                            for row, col in zip(m, n):
                                result1[row, col] += 1
                            correct1 += (predicted1 == labels_action).sum()
                        print(' Test Acc_act：%.3f%% ' % (100. * correct1 / total))
                        current1_acc = 100. * correct1 / total
                        train_losses.append(train_loss)
                        train_accs.append(train_acc)
                        test_accs.append(current1_acc)
                        writer.add_scalar('Loss/train', train_loss, epoch+1)
                        writer.add_scalar('Accuracy/train', train_acc, epoch+1)
                        writer.add_scalar('Accuracy/test', current1_acc, epoch+1)
                        if best_error is None or current1_acc > best_acc:
                            best_acc = current1_acc
                            best_model = copy.deepcopy(net)
                            print(f'===== best_acc: {best_acc:.4f} ======   ==== acc_act: {current1_acc:.4f} =====')
                            no_improve_count = 0
                            cnf_matrix1 = result1
                            attack_types1 = ['step', 'kick','fall','sit']##attack_types1 = ['step', 'kick','fall','sit']
                            plot_confusion_matrix(cnf_matrix1, classes=attack_types1,txt='action confusion_resnet',normalize=True,
                                                  title='Normalized confusion matrix')
                        else:
                            no_improve_count += 1  # 准确率未提升，计数器+1
                            print(f'No improvement: {no_improve_count}/{patience}')

                        # 早停条件判断
                        if no_improve_count >= patience:
                            print(f'Early stopping triggered at epoch {epoch}!')
                            break
                    if no_improve_count >= patience:
                        break
                epochs = range(1, len(train_losses) + 1)
                with open("training_log.txt", "w") as f:
                    f.write("Epoch\tTrain_Loss\tTrain_Acc\tTest_Acc\n")
                    for i in range(len(train_losses)):
                        f.write(f"{i + 1}\t{train_losses[i]:.6f}\t{train_accs[i]:.4f}\t{test_accs[i]:.4f}\n")
                torch.save(best_model.state_dict(), '%s/bestmodel_class_K_={}_act_acc={}.pth'.format(K,best_acc) % ('./sim_model/'))
                print("Training Finished, TotalEPOCH=%d" % args.Epoch)

if __name__ == '__main__':

    device = torch.device( "cuda")
    torch.backends.cudnn.enabled = False
    print(device)
    run(device)