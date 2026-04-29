import random
from collections import defaultdict
import cv2
from PIL import Image,ImageOps
from torch.utils.data import DataLoader
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms
import os
import torch
import scipy.io as sio
import re
def compute_dataset_statistics(data_paths,n,batch_size):
    """
    计算数据集的均值和标准差
    """
    
    temp_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    
    temp_dataset = DatasetFromFolders0(data_paths, class_num=n, transform=temp_transform)
    temp_loader = DataLoader(temp_dataset, batch_size=batch_size, shuffle=False)
    
    mean = 0.0
    std = 0.0
    nb_samples = 0.0
    for data, _, _, _ in temp_loader:
        batch_samples = data.size(0)
        data = data.view(batch_samples, data.size(1), -1)
        mean += data.mean(2).sum(0)
        std += data.std(2).sum(0)
        nb_samples += batch_samples
    mean /= nb_samples
    std /= nb_samples
    return mean.tolist(), std.tolist()
def compute_dataset_statistics1(data_paths,n,batch_size):
    """
    计算数据集的均值和标准差
    """
    
    temp_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    
    temp_dataset = DatasetFromFolders01(data_paths, class_num=n, transform=temp_transform)
    temp_loader = DataLoader(temp_dataset, batch_size=batch_size, shuffle=False)
    
    mean = 0.0
    std = 0.0
    nb_samples = 0.0
    for data, _, _, _,_ in temp_loader:
        batch_samples = data.size(0)
        data = data.view(batch_samples, data.size(1), -1)
        mean += data.mean(2).sum(0)
        std += data.std(2).sum(0)
        nb_samples += batch_samples
    mean /= nb_samples
    std /= nb_samples
    return mean.tolist(), std.tolist()
transform = transforms.Compose([
    transforms.Resize(
        (224, 224),  
    ),
    transforms.ToTensor(),
])
class DatasetFromFolders0(Dataset):
    def __init__(self, data_dir,class_num,labels=None,transform=transform):
        self.data_dir = data_dir
        self.transform = transform
        self.class_num = class_num
        
        
    def __len__(self):
        return len(self.data_dir)
    def __getitem__(self, idx):
        data_path = self.data_dir[idx]
        angle_match = re.search(r'\d+_\d+_(\d+)\.jpg$', self.data_dir[idx])  
        
        
        angle_value = int(np.floor(int(angle_match.group(1))/100))
        
        data_path = self.data_dir[idx]
        species =['step', 'kick','fall','sit']
        for i, c in enumerate(species):
            if c in data_path:
                label0 = i
        label0_tensor = torch.tensor(label0)
        label0 = int(angle_value)
        label0_angle = torch.tensor(label0)

        if angle_value == 360:
            label = 0
        else:
            label = int((angle_value) // (360 / self.class_num))
        
        
        label_tensor = torch.tensor(label)
        
        image = Image.open(data_path).convert('RGB')
        
        data_tensor = self.transform(image)
        
        
        
        
        return data_tensor, label_tensor, label0_tensor,label0_angle
class DatasetFromFolders01(Dataset):
    def __init__(self, data_dir,class_num,labels=None,transform=transform):
        self.data_dir = data_dir
        self.transform = transform
        self.class_num = class_num
        
        
    def __len__(self):
        return len(self.data_dir)
    def __getitem__(self, idx):
        data_path = self.data_dir[idx]
        angle_match = re.search(r'\d+_(\d+)_\d+\.dat\.jpg$', self.data_dir[idx])  
        
        angle_value = int(np.floor(int(angle_match.group(1)) / 1))
        
        data_path = self.data_dir[idx]
        species = ['step', 'kick','fall','sit']
        for i, c in enumerate(species):
            if c in data_path:
                label0 = i
        label0_tensor = torch.tensor(label0)
        label0 = int(angle_value)
        label0_angle = torch.tensor(label0)

        
        if angle_value == 360:
            label =0
        else:
            label = int((angle_value ) // (360 / self.class_num))
        
        
        label_tensor = torch.tensor(label)
        
        
        image = Image.open(data_path).convert('RGB')
        

        data_tensor = self.transform(image)
        
        
        
        
        
        return data_tensor, label_tensor, label0_tensor,label0_angle,data_path
class DatasetFromFolders(Dataset):
    def __init__(self, data_dir,labels=None,transform=transform):
        self.data_dir = data_dir
        self.transform = transform
        
        
    def __len__(self):
        return len(self.data_dir)
    def __getitem__(self, idx):
        data_path = self.data_dir[idx]
        species = ['run', 'sit', 'walk','fall']
        species_to_id = dict((c, i) for i, c in enumerate(species))
        id_to_species = dict((v, k) for k, v in species_to_id.items())
        for i,c in enumerate(species):
            if c in self.data_dir[idx]:
                label =i

        
        label_tensor = torch.tensor(label)
        
        
        mat_data = sio.loadmat(data_path)
        
        data = mat_data['spectrogram_data'][:, 0:190]
        
        data= data.transpose(1,0)
        data = Image.fromarray(data.astype(np.float32))
        
        
        data_tensor = self.transform(data)

        return data_tensor, label_tensor
def get_train_test_loaders(root_dir, batch_size, shuffle_train=True):
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    for folder in folders:
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        for idx in range(len(all_files)):
            
            all_files.sort(key=lambda x: int(re.search(r'_(\d+)\.mat$', x).group(1)))
            angle_match = re.search(r'_(\d+)\.mat$', all_files[idx])  
            angle_value = int(np.floor(int(angle_match.group(1))/10))
            
            
            label1 = int(angle_value//30)
            
            if label1 == 3 :
                test_files.append(all_files[idx])
            else:
                train_files.append(all_files[idx])

    train_dataset = DatasetFromFolders(train_files)
    test_dataset = DatasetFromFolders(test_files)
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        pin_memory=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  
        pin_memory=True
    )
    return train_loader, test_loader
def get_data_loader(data_dir, batch_size,labels=None,aug=False):
    dataset = DatasetFromFolders(data_dir)
    loader = torch.utils.data.DataLoader(dataset,batch_size=batch_size, shuffle=aug)
    return loader, dataset
class DatasetFromFolders1(Dataset):
    def __init__(self, data_dir,class_num,labels=None,transform=transform):
        self.data_dir = data_dir
        self.transform = transform
        self.class_num = class_num
        
        
    def __len__(self):
        return len(self.data_dir)
    def __getitem__(self, idx):
        data_path = self.data_dir[idx]
        angle_match = re.search(r'\d+_(\d+)_\d+\.dat\.jpg$', self.data_dir[idx])  
        
        angle_value = int(np.floor(int(angle_match.group(1)) / 1))
        
        data_path = self.data_dir[idx]
        species = ['step', 'kick','fall','sit']
        for i, c in enumerate(species):
            if c in data_path:
                label0 = i
        label0_tensor = torch.tensor(label0)
        label0 = int(angle_value)
        label0_angle = torch.tensor(label0)

        if angle_value == 360:
            label =0
        else:
            label = int((angle_value ) // (360 / self.class_num))
        
        
        label_tensor = torch.tensor(label)
        
        
        image = Image.open(data_path).convert('RGB')
        width, height = image.size
        split_point = width // 2
        left_image = image.crop((0, 0, split_point, height))
        right_image = image.crop((split_point, 0, width, height))
        left_image = self.transform(left_image)
        right_image = self.transform(right_image)
        data_tensor = torch.cat([left_image, right_image], dim=0)
        
        
        
        
        
        return data_tensor, label_tensor, label0_tensor,label0_angle,data_path
def get_train_test_loaders1(root_dir, batch_size,n, shuffle_train=True):
    
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        
        all_files.sort(key=lambda x: int(re.search(r'\d+_(\d+)_\d+\.dat_combined\.jpg$', x).group(1)))
        
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_(\d+)_\d+\.dat_combined+\.jpg$', all_files[idx])
            
            
            angle_value = int(np.floor(int(angle_match.group(1)) / 1))
            
            
            
            if angle_value  == 360:
                label1 = 0
            else:
                label1 = int(angle_value  // (360 / n))
            files_by_label[label1].append(all_files[idx])
            
            
            
            
    for label, files in files_by_label.items():
        
        n_total = len(files)
        n_test = max(0, round(n_total * 0.1))  
        
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
        
        train_files.extend([f for f in files if f not in test_sample])
    
    print(len(test_files))
    print(len(train_files))
    
    
    
    normMean, normStd = compute_dataset_statistics1(train_files, n, batch_size)
    normMean1, normStd1 = compute_dataset_statistics1(test_files, n, batch_size)
    
    trainTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean, normStd)
    ])
    testTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean1, normStd1)
    ])
    
    train_dataset = DatasetFromFolders1(train_files, class_num=n, transform=trainTransform)
    test_dataset = DatasetFromFolders1(test_files, class_num=n, transform=testTransform)
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        pin_memory=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  
        pin_memory=True
    )
    return train_loader, test_loader
def get_train_test_loaders3(root_dir, batch_size,n, shuffle_train=True):
    
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        
        all_files.sort(key=lambda x: int(re.search(r'\d+_(\d+)_\d+\.dat_combined\.jpg$', x).group(1)))
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_(\d+)_\d+\.dat_combined+\.jpg$', all_files[idx])
            
            angle_value = int(np.floor(int(angle_match.group(1)) / 1))
            
            
            
            if angle_value == 360:
                label1 = 0
            else:
                label1 = int(angle_value // (360 / n))

            files_by_label[label1].append(all_files[idx])
            
            
            
            
    for label, files in files_by_label.items():
        
        n_total = len(files)
        n_test = max(1, round(n_total * 0.95))  
        
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
        
        train_files.extend([f for f in files if f not in test_sample])
    
    
    print(len(train_files))
    
    
    
    normMean, normStd = compute_dataset_statistics1(train_files, n, batch_size)
    normMean1, normStd1 = compute_dataset_statistics1(test_files, n, batch_size)
    
    trainTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean, normStd)
    ])
    testTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean1, normStd1)
    ])
    
    train_dataset = DatasetFromFolders1(train_files, class_num=n, transform=trainTransform)
    test_dataset = DatasetFromFolders1(test_files, class_num=n, transform=testTransform)

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        pin_memory=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  
        pin_memory=True
    )
    return train_loader, test_loader
class DatasetFromFolders2(Dataset):
    def __init__(self, data_dir,class_num,labels=None,transform=transform):
        self.data_dir = data_dir
        self.transform = transform
        self.class_num = class_num
        
        
    def __len__(self):
        return len(self.data_dir)
    def __getitem__(self, idx):
        data_path = self.data_dir[idx]
        angle_match = re.search(r'\d+_\d+_(\d+)\.jpg$', self.data_dir[idx])  

        angle_value = int(np.floor(int(angle_match.group(1)))/100)
        
        data_path = self.data_dir[idx]
        species =['step', 'kick','fall','sit']
        for i, c in enumerate(species):
            if c in data_path:
                label0 = i
        label0_tensor = torch.tensor(label0)
        label0 = int(angle_value)
        label0_angle = torch.tensor(label0)

        if angle_value == 360:
            label = 0
        else:
            label = int((angle_value) // (360 / self.class_num))
        
        
        label_tensor = torch.tensor(label)
        
        image = Image.open(data_path).convert('RGB')
        
        width, height = image.size
        split_point = width // 2
        left_image = image.crop((0, 0, split_point, height))
        right_image = image.crop((split_point, 0, width, height))
        
        
        left_image = self.transform(left_image)
        right_image = self.transform(right_image)
        data_tensor = torch.cat([left_image,right_image],dim=0)
        
        
        
        
        
        return data_tensor, label_tensor, label0_tensor,label0_angle
def get_train_test_loaders2(root_dir, batch_size,n, shuffle_train=True):
    
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        
        
        
        
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        
        
        all_files.sort(key=lambda x: int(re.search(r'\d+_\d+_(\d+)\.jpg$', x).group(1)))
        
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_\d+_(\d+)\.jpg$', all_files[idx])
            
            print(angle_match)
            angle_value = int(np.floor(int(angle_match.group(1))))
            
            
            
            if angle_value == 360:
                label1 = 0
            else:
                label1 = int((angle_value) // (360 / n))
            files_by_label[label1].append(all_files[idx])
    for label, files in files_by_label.items():
        n_total = len(files)
        n_test = max(1, round(n_total * 0.05))  
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
        train_files.extend([f for f in files if f not in test_sample])
    normMean, normStd = compute_dataset_statistics(train_files,n,batch_size)
    normMean1, normStd1 = compute_dataset_statistics(test_files,n,batch_size)
    
    trainTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean, normStd)
    ])
    testTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean1, normStd1)
    ])
    
    train_dataset = DatasetFromFolders2(train_files, class_num=n,transform=trainTransform)
    test_dataset = DatasetFromFolders2(test_files, class_num=n,transform=testTransform)
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        pin_memory=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  
        pin_memory=True
    )
    return train_loader, test_loader
class MatchedSourceTargetDataset(Dataset):
    def __init__(self, source_dataset, target_dataset, max_angle_diff=360):
        self.source_dataset = source_dataset
        self.target_dataset = target_dataset
        self.max_angle_diff = max_angle_diff
        
        self.matched_pairs = self._create_matched_pairs()
    def _create_matched_pairs(self):
        matched_pairs = []
        
        for target_idx in range(len(self.target_dataset)):
            target_data, target_label, target_label0, target_angle,_ = self.target_dataset[target_idx]
            
            matched_source_indices = []
            for source_idx in range(len(self.source_dataset)):
                source_data, source_label, source_label0, source_angle = self.source_dataset[source_idx]
                
                
                
                matched_source_indices.append(source_idx)
            
            if matched_source_indices:
                matched_pairs.append((matched_source_indices,target_idx))
        return matched_pairs
    def __len__(self):
        return len(self.matched_pairs)
    def __getitem__(self, idx):
        source_indices, target_idx = self.matched_pairs[idx]
        
        
        source_idx = random.choice(source_indices)
        
        source_data, source_label, source_label0, source_angle = self.source_dataset[source_idx]
        target_data, target_label, target_label0, target_angle = self.target_dataset[target_idx]
        
        
        return source_data,source_label,source_label0,target_data, target_label,target_label0
def get_train_test_loaders_real(root_dir, batch_size,n, shuffle_train=True):
    
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        
        all_files.sort(key=lambda x: int(re.search(r'\d+_(\d+)_\d+\.dat+\.jpg$', x).group(1)))
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_(\d+)_\d+\.dat\.jpg$', all_files[idx])
            
            angle_value = int(np.floor(int(angle_match.group(1)) / 1))
            
            
            
            if angle_value == 360:
                label1 = 0
            else:
                label1 = int(angle_value // (360 / n))
            files_by_label[label1].append(all_files[idx])
            
            
            
            
    for label, files in files_by_label.items():
        
        n_total = len(files)
        n_test = max(1, round(n_total * 1))  
        
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
    normMean1, normStd1 = compute_dataset_statistics1(test_files, n, batch_size)
    
    testTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean1, normStd1)
    ])
    
    test_dataset = DatasetFromFolders1(test_files, class_num=n, transform=testTransform)
    
    
    
    
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  
        pin_memory=True
    )
    return  test_loader
def get_train_test_loaders_sim(root_dir, batch_size,n, shuffle_train=True):
    
    
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    train_files = []
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        
        
        
        
        
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        
        
        all_files.sort(key=lambda x: int(re.search(r'\d+_\d+_(\d+)\.jpg$', x).group(1)))
        
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_\d+_(\d+)\.jpg$', all_files[idx])
            
            
            angle_value = int(np.floor(int(angle_match.group(1)))/100)
            
            
            
            if angle_value == 360:
                label1 = 0
            else:
                label1 = int((angle_value) // (360 / n))
            files_by_label[label1].append(all_files[idx])
    for label, files in files_by_label.items():
        n_total = len(files)
        n_test = max(0, round(n_total * 0))
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
        train_files.extend([f for f in files if f not in test_sample])
    print(len(train_files))
    normMean, normStd = compute_dataset_statistics(train_files,n,batch_size)
    trainTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean, normStd)
    ])
    train_dataset = DatasetFromFolders2(train_files, class_num=n,transform=trainTransform)
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        pin_memory=True
    )
    return train_loader
def get_train_test_loaders6(root_dir, batch_size,n, shuffle_train=True):
    folders = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
               if os.path.isdir(os.path.join(root_dir, f))]
    test_files = []
    files_by_label = defaultdict(list)
    for folder in folders:
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.endswith('.jpg')]
        all_files.sort(key=lambda x: int(re.search(r'\d+_(\d+)_\d+\.dat_combined\.jpg$', x).group(1)))
        for idx in range(len(all_files)):
            angle_match = re.search(r'\d+_(\d+)_\d+\.dat_combined+\.jpg$', all_files[idx])
            angle_value = int(np.floor(int(angle_match.group(1)) / 1))
            if angle_value == 360:
                label1 = 0
            else:
                label1 = int(angle_value // (360 / n))
            files_by_label[label1].append(all_files[idx])
    for label, files in files_by_label.items():
        
        n_total = len(files)
        n_test = max(1, round(n_total * 1))  
        
        test_sample = random.sample(files, n_test)
        test_files.extend(test_sample)
    normMean1, normStd1 = compute_dataset_statistics1(test_files, n, batch_size)
    
    testTransform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(normMean1, normStd1)
    ])
    
    test_dataset = DatasetFromFolders1(test_files, class_num=n, transform=testTransform)
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=True,  
        pin_memory=True
    )
    return  test_loader