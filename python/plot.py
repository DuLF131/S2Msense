
import itertools
import numpy as np
import torch
from sklearn.manifold import TSNE
import matplotlib.patches as mpatches
from matplotlib import pyplot as plt
import seaborn as sns

def plot_confusion_matrix(cm, classes,txt, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    Input
    - cm : 计算出的混淆矩阵的值
    - classes : 混淆矩阵中每一行每一列对应的列
    - normalize : True:显示百分比, False:显示个数
    """
    if normalize:
        matrix = cm
        # print(cm.astype('float'))
        # print(cm.sum(axis=1)[:, np.newaxis])
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')
    plt.figure()
    # 设置输出的图片大小
    figsize = 16, 9
    figure, ax = plt.subplots(figsize=figsize)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    # 设置title的大小以及title的字体
    font_title = {'family': 'Times New Roman',
                  'weight': 'normal',
                  'size': 15,
                  }
    plt.title(title, fontdict=font_title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, )
    plt.yticks(tick_marks, classes)
    # 设置坐标刻度值的大小以及刻度值的字体
    plt.tick_params(labelsize=15)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    # print(labels)
    [label.set_fontname('Times New Roman') for label in labels]
    if normalize:
        fm_int = 'd'
        fm_float = '.3%'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fm_float),
                     horizontalalignment="center", verticalalignment='center', family="Times New Roman",
                     weight="normal", size=15,
                     color="white" if cm[i, j] > thresh else "black")

    else:
        fm_int = 'd'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fm_int),
                     horizontalalignment="center", verticalalignment='bottom',
                     color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    # 设置横纵坐标的名称以及对应字体格式
    font_lable = {'family': 'Times New Roman',
                  'weight': 'normal',
                  'size': 15,
                  }
    plt.ylabel('True label', font_lable)
    plt.xlabel('Predicted label', font_lable)

    plt.savefig(f"{txt}.eps", dpi=600, format='eps', bbox_inches='tight')
    plt.savefig(f"{txt}.png", dpi=800, format='png', bbox_inches='tight')

def calculate_angular_error(pred_angles, true_angles):
    """
    计算角度预测误差（考虑角度周期性）

    参数:
    pred_angles: 预测角度数组 (0-360度)
    true_angles: 真实角度数组 (0-360度)

    返回:
    errors: 最小角度误差数组 (0-180度)
    """
    pred_angles = np.array(pred_angles)
    true_angles = np.array(true_angles)
    # 计算原始差值
    pred_over_360 = np.any(pred_angles > 360)
    true_over_360 = np.any(true_angles > 360)

    # 如果有任何角度大于360度，打印标识
    if pred_over_360 or true_over_360:
        print("⚠️ 角度值大于360度警告 ⚠️")

        # 打印具体信息
        if pred_over_360:
            print(f"预测角度中有 {np.sum(pred_angles > 360)} 个值大于360度")
            print(f"最大预测角度: {np.max(pred_angles):.2f}°")

        if true_over_360:
            print(f"真实角度中有 {np.sum(true_angles > 360)} 个值大于360度")
            print(f"最大真实角度: {np.max(true_angles):.2f}°")

        print("建议检查数据预处理或模型输出")
        print("----------------------------------")


    diff = np.abs(pred_angles - true_angles)

    # 考虑角度周期性（360度模运算）
    errors = np.minimum(diff, 360 - diff)

    return errors

def plot_angular_error_cdf(pred_angles, true_angles, isplt,title="angle_error CDF"):
    """
    绘制角度预测误差的CDF图

    参数:
    pred_angles: 预测角度数组
    true_angles: 真实角度数组
    title: 图表标题
    """
    # 计算角度误差
    errors = calculate_angular_error(pred_angles, true_angles)

    # 计算CDF
    sorted_errors = np.sort(errors)
    cdf = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors)

    # 创建图表
    plt.figure(figsize=(10, 6))

    # 绘制CDF曲线
    plt.plot(sorted_errors, cdf, 'b-', linewidth=2.5, label='CDF')

    # 添加关键点标记
    for percentile in [50, 75, 90, 95]:
        error_value = np.percentile(errors, percentile)
        plt.scatter(error_value, percentile / 100, color='red', s=80, zorder=5)
        plt.text(error_value + 1, percentile / 100 + 0.02,
                 f'{percentile}%: {error_value:.2f}°',
                 fontsize=10, ha='left')

    # 添加中位线
    median_error = np.median(errors)
    plt.axvline(median_error, color='green', linestyle='--', alpha=0.7)
    plt.text(median_error + 1, 0.05, f'middle: {median_error:.2f}°',
             fontsize=10, color='green')

    # 添加平均误差
    mean_error = np.mean(errors)
    plt.axvline(mean_error, color='purple', linestyle='--', alpha=0.7)
    plt.text(mean_error + 1, 0.15, f'mean: {mean_error:.2f}°',
             fontsize=10, color='purple')

    # 美化图表
    plt.title(title, fontsize=14)
    plt.xlabel('angle_error (°)', fontsize=12)
    plt.ylabel('cdf', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim(0, max(180, np.max(errors) * 1.1))
    plt.ylim(0, 1.05)
    plt.legend(loc='lower right')

    # 添加误差分布直方图
    ax2 = plt.gca().inset_axes([0.6, 0.15, 0.3, 0.3])
    sns.histplot(errors, bins=30, kde=True, ax=ax2, color='skyblue')
    ax2.set_title('CDF', fontsize=9)
    ax2.set_xlabel('')
    ax2.set_ylabel('')

    plt.tight_layout()
    if isplt:
        plt.savefig('angle_cdf.png', dpi=800, format='png', bbox_inches='tight')

    # 返回关键统计值
    return {
        'mean_error': mean_error,
        'median_error': median_error,
        'max_error': np.max(errors),
        'min_error': np.min(errors),
        'std_dev': np.std(errors),
        'percentiles': {
            '50%': np.percentile(errors, 50),
            '75%': np.percentile(errors, 75),
            '90%': np.percentile(errors, 90),
            '95%': np.percentile(errors, 95)
        }
    }

def calculate_angle_from_cos_sin(cos_values, sin_values):
    """
    从余弦和正弦值计算角度（0-360度）

    参数:
    cos_values: 余弦值数组或张量
    sin_values: 正弦值数组或张量

    返回:
    angles: 角度数组（0-360度）
    """
    # 确保输入为NumPy数组
    if isinstance(cos_values, torch.Tensor):
        cos_values = cos_values.cpu().numpy()
    if isinstance(sin_values, torch.Tensor):
        sin_values = sin_values.cpu().numpy()

    # 计算角度（弧度）
    angles_rad = np.arctan2(sin_values, cos_values)

    # 将弧度转换为角度（0-360度）
    angles_deg = np.degrees(angles_rad)
    angles_deg = np.where(angles_deg < 0, angles_deg + 360, angles_deg)

    return angles_deg
def visualize_features(features,angles, labels=None,n_components=2, random_state=42):
    # pca = PCA(n_components=40 if features.shape[1] > 2 else features.shape[1])
    # umap_features= pca.fit_transform(features)
    #
    color_bins = [0, 60, 120,180,240, 300, 360]
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    color_list = [colors[np.digitize(a, color_bins) - 1] for a in angles]
    #TSNE
    RANDOM_STATE_TSNE = 777
    tsne = TSNE(n_components=3, init='pca', random_state=RANDOM_STATE_TSNE)
    umap_features = tsne.fit_transform(features)

    plt.figure(figsize=(15, 5))
    # umap_model = UMAP(n_components=n_components,
    #                  random_state=random_state,
    #                  n_neighbors=min(15, features.shape[0]-1))
    # umap_features = umap_model.fit_transform(features)


    plt.figure(figsize=(15, 10) if n_components == 3 else (10, 8))
    legend_handles = []
    # 第一个区间: [0, 60)
    legend_handles.append(mpatches.Patch(color='red', label='0°-30°'))
    # 第二个区间: [60, 120)
    legend_handles.append(mpatches.Patch(color='orange', label='30°-60°'))
    # 第三个区间: [120, 180)
    legend_handles.append(mpatches.Patch(color='yellow', label='60°-90°'))
    # 第四个区间: [180, 240) - 注意：你的bins只到180，但colors有6种颜色
    # 这里假设角度范围是0-360°，添加缺失的区间
    legend_handles.append(mpatches.Patch(color='green', label='90°-120°'))
    legend_handles.append(mpatches.Patch(color='blue', label='180°-150°'))
    legend_handles.append(mpatches.Patch(color='purple', label='150°-180°'))

    if n_components == 2:

        if labels is not None:
            unique_labels = np.unique(labels)
            for label in unique_labels:
                if label == -1:
                    plt.scatter(umap_features[labels == label, 0],
                                umap_features[labels == label, 1],
                                c='gray', alpha=0.5, s=30, label='Noise')
                else:
                    plt.scatter(umap_features[labels == label, 0],
                                umap_features[labels == label, 1],
                                c=color_list,alpha=0.7, s=50, label=f'Cluster {label}')
        else:
            plt.scatter(umap_features[:, 0], umap_features[:, 1],c=color_list, alpha=0.7)

        plt.xlabel('TSNE Dimension 1')
        plt.ylabel('TSNE Dimension 2')
        plt.title('Fall 2D TSNE Projection')
        plt.legend(handles=legend_handles, title='Angle Bins', loc='best')