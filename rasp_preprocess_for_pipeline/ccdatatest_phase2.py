import h5py

# 既存のHDF5ファイル名
input_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\ff.h5"
# 新しいHDF5ファイル名
output_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\ff.h5"
import h5py
import numpy as np
import pandas as pd
                
import shutil

###   現状ではconfigに相当する
# HDF5ファイル名

input_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\ff.h5"
# CSVファイルのパス
csv_path ="Z:\D2behavior\prj5-5\\3CSRTT-phase1\\raw_raspberypi_nb07\\results_TO36_day04-phase2S01_240609-225158.csv"
# HDF5ファイルのパス
hdf5_path = input_filename
# データセット名のリスト
datasets = ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']

# 更新するtrial_numのリスト
trial_nums =  [i for i in range(60)]  # 例として
# 各trialの開始時間を記録しているリスト
#start_time_list =[1717755452.937, 1717755475.023, 1717755496.072, 1717755515.129, 1717755531.19, 1717755555.267, 1717755571.313, 1717755591.368, 1717755612.428, 1717755630.471, 1717755649.533, 1717755664.592, 1717755681.634, 1717755696.687, 1717755720.748, 1717755736.794, 1717755753.838, 1717755771.88, 1717755787.928, 1717755807.972, 1717755832.033, 1717755855.087, 1717755875.127, 1717755898.189, 1717755915.231, 1717755930.271, 1717755949.309, 1717755966.348, 1717755989.39, 1717756008.428, 1717756024.46, 1717756040.493, 1717756062.547, 1717756085.603, 1717756100.634, 1717756123.677, 1717756144.717, 1717756161.756, 1717756183.802, 1717756198.833, 1717756220.872, 1717756242.923, 1717756266.971, 1717756286.01, 1717756308.057, 1717756328.127, 1717756345.164, 1717756363.212, 1717756383.254, 1717756401.29, 1717756424.337, 1717756445.374, 1717756461.409, 1717756482.462, 1717756501.494, 1717756519.53, 1717756534.562, 1717756558.607, 1717756577.657, 1717756592.694, 1717756615.735, 1717756636.777, 1717756651.81, 1717756669.854, 1717756687.907, 1717756708.948, 1717756728.992, 1717756753.032, 1717756774.075, 1717756789.103, 1717756805.157, 1717756828.218, 1717756845.266, 1717756869.319, 1717756893.368, 1717756913.412, 1717756935.47, 1717756955.511, 1717756971.552, 1717756989.594, 1717757006.627, 1717757022.667, 1717757039.705, 1717757061.747, 1717757081.786, 1717757105.834, 1717757127.879, 1717757142.918, 1717757162.956, 1717757180.991, 1717757200.032, 1717757223.075, 1717757241.13, 1717757262.173, 1717757279.21, 1717757298.247, 1717757319.286, 1717757342.33, 1717757366.369, 1717757388.402]
start_time_list=[]
print(len(start_time_list))
# CSVデータを読み込む
if len(start_time_list)==0:
    df = pd.read_csv(csv_path, delimiter=',')
    # actionが'trial_start'の行をフィルタリング
    trial_start_df = df[df['action'] == 'trial_start']
    # time列のみを取得してリストに変換
    start_time_list = trial_start_df['time'].tolist()
    
    
if len(start_time_list) < len(trial_nums):
    raise ValueError("start timeが一部欠損しています。start_time_listの長さ: {}, trial_numsの長さ: {}".format(len(start_time_list), len(trial_nums)))
elif len(start_time_list) == len(trial_nums):
    print("start time list とtrialの数が一致しています。start_time_listの長さ: {}, trial_numsの長さ: {}".format(len(start_time_list), len(trial_nums)))
if len(start_time_list) > len(trial_nums):
    print("start time余剰。start_time_listの長さ: {}, trial_numsの長さ: {}".format(len(start_time_list), len(trial_nums)))


# HDF5ファイルを読み書きモードで開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        # 3桁にフォーマット
        formatted_trial_num = f"{trial_num:03d}"
        # trial_start データセットのパス
        start_time_path = f"trial_data/{formatted_trial_num}/trial_start"
        #print(start_time_path)
        # 開始時間をデータセットに書き込む
        if start_time_path in file:
            # データセットが存在する場合、値を更新
            file[start_time_path][()] = start_time_list[i]
        else:
            # データセットが存在しない場合、新規に作成
            file.create_dataset(start_time_path, data=np.array([start_time_list[i]]))

print("各trialの開始時間の更新が完了しました")
i=0

# CSVデータを読み込む
df = pd.read_csv(csv_path, delimiter=',')

# HDF5ファイルを開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for trial_num in df['trial_num'].unique():
        # trial_startの時刻を取得
        #print(i)
        
        if trial_num > max(trial_nums):
            break
        print(trial_num)
        
        trial_start = file[f"trial_data/{trial_num:03d}/trial_start"][()]
        
        # actionごとのデータを処理
        for action in ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']:
            # 対応するactionの行をフィルタリング
            action_df = df[(df['trial_num'] == trial_num) & (df['action'] == action)]
            # データセットのパス
            data_path = f"trial_data/{trial_num:03d}/{action}"
            downsample_path = f"param_dev/dev1_ai_task/{action}/downsample_in_hz"
            downsample_in_hz = file[downsample_path][()]
            if data_path in file:
                # データセットの現在のデータを取得
                data_array = file[data_path][()]
                # 各時刻について処理
                for _, row in action_df.iterrows():
                    time_index = int((row['time'] - trial_start) * downsample_in_hz)  # 20 Hzに基づいてインデックスを計算
                    print(time_index)
                    
                    print(len(data_array))
                    #if 0 <= time_index < len(data_array):
                    data_array[time_index] = 1  # 値を1に更新
                    print(data_array)
                # 更新されたデータでデータセットを上書き
                file[data_path][...] = data_array
                



"""
# HDF5ファイルを開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for trial_num in df['trial_num'].unique():
        # trial_startの時刻を取得
        if trial_num > max(trial_nums):
            continue
        print(trial_num)
        
        trial_start = file[f"trial_data/{trial_num:03d}/trial_start"][()]

        # actionごとのデータを処理
        for action in ['OP_NP1_correct', 'OP_NP2_correct', 'OP_NP3_correct']:
            # 対応するactionの行をフィルタリング
            action_df = df[(df['trial_num'] == trial_num) & (df['action'] == action)]
            # データセットのパス
            data_path = f"trial_data/{trial_num:03d}/operant_events/{action}/responses"
            # データセットが存在しなければ作成
            if data_path not in file:
                file.create_dataset(data_path, data=np.zeros(1000, dtype=int))  # 仮に1000と設定

            # データセットの現在のデータを取得
            data_array = file[data_path][()]

            # 各時刻について処理
            for _, row in action_df.iterrows():
                time_index = int((row['time'] - trial_start) * 2)  # 20 Hzに基づいてインデックスを計算
                if 0 <= time_index < len(data_array):
                    data_array[time_index] = 1  # 値を1に更新
                print(data_array)
            # 更新されたデータでデータセットを上書き
            file[data_path][...] = data_array
"""
operant_downsample_in_hz = 10#pipeline解析の都合で10固定
# HDF5ファイルを開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for trial_num in df['trial_num'].unique():
        # trial_startの時刻を取得
        if trial_num > max(trial_nums):
            continue
        print(trial_num)
        
        trial_start = file[f"trial_data/{trial_num:03d}/trial_start"][()]
        
        # actionごとのデータを処理
        for action in ['OP_NP1_correct', 'OP_NP2_correct', 'OP_NP3_correct']:
            # 対応するactionの行をフィルタリング
            action_df = df[(df['trial_num'] == trial_num) & (df['action'] == action)]
            # データセットのパス
            response_path = f"trial_data/{trial_num:03d}/operant_events/{action}/responses"
            success_path = f"trial_data/{trial_num:03d}/operant_events/{action}/success"

            # データセットが存在しなければ作成
            if response_path not in file:
                file.create_dataset(response_path, data=np.zeros(1000, dtype=int))  # 仮に1000と設定
            
            data_array = file[response_path][()]
            success_indices = []

            # 各時刻について処理
            for _, row in action_df.iterrows():
                time_index = int((row['time'] - trial_start) * operant_downsample_in_hz)  # 20 Hzに基づいてインデックスを計算
                if 0 <= time_index < len(data_array):
                    data_array[time_index] = 1  # 値を1に更新
                    success_indices.append(time_index * (1000 / operant_downsample_in_hz))  # 例としてdownsample_in_hz=2

            # 更新されたデータでデータセットを上書き
            file[response_path][...] = data_array

            # successデータセットを作成または更新
            if success_path in file:
                del file[success_path]  # 既存データセットがあれば削除
            file.create_dataset(success_path, data=np.array(success_indices, dtype=int))

print("データの更新が完了しました")
print("データの更新が完了しました")


# 入力ファイルを変更した後に、そのファイルを出力ファイルパスにコピー
shutil.copy(input_filename, output_filename)
