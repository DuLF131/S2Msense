clear all;
clc;

% 定义要处理的文件夹列表
% action_folders = {'fall_du_0114', 'kick_du_0114', 'sit_du_0114', 'step_du_0114'};
% action_folders = {'fall_du_0114', 'fall_wen', 'fall_wu_0114', 'kick_du_0114', 'kick_wen', 'kick_wu_0114', 'sit_du_0114', 'sit_wen', 'sit_wu_0114', 'step_du_0114', 'step_wen', 'step_wu_0114'};

% action_folders = {'fall_du_0114', 'fall_wen', 'fall_wu_0114'};

action_folders = {'kick_du_0114', 'kick_wen', 'kick_wu_0114'};
base_folder ='E:\data\real\except_chen\'; % 当前文件夹路径

% 处理参数
ChannelNum = 4;
f_s = 1e6;
fs_TX = 1e6;
CIT = 0.1;
N_slide = 10;
T_slide = CIT / N_slide;
sample_per_CIT = CIT * f_s;
% max_dop = 800;
max_dop = 1000;
step_dop = 1 / CIT;
array_Doppler_frequency = -max_dop:step_dop:max_dop;

% 遍历每个动作文件夹
for action_idx = 1:length(action_folders)
    current_action = action_folders{action_idx};
    
    % 设置输入和输出文件夹路径
    folder_path = fullfile(base_folder,'', current_action);
    out_folder = fullfile(base_folder, ['0427pca\', current_action]);
    
    % 创建输出文件夹
    if ~exist(out_folder, 'dir')
        mkdir(out_folder);
    end
    
    % 获取当前动作文件夹下所有.dat文件
    files = dir(fullfile(folder_path, '*.dat'));
    
    % 如果没有找到文件，跳过该文件夹
    if isempty(files)
        fprintf('No .dat files found in folder: %s\n', folder_path);
        continue;
    end
    
    fprintf('Processing folder: %s, found %d files\n', current_action, length(files));

    % 遍历文件夹中的每个 .dat 文件
    for file_idx = 1:length(files)
        filename = files(file_idx).name;
        fullfilename = fullfile(folder_path, filename);
        disp(['Processing file: ', fullfilename]);

        %% 读取数据文件
        fid = fopen(fullfilename, 'rb');
        fseek(fid, 0, 'eof');
        fsize = ftell(fid);
        total_samplelen1 = fsize / 4;
        total_samplelen = total_samplelen1 / 8;
        total_duration = total_samplelen / f_s;
        fclose(fid);

        fid = fopen(fullfilename, 'rb');
        fseek(fid, 0, 'bof');
        [data, ~] = fread(fid, [2, 4 * total_samplelen], 'float32', 'l');
        data = data(1, :) + 1i * data(2, :);
        data = reshape(data, [total_samplelen, 4]);
        data = data.';
        fclose(fid);

        % 时间轴
        t_axis = 0:1 / f_s:(CIT * f_s - 1) / f_s;

        %%% 对齐数据
        S_ref = data(1, 1:CIT * f_s);
        S_tar = data(2, 1:CIT * f_s);
        h_temp = xcorr(S_ref, S_tar);
        [row_h, col_h] = size(h_temp);
       
        col_h = col_h + 1;
        N = floor(CIT*f_s)/1000-1;
        col_max = find(max(abs(h_temp(col_h/2-N:col_h/2+N))) == abs(h_temp(col_h/2-N:col_h/2+N)));
        array_sample_shift = col_max - N - 1;



        


        data_cor = zeros(4, size(data, 2) - abs(array_sample_shift));
        
        if array_sample_shift > 0
        data_cor(1,:) = data(1, 1+array_sample_shift:end);
        data_cor(2,:) = data(2, 1:end-array_sample_shift);
        data_cor(3,:) = data(3, 1+array_sample_shift:end);
        data_cor(4,:) = data(4, 1:end-array_sample_shift);
    else
        data_cor(1,:) = data(1, 1:end+array_sample_shift);
        data_cor(2,:) = data(2, 1-array_sample_shift:end);
        data_cor(3,:) = data(3, 1:end+array_sample_shift);
        data_cor(4,:) = data(4, 1-array_sample_shift:end);
        end


        %%%滑动数据
        array_start_time = 0:T_slide:total_duration-CIT;
        valid_frames = length(array_start_time) - 1;
        A_TD1 = zeros(valid_frames, length(array_Doppler_frequency));
A_TD2 = zeros(valid_frames, length(array_Doppler_frequency));

        %% Process
        num_sample = CIT * f_s;
        
        for idx_start_time = 1:length(array_start_time)-1
            % % temp_ref = data_cor(1, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
            % % temp_tar1 = data_cor(2, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
            % % temp_tar2 = data_cor(3, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
            % % 
            % % % 消除算法
            % % temp_tar1 = ClutterCancellation(temp_tar1, temp_ref, 1, 0, CIT, f_s);
            % % temp_tar2 = ClutterCancellation(temp_tar2, temp_ref, 1, 0, CIT, f_s);
            % % 
            % % temp_tar1 = temp_tar1';
            % % temp_tar2 = temp_tar2';

        temp_ref = data_cor(1, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
        temp_ref1 = data_cor(3, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
        temp_tar1 = data_cor(2, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));
        temp_tar2 = data_cor(4, (round(array_start_time(idx_start_time)*f_s+1)):(round(array_start_time(idx_start_time)*f_s)+round(CIT*f_s)));

         % % % 消除算法
            temp_tar1 = ClutterCancellation(temp_tar1, temp_ref, 1, 0, CIT, f_s);
            temp_tar2 = ClutterCancellation(temp_tar2, temp_ref1, 1, 0, CIT, f_s);
            temp_tar1 = temp_tar1';
            temp_tar2 = temp_tar2';

            % fft
            temp1 = fftshift(fft(temp_tar1 .* conj(temp_ref), num_sample));
            A_TD1(idx_start_time, :) = temp1(num_sample/2+1-max_dop/step_dop:num_sample/2+1+max_dop/step_dop);
            temp2 = fftshift(fft(temp_tar2 .* conj(temp_ref1), num_sample));
            A_TD2(idx_start_time, :) = temp2(num_sample/2+1-max_dop/step_dop:num_sample/2+1+max_dop/step_dop);
        end
    
       
        
        
        %%%%%%%%%%%%%%%
        s1 = A_TD1';
        s2 = A_TD2';

        s1=s1/max(abs(s1),[],'all');
        s1=mag2db(abs(s1));

        s2=s2/max(abs(s2),[],'all');
        s2=mag2db(abs(s2));
        bind_data = [s1,s2];
    bind_data = imresize(bind_data, [100, 190], "bicubic");
     bind_data((49:51),:)=-55;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% figure;
% imagesc(time_axis_spec, dop_axis, s1_pca);
% axis xy;
% colormap jet;
% caxis([-35 0]);
% xlabel('Time (s)');
% ylabel('Doppler Frequency (Hz)');
% title('A\_TD1 PCA Denoised Doppler Ridges');
% hold on;
% 
% for k = 1:nLines
%     plot(time_axis_spec, ridgeFreq1(k, :), 'w-', 'LineWidth', 1.5);
% end
% 
% hold off;
% figure;
% imagesc(time_axis_spec, dop_axis, s2_pca);
% axis xy;
% colormap jet;
% caxis([-35 0]);
% xlabel('Time (s)');
% ylabel('Doppler Frequency (Hz)');
% title('A\_TD2 PCA Denoised Doppler Ridges');
% hold on;
% 
% for k = 1:nLines
%     plot(time_axis_spec, ridgeFreq2(k, :), 'w-', 'LineWidth', 1.5);
% end
% 
% hold off;
    mat_output_folder = out_folder;  % 保存 .mat 文件的文件夹
    if ~exist(mat_output_folder, 'dir')
        mkdir(mat_output_folder);  % 如果文件夹不存在则创建
    end
    mat_output_filename = fullfile(mat_output_folder, [sprintf('%s', filename), '.mat']);  % 使用文件索引生成文件名
    parsave(mat_output_filename, bind_data,A_TD1,A_TD2);  % 保存矩阵和时间轴、多普勒轴
    
    disp(['Saved .mat file to: ', mat_output_filename]);

    % 创建纯净图片
    jpg_output_filename = fullfile(out_folder, [filename, '.jpg']);

   

 h=imagesc(bind_data);


caxis([-30,0]);
 % 
 colormap jet;
 axis off;
 set(gca,'xtick',[],'ytick',[],'xcolor','w','ycolor','w');
 set(gca,'looseInset',[0 0 0 0]);

    
    
    
saveas(gcf, jpg_output_filename, 'jpg');
    disp(['Saved image to: ', jpg_output_filename]);
    end
    % 
    fprintf('Finished processing folder: %s\n', current_action);
end

fprintf('All folders processed successfully!\n');


function parsave(fname, bind_data, A_TD1, A_TD2)
    % 使用 parfor 保存多个变量到 MAT 文件
    save(fname, 'bind_data', 'A_TD1', 'A_TD2');
end


