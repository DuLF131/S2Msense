clc;
clear all;
% close all;

% 参数设置
% Tx_pos = [0.45 0.1 2.2]; % 发射机位置
% Rx_pos = [0.44 0.1 -0.26]; % 接收机位置 
% Rx_pos2= [-0.35 0.1 -0.23];

% Tx_pos = [-0.4 0 0.07]; % 发射机位置
% Tx_pos2 = [2.12 0 -2.55]; % 发射机位置
% Rx_pos = [-0.4 0 -0.65]; % 接收机位置 
% Rx_pos2= [1.0 0 -2.55];

% Tx_pos = [-0.51 0 0.86]; % 发射机位置
% Tx_pos2 = [2.75 0 -2.18]; % 发射机位置
% Rx_pos = [-0.73 0 -0.65]; % 接收机位置 
% Rx_pos2 = [1.15 0 -2.03];

Tx_pos = [-0.4 0 0.07]; % 鍙戝皠鏈轰綅缃?
Tx_pos2 = [2.12 0 -2.55]; % 鍙戝皠鏈轰綅缃?
Rx_pos = [-0.4 0 -0.65]; % 鎺ユ敹鏈轰綅缃?
Rx_pos2= [1.0 0 -2.55];


fc = 60.48e9; % 载波频率
fs = 1600; % 采样率
thres_A_TRD = -40; % 阈值
drawScenario = false; % 是否绘制 场景
rcsRendering = true; % 是否渲染3D关键点
using_camera_coordinate = true; % 是否使用相机坐标系
connections34 = [1 2; 2 3; 3 5; 5 6; 6 7; 7 8; 8 9; 9 10; 8 11; 3 12; 12 13; 13 14; 14 15; 15 16; 16 17; 15 18; 1 19; 19 20; 20 21; 21 22; 1 23; 23 24; 24 25; 25 26; 3 4; 4 27; 27 28; 28 29; 29 30; 28 31; 31 32; 21 33; 25 34; 33 22; 34 26];
connections = connections34;
ellipsoid_coefs = [
    0.8, 0.4, 0.5;
    0.7, 0.4, 0.5;
    0.4, 0.4, 0.5;
    0.25, 0.25, 0.5;
    0.18, 0.18, 0.5;
    0.16, 0.16, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.4, 0.4, 0.5;
    0.25, 0.25, 0.5;
    0.16, 0.16, 0.5;
    0.16, 0.16, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.25, 0.4, 0.5;
    0.18, 0.18, 0.5;
    0.18, 0.18, 0.5;
    0.2, 0.2, 0.5;
    0.25, 0.4, 0.5;
    0.18, 0.18, 0.5;
    0.18, 0.18, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.18, 0.18, 0.5;
    0.4, 0.4, 0.5;
    0.4, 0.4, 0.5;
    0.25, 0.25, 0.5;
    0.4, 0.4, 0.5;
    0.25, 0.25, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
    0.2, 0.2, 0.5;
];
AWGN_mean = 0;
AWGN_var = 0;

action_folders = {'wkh_fall', 'liujh_fall','liuqh_fall','1203kick', '1203sit', '1203step',  'kick_1219', 'kick_1219liu', 'sit_1219', 'sit_1219liu', 'step_1219', 'step_1219liu'};
% action_folders = {'wkh_fall', 'liujh_fall','liuqh_fall'};

% action_folders = {'sit_1219liu'};
% action_folders ={'1203kick'};
base_folder = 'E:\data\sim\'; % 褰撳墠鏂囦欢澶硅矾寰?
disp(datetime('now'))






for action_idx = 1:length(action_folders)
    current_action = action_folders{action_idx};
 
    folder_path = fullfile(base_folder,['qiu_liu_wu\', current_action]);
    out_folder = fullfile(pwd, ['0429simpca\', current_action]);


    if ~exist(out_folder, 'dir')
        mkdir(out_folder);
    end

 files = dir(fullfile(folder_path, '*.mat'));
if isempty(files)
        fprintf('No .mat files found in folder: %s\n', folder_path);
        continue;
    end
% 计算每个文件需要处理的角度范围


% 遍历每个文件并进行处理
for file_idx = 1:length(files)
    filename = files(file_idx).name; % 获取文件名
    [~, base_name, ~] = fileparts(filename); % 获取不带扩展名的文件名
    input_mat_path = fullfile(folder_path, filename); % 输入路径
    
    % 计算当前文件处理的起始和结束角度

    
    % 对每个文件处理指定范围内的角度
    parfor theta_round = 1:25
      % 定义区间范围
        ranges = [10, 80; 
                  100,170;
                  190,260;
                  280,350;];
        
        % 计算每个区间的长度和总长度
        interval_lengths = ranges(:,2) - ranges(:,1);
        total_length = sum(interval_lengths);
        
        % 生成一个[0,total_length]均匀分布的随机数
        rand_val = total_length * rand();
        
        % 确定随机数落在哪个区间
        cumulative_length = 0;
        selected_range = [];
        for i = 1:size(ranges,1)
            if rand_val <= cumulative_length + interval_lengths(i)
                selected_range = ranges(i,:);
                break;
            end
            cumulative_length = cumulative_length + interval_lengths(i);
        end
        
        % 在选定的区间内生成均匀分布的随机数
        theta1_deg = selected_range(1) + (selected_range(2) - selected_range(1)) * rand();
        
        % 将角度转换为弧度（如果需要）
        theta1 = deg2rad(theta1_deg);
        theta_deg=round(rad2deg(theta1) * 100);
        
        % 输出文件路径 - 格式为"原始文件编号_theta角度值.mat"
        output_mat_path = fullfile(out_folder, sprintf('%s_%d.mat', base_name, theta_deg));
        output_jpg_path = fullfile(out_folder, sprintf('%s_%d.jpg', base_name, theta_deg));

        tic
        % 加载数据
        
       
        % 调用主函数进行频谱图生成
        [spectrogram_data, ~, ~] = simuSpectrogramx1(Tx_pos, Rx_pos, fc, fs, AWGN_mean, AWGN_var, thres_A_TRD, ...
            drawScenario, rcsRendering, input_mat_path, using_camera_coordinate, connections, ellipsoid_coefs, output_jpg_path, true, theta1);
        
        [spectrogram_data1, time_vector, freq_vector] = simuSpectrogramx1(Tx_pos2, Rx_pos2, fc, fs, AWGN_mean, AWGN_var, thres_A_TRD, ...
            drawScenario, rcsRendering, input_mat_path, using_camera_coordinate, connections, ellipsoid_coefs, output_jpg_path, true, theta1);

        % 合并数据
        
        % % % s1=spectrogram_data;
        % % % s1=s1/max(abs(s1),[],'all');
        % % % s1=mag2db(abs(s1));
        % % % s2=spectrogram_data1;
        % % % s2=s2/max(abs(s2),[],'all');
        % % % s2=mag2db(abs(s2));
        % % % bind_data = [s1, s2];
        % % % bind_data = imresize(bind_data, [100, 190], "bicubic");
        % % % bind_data((49:51),:)=-55;
        % % % t=time_vector;
        % % % f=freq_vector;
%% ================= PCA 去噪 + 多条 Doppler 频率线提取 =================

% 频率轴和时间轴
f = freq_vector(:);          % Doppler frequency, 纵轴
t = time_vector(:).';        % time, 横轴

% 原始复数 spectrogram
S1_complex = spectrogram_data;
S2_complex = spectrogram_data1;

% 转成 dB 谱图
S1_db = 20 * log10(abs(S1_complex) / max(abs(S1_complex), [], 'all') + eps);
S2_db = 20 * log10(abs(S2_complex) / max(abs(S2_complex), [], 'all') + eps);

% 设置噪声底，避免极小值影响 PCA
noiseFloorDb = -40;
S1_db = max(S1_db, noiseFloorDb);
S2_db = max(S2_db, noiseFloorDb);

% PCA 保留主成分数量
% 如果噪声很多：K_pca = 3 或 4
% 如果真实频率线比较多：K_pca = 5 到 8
K_pca = 7;

% PCA 去噪
[S1_pca, pcaInfo1] = pca_denoise_spectrogram(S1_db, K_pca, noiseFloorDb);
[S2_pca, pcaInfo2] = pca_denoise_spectrogram(S2_db, K_pca, noiseFloorDb);
bind_data = [S1_pca, S2_pca];
bind_data = imresize(bind_data, [100, 190], "bicubic");

% 如果你想人为去掉中间 0 Hz 附近，可以保留这句
% 但是注意：这会破坏低频动作特征
% bind_data((49:51),:) = -55;



        h=imagesc(bind_data);
        % 调整大小和归一化
        
        % caxis([-35,0]);
        % 
        colormap jet;
        axis off;
        set(gca,'xtick',[],'ytick',[],'xcolor','w','ycolor','w');
        set(gca,'looseInset',[0 0 0 0]);
        
        saveas(gcf,output_jpg_path);
      
        fprintf('已完成角度 %d\n', theta_round);
        toc
    end
end
end
% 主函数：生成频谱图并保存
function [spectrogram_data, time_vector, freq_vector ] = simuSpectrogramx1(Tx_pos, Rx_pos, fc, fs, AWGN_mean, AWGN_var, thres_A_TRD, ...
    drawScenario, rcsRendering, input_mat_path, using_camera_coordinate, connections, ellipsoid_coefs, output_jpg_path, pic_save,theta1)
arguments
    Tx_pos (1,3) double
    Rx_pos (1,3) double
    fc (1,1) double
    fs (1,1) double
    AWGN_mean (1,1) double
    AWGN_var (1,1) double
    thres_A_TRD (1,1) double
    drawScenario (1,1) logical
    rcsRendering (1,1) logical
    input_mat_path  (1,1) string
    using_camera_coordinate (1,1) logical
    connections (:,2) double
    ellipsoid_coefs (:,3) double
    output_jpg_path (1,1) string
    pic_save (1,1) logical
    theta1 (1,1) double 
end

data =load(input_mat_path);
% keypoints = keypoints_smooth_1euro;
keypoints = data.keypoints_smooth_maf;
timestampList = data.timestampList;
fps = data.fps;
% keypoints = keypoints(2:end,:,:);
% timestampList = timestampList(2:end);
% if fs < fps
%     fs = fps;
% end
% if ~using_camera_coordinate
%     keypoints = handword_keypoints;
% end

% keypoints = smoothdata(keypoints,1,"rlowess",5);

% %%%%%%%%%% Remove first frame %%%%%%%%%%
% keypoints = keypoints(2:end,:,:);
% timestampList = timestampList(2:end);
% handword_keypoints = handword_keypoints(2:end,:,:);
% transformations = transformations(2:end,:,:);
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Njoints = size(keypoints,2);
Nframes = length(timestampList);
frameLength = 1/fps;



keypoints = rotate_keypoints(keypoints, theta1);
center = squeeze(keypoints(1,2,:))';
TX_beam_vector=center-Tx_pos;
TX_beam_vector(2)=0;
RX_beam_vector=center-Rx_pos;
RX_beam_vector(2)=0;





% initial_point=keypoints(1,2,:);
% for i=1:size(keypoints,1)
%     for j =1:size(keypoints,2)
%         tmp = keypoints(i,j,:);
%         tmp= rotate_angle(tmp,initial_point,theta1);
%         keypoints(i,j,:)=tmp;
%     end
% end




T = frameLength*Nframes;
% Tx_pos = [0 -0.1 -1.5]; % XYZ
% Rx_pos = [0 -0.1 0]; % XYZ
% drawScenario = false;
%% plot

%% Spectrogram
% Interpolation of the data:
% fs = 3000; % new frame rate
TimeSamples = linspace(0,T,Nframes);
NframesNew = round(T*fs); % Number of frame after interpolation
TimeSamplesNew = linspace(0,T,NframesNew);
keypointsNew = zeros(length(TimeSamplesNew),Njoints,3);
for j=1:Njoints
    for k=1:3
        keypointsNew(:,j,k) = interp1(TimeSamples, keypoints(:,j,k),...
            TimeSamplesNew,'spline','extrap');
    end
end
% Calculate Radar returns from target
% Radar parameters
c = 3e8; % m/s
% fc = 60.48e9; % carrier frequency
lambda = c/fc; %(m) wavelength
for nf = 1:NframesNew
    % Narrowband CIR, see
    % https://rzy0901.github.io/post/channel/#narrowband-channel-model or
    % chapter 3 for book "wireless communication" written by goldsmith.
    cir = 0;
    for jj = 1:1:size(connections,1)
        joint1(1:3) = keypointsNew(nf,connections(jj,1),1:3);
        joint2(1:3) = keypointsNew(nf,connections(jj,2),1:3);
        % origin of constructed ellipsoid
        mid = 0.5*(joint1+joint2);
        R_Tx = norm(mid-Tx_pos);
        R_Rx = norm(mid-Rx_pos);
        % aspect vector
        aspect = joint1 - joint2;
        % semi-axis length: use per-connection ellipsoid ratios from sim_ellipsoid
        segment_length = norm(aspect);
        ka = ellipsoid_coefs(jj,1);
        kb = ellipsoid_coefs(jj,2);
        kc = ellipsoid_coefs(jj,3);
        a = ka * segment_length;
        b = kb * segment_length;
        c = kc * segment_length;
        radius = sqrt(a * b); % keep circular-section approximation energy close to the designed ellipse
        len = c;
        %%%%%%%%%%%%%%%%%%%%%%%% method 1 (dot production) %%%%%%%%%%%%%%%%%%%%%
        % Calculate theta
        Cos_Theta_i = dot(mid-Tx_pos,aspect)/norm(mid-Tx_pos)/norm(aspect);
        Theta_i = acos(Cos_Theta_i);
        Cos_Theta_s = dot(mid-Rx_pos,aspect)/norm(mid-Rx_pos)/norm(aspect);
        Theta_s = acos(Cos_Theta_s);
        % Calculate phi (possible wrong)
        Sin_Phi_i = (Tx_pos(2) - mid(2))/sqrt((Tx_pos(1)-mid(1))^2+(Tx_pos(2)-mid(2))^2);
        Phi_i = asin(Sin_Phi_i);
        Sin_Phi_s = (Rx_pos(2) - mid(2))/sqrt((Rx_pos(1)-mid(1))^2+(Rx_pos(2)-mid(2))^2);
        Phi_s = asin(Sin_Phi_s);
        % Calculate bistatic phi
        normal_vector = aspect / norm(aspect);
        Tx_projection = Tx_pos - dot(Tx_pos - mid, normal_vector) * normal_vector;
        Rx_projection = Rx_pos - dot(Rx_pos - mid, normal_vector) * normal_vector;
        bistatic_angle_phi = acos(dot(Tx_projection - mid, Rx_projection - mid) / (norm(Tx_projection - mid) * norm(Rx_projection - mid)));
        %%%%%%%%%%%%%%%%%%%%%%%% method 2 (transformation matrix) %%%%%%%%%%%%%%%%%%%%%%%%
        V = normal_vector; % normalized cylinder's axis-vector;
        U = rand(1,3);     % linear independent vector
        % U = U-(U*V')*V/norm(V);    % orthogonal vector to V
       U=U-V*(U*V');
        U = U/sqrt(U*U');  % orthonormal vector to V
        W = cross(V,U);    % vector orthonormal to V and U
        W = W/sqrt(W*W');  % orthonormal vector to V and U
        R = [U.', W.', V.'];
        T = eye(4);
        T(1:3, 1:3) = R;
        T(1:3, 4) = mid;
        Tx_local = inv(T)*[Tx_pos 1].'; Tx_local = Tx_local(1:3);
        Rx_local = inv(T)*[Rx_pos 1].'; Rx_local = Rx_local(1:3);
        [Phi_i2,Theta_i2,R_Tx2] = my_cart2sph(Tx_local(1),Tx_local(2),Tx_local(3));
        [Phi_s2,Theta_s2,R_Rx2] = my_cart2sph(Rx_local(1),Rx_local(2),Rx_local(3));
        % rcsellipsoid/R^2 is based on bistatic radar range equation
        % These two amplitudes are equal
        Amp = sqrt(brcsellipsoid_circle(len,radius,bistatic_angle_phi,Theta_i,Theta_s))/R_Rx/R_Tx;
        Amp2 = sqrt(rcsellipsoid(a,b,c,Phi_i2,Theta_i2,Phi_s2,Theta_s2))/R_Rx/R_Tx;

        % Effect of beam patterns
%        假设水平方向是全向的
%         vector_beam_Rx = [0 0 -1]; 只能代表beam的方向，这个代码就是搞笑的
%         vector_beam_Tx = [0 0 -1];
        vector_Rx_Primmitive1 = mid-Rx_pos;
        vector_Tx_Primmitive1 = mid-Tx_pos;

        vector_Rx_Primmitive = [vector_Rx_Primmitive1(1) 0  vector_Rx_Primmitive1(3)];
        vector_Tx_Primmitive = [vector_Tx_Primmitive1(1) 0 vector_Tx_Primmitive1(3)];
       
        Cos_Theta_Tx = dot(vector_Tx_Primmitive(),TX_beam_vector)/norm(vector_Tx_Primmitive)/norm(TX_beam_vector);
        Theta_TX = rad2deg(acos(Cos_Theta_Tx));
        
        Cos_Theta_Rx = dot(vector_Rx_Primmitive,RX_beam_vector)/norm(vector_Rx_Primmitive)/norm(RX_beam_vector);
        Theta_RX = rad2deg(acos(Cos_Theta_Rx));

        Cos_Phi_RX = dot(vector_Rx_Primmitive(), vector_Rx_Primmitive1)/norm(vector_Rx_Primmitive)/norm( vector_Rx_Primmitive1);
        Cos_Phi_TX = dot(vector_Tx_Primmitive(), vector_Tx_Primmitive1)/norm(vector_Tx_Primmitive)/norm( vector_Tx_Primmitive1);
        Phi_TX = rad2deg(acos(Cos_Phi_TX));
        Phi_RX = rad2deg(acos(Cos_Phi_RX));
        Phi_max = 30;
        Phi_min = 30/2;
        % gain_Tx_Rx1=0;
        % if Theta_TX>13 || Theta_RX >13
        %     gain_Tx_Rx1=0;
        % 
        % elseif Theta_TX>=6.5 || Theta_RX >=6.5
        %     gain_Tx_Rx1 = 1-(max(Theta_TX,Theta_RX)-6.5)/(13-6.5);
        % else
        %     gain_Tx_Rx1=1;
        % end
        % gain_Tx_Rx2=0;
        % if Phi_RX>Phi_max || Phi_TX >Phi_max
        %     gain_Tx_Rx2=0;
        % 
        % elseif Phi_TX>=Phi_min || Phi_RX >=Phi_min
        %     gain_Tx_Rx2 = 1-(max(Phi_TX,Phi_RX)-Phi_min)/(Phi_max-Phi_min);
        % else
        %     gain_Tx_Rx2=1;
        % end
        gain_Tx_Rx = af_factor(Theta_TX,Phi_TX,Theta_RX,Phi_RX);
% %         %phi_Primmitive_Rx = abs(atan(vector_Rx_Primmitive(2)/vector_Rx_Primmitive(1)));
% %         phi_Primmitive_Rx = atan2(vector_Rx_Primmitive(2), vector_Rx_Primmitive(1));
% %        % phi_Primmitive_Tx = abs(atan(vector_Tx_Primmitive(2)/vector_Tx_Primmitive(1)));
% %         phi_Primmitive_Tx = atan2(vector_Tx_Primmitive(2), vector_Tx_Primmitive(1));
% %         gain_Tx_Rx = 1;
% %         if phi_Primmitive_Rx > 22.5*pi/180 || phi_Primmitive_Tx > 22.5
% %                 gain_Tx_Rx = 1/4;
% % %                 gain_Tx_Rx = 1/20;
% %         end
        
%         sin(Theta_i)-sin(Theta_i2)
%         sin(Theta_s)-sin(Theta_s2)
%         cos(Theta_i)+cos(Theta_i2)
%         cos(Theta_s)+cos(Theta_s2)
%         R_Tx-R_Tx2
%         R_Rx-R_Rx2
%         bistatic_angle_phi-abs(Phi_s2-Phi_i2)
%         Amp-Amp2

        Phase = exp(-1i*2*pi*(R_Tx+R_Rx-(norm(Tx_pos-Rx_pos)))/lambda);%% 可能需要修改
        cir_joint = gain_Tx_Rx*Amp*Phase;
        if isnan(cir_joint)
            cir_joint = 0;
        end
        cir = cir + cir_joint;
    end
    CIR(nf) = cir;
end

% target unrelared
% meanRCS = 0.005;
% stdRCS = 0.001;
meanRCS = 0.0005;
stdRCS = 0.0001;
numScatterers = 10;
RCSs = meanRCS + stdRCS * randn(numScatterers, 1);
cuboidDimensions = [2, 2, 2]; % 2m x 2m x 2m cuboid
scattererLocations = -cuboidDimensions / 2 + cuboidDimensions .* rand(numScatterers, 3);
% transmitterLocation = [0, -0.1, -1.5];
% receiverLocation = [0.2, -0.1, 0.1];
% narrowband target unrelared channel
CIR_static = 0;
for ii = 1:1:size(scattererLocations,1)
    R_Tx = norm(scattererLocations(ii,:)-Tx_pos);
    R_Rx = norm(scattererLocations(ii,:)-Rx_pos);
    Amp = sqrt(RCSs(ii))/R_Rx/R_Tx;
    Phase = exp(-1i*2*pi*(R_Tx+R_Rx)/lambda);
    CIR_static = CIR_static + Amp*Phase;
end
CIR = CIR + (AWGN_mean + AWGN_var*rand(size(CIR)));
% CIR = CIR + (AWGN_mean + AWGN_var*rand(size(CIR)))+CIR_static;
% CIR = CIR +CIR_static;
%% micro-Doppler signature
% 1/fs*v < c/fc; fs>fc/c*v
F = fs;
% thres_A_TRD = -60;
% figure;% figure('Position',[500 200 900 600])
% colormap(jet)
% spectrogram(CIR,kaiser(256,15),250,512,F,'centered','yaxis');
% clim = get(gca,'CLim');
% ylim([-0.6 0.6]);
% set(gca,'CLim',clim(2) + [thres_A_TRD 0]);
% % set(gca,'CLim',clim(2) + [-60 0]);
% title('Micro-Doppler Signature', 'Fontsize',12,'color','k')
% % tightfig;
% drawnow

%% Normalize
% figure;
F = fs;

[s,f,t] = spectrogram([CIR,zeros(1,85)],kaiser(198,15),160,198,F,'centered','yaxis');
% 
spectrogram([CIR,zeros(1,85)],kaiser(198,15),160,198,F,'centered','yaxis');
% [r,c]=size(s);
% 
% for i=1: c
% s(:,i)=abs(s(:,i)/max(abs(s(:,i))));
% end
% % 调整频谱图大小为191x201
% s = imresize(s, [100, 191],"bicubic"); % 调整大小为 191x201
% s = s/max(abs(s),[],'all');
% s = abs(s);





% 将频谱图调整为 191x201
% spectrogram_data = mag2db(abs(s));
% time_vector = t;
% freq_vector = f;


%%%%%%原始归一化
% s=norm_energy(s);

%%%%%%%


spectrogram_data = s;
time_vector = t;
freq_vector = f;
% s = mag2db(abs(s));
% h = imagesc(t, f, s);
% xlabel('Time (s)')
% ylabel('Doppler frequency (Hz)')
% if fs >= 1000
% ylim([-800 800]);
% end
% axis xy; % 设置坐标轴方向，使频率轴朝上
% colormap jet;
% colorbar;

% caxis([thres_A_TRD,0]);

% tightfig;

%% Remove lim
% fig = figure;
% ax = axes;
% new_handle = copyobj(h,ax);
% if fs >= 1000
% ylim([-800 800]);
% end
% xlim([t(1) t(end)]);
% colormap jet;
% caxis([thres_A_TRD,0]);
% axis off
% set(gca,'xtick',[],'ytick',[],'xcolor','w','ycolor','w')
% set(gca,'looseInset',[0 0 0 0]);
% if pic_save == true
%     saveas(gcf,output_jpg_path)
% end
end
function [azimuth,elevation,r] = my_cart2sph(x,y,z)
% matlab自带的坐标转化有问题
% https://www.mathworks.com/help/releases/R2022b/matlab/ref/cart2sph.html
% matlab计算的elevation角以x轴为基准，正负pi/2, 如下
% azimuth = atan2(y,x)
% elevation = atan2(z,sqrt(x.^2 + y.^2))
% r = sqrt(x.^2 + y.^2 + z.^2)
% https://zhuanlan.zhihu.com/p/34485962
  r = sqrt(x^2 + y^2 + z^2);
  elevation = acos(z/r);
  azimuth = atan2(x,y);
end
function rcs = brcsellipsoid_circle(len,radius,bistatic_angle_phi,theta_i,theta_s)
% bistatic rcs for an ellipsoid with circular section.
a = radius;
b = radius;
c = len;
rcs = (4*pi*a^2*b^2*c^2)*((1+cos(theta_i)*cos(theta_s))*cos(bistatic_angle_phi)+sin(theta_i)*sin(theta_s))^2/ ...
    (a^2*(sin(theta_i)^2+sin(theta_s)^2+2*sin(theta_i)*sin(theta_s)*cos(bistatic_angle_phi))+...
    c^2*(cos(theta_i)+cos(theta_s))^2 ...
    )^2;
end
function rcs = rcsellipsoid(a,b,c,phi_i,theta_i,phi_s,theta_s)
% Modified from "Chen, Victor C. The micro-Doppler effect in radar. Artech house, 2019."
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This program calculates the bistatic (or monostatic) RCS of an ellipsoid
% with semi-axis lengths of a, b, and c.
% phi_i, theta_i: the aspect and azimuth angles of incident waves.
% phi_s, theta_s: the aspect and azimuth angles of scattered waves.
% Seeing details for ellipsoid rcs settings, please refer to 
% https://rzy0901.github.io/post/rcs/#bistatic-rcs-estimation-of-an-ellipsoid5-6
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if nargin ~=5 && nargin ~= 7
    nargin
    error("Please use correct input parameters.")
end
if nargin == 5 % monostatic rcs
    rcs = (pi*a^2*b^2*c^2)/(a^2*(sin(theta_i))^2*(cos(phi_i))^2+b^2*(sin(theta_i))^2*(sin(phi_i))^2+c^2*(cos(theta_i))^2)^2;
end
if nargin == 7 % bistatic rcs
    rcs = (4*pi*a^2*b^2*c^2)*((1+cos(theta_i)*cos(theta_s))*cos(phi_s-phi_i)+sin(theta_i)*sin(theta_s))^2/ ...
        (a^2*(sin(theta_i)*cos(phi_i)+sin(theta_s)*cos(phi_s))^2+ ...
        b^2*(sin(theta_i)*sin(phi_i)+sin(theta_s)*sin(phi_s))^2+ ...
        c^2*(cos(theta_i)+cos(theta_s))^2 ...
        )^2;
end
end



function rotate_position = rotate_angle(position1,position2,angle)%%仅仅给出二维平面上旋转的方法，可能需要额外参数，x1,y1旋转 x2,y2不动
x1=position1(1);    
y1=position1(3);
x2=position2(1);
y2=position2(3);
rotate_position(1)=(x1-x2)*cos(angle)-(y1-y2)*sin(angle)+x2;
rotate_position(2)=position1(2);
rotate_position(3)=(x1-x2)*sin(angle)-(y1-y2)*cos(angle)+y2;

%%仅仅在xoz平面上做投影，然后旋转
%%深度相机y是海拔面积

end

function keypoints = rotate_keypoints(keypoints, theta1)
    % 获取旋转中心（第一帧第二特征点）
    center = squeeze(keypoints(1,2,:))';
    
    % 提取x,z坐标
    X = keypoints(:,:,1);
    Z = keypoints(:,:,3);
    
    % 计算相对坐标
    X_rel = X - center(1);
    Z_rel = Z - center(3);
    
    % 向量化旋转
    costheta = cos(theta1);
    sintheta = sin(theta1);
    
    % 更新关键点
    keypoints(:,:,1) = X_rel * costheta - Z_rel * sintheta + center(1);
    keypoints(:,:,3) = X_rel * sintheta + Z_rel * costheta + center(3);
end


function [S_pca_db, pcaInfo] = pca_denoise_spectrogram(S_db, K_pca, noiseFloorDb)
    % S_db: 频率 × 时间 的 dB 谱图
    % K_pca: 保留的 PCA 主成分数量
    % noiseFloorDb: 噪声底，例如 -45 dB

    S_db(~isfinite(S_db)) = noiseFloorDb;
    S_db = max(S_db, noiseFloorDb);
    S_db = min(S_db, 0);

    % 归一化到 [0, 1]
    S_norm = (S_db - noiseFloorDb) / (0 - noiseFloorDb);
    S_norm = max(min(S_norm, 1), 0);

    % 这里把每一个时间帧看成一个样本，
    % 每一个 Doppler bin 看成一个特征。
    % X 的大小是：时间 × 频率
    X = S_norm.';

    % 每个频率 bin 去均值
    mu = mean(X, 1);
    X0 = X - mu;

    % SVD 等价于 PCA
    [U, Sigma, V] = svd(X0, 'econ');

    K_pca = min(K_pca, size(Sigma, 1));

    % 只保留前 K 个主成分重构
    X_rec = U(:, 1:K_pca) * Sigma(1:K_pca, 1:K_pca) * V(:, 1:K_pca).' + mu;

    X_rec = max(min(X_rec, 1), 0);

    % 转回 频率 × 时间
    S_rec = X_rec.';

    % 转回 dB
    S_pca_db = S_rec * (0 - noiseFloorDb) + noiseFloorDb;

    % 输出 PCA 信息
    eigVal = diag(Sigma).^2;
    pcaInfo.explainedRatio = eigVal / (sum(eigVal) + eps) * 100;
    pcaInfo.cumExplainedRatio = cumsum(pcaInfo.explainedRatio);
    pcaInfo.freqModes = V(:, 1:K_pca);
    pcaInfo.timeScores = U(:, 1:K_pca) * Sigma(1:K_pca, 1:K_pca);
end

function AF_factor = af_factor(theta1,phi1,theta2,phi2)  %%%%%如果不对自己改这部分天线设置参数

fc = 60.48e9;
c = 3e8;
lambda = c/fc;
d = 0.0013;

N = 16;   % 增大发射阵列（更尖锐主瓣）
steering = @(N, theta,phi) exp(1j*2*pi*d/lambda*(0:N-1)'*sind(theta)*cosd(phi));
true = steering(N,90, 0);

 w_tx = steering(N, 90-theta1,phi1);
 w_rx = steering(N, 90-theta2,phi2);
gain=(w_rx' * true) * (true' * w_tx);
gain=abs(gain);
standardgain=abs(true'*true);
AF_factor=gain/standardgain;

end