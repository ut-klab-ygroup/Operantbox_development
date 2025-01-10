import h5py
import numpy as np
import pandas as pd
import shutil
import os

# CSVファイルのパス
csv_path ="Z:\D2behavior\prj5-5\\3CSRTT-phase1\\raw_raspberypi_nb07\\results_TO46_day03-phase1S02_240709-230053.csv"
cond = "random-iti"
phase = "phase1"
analyzed_directory = "Z:\D2behavior\prj5-5\\3CSRTT-phase1\\cond_rasp-exp\\"  # 保存したいディレクトリに変更してください


if cond == "random-iti" and phase == "phase1":
    # テンプレートファイル名
    template_filename = "Z:\\D2behavior\prj5-5\\3CSRTT-phase1\cc_template\\daytime_prj-00_3CSRTT_cond-random-iti-50_mouse-name_day00-phase1-session00___cc_data.h5"

# テンプレートファイル名の解析
template_basename = os.path.basename(template_filename)
template_parts = template_basename.split('_')
prj_name = template_parts[1]  # 例: prj ->　本来はresultsからとってくるか。
experiment_name = template_parts[2]  # 例: 3CSRTT
condition = template_parts[3]  # 例: cond-random-iti-50
#print(template_parts)

# CSVファイルの名前から出力ファイル名を生成
csv_filename = os.path.basename(csv_path)
csv_parts = csv_filename.split('_')
mouse_name = csv_parts[1]
day_phase = csv_parts[2]
timestamp = csv_parts[3].replace(".csv", "")

output_directory = os.path.join(analyzed_directory, f"{mouse_name}\\{day_phase}_")
output_filename = f"{timestamp}_{prj_name}_{experiment_name}_{condition}_{mouse_name}_{day_phase}___cc_data.h5"
output_filepath = os.path.join(output_directory, output_filename)

# ディレクトリが存在しない場合は作成
os.makedirs(output_directory, exist_ok=True)

# テンプレートファイルをコピーして新しいHDF5ファイルを作成
shutil.copy(template_filename, output_filepath)

# HDF5ファイルのパス
hdf5_path = output_filepath

# データセット名のリスト
datasets = ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']

# 更新するtrial_numのリスト
trial_nums = [i for i in range(100)]  # 例として
# 各trialの開始時間を記録しているリスト
start_time_list = []  # 未定義の場合は、下でcsvから読み込む

# CSVデータを読み込む
if len(start_time_list) == 0:
    df = pd.read_csv(csv_path, delimiter=',')
    # actionが'trial_start'の行をフィルタリング
    trial_start_df = df[df['action'] == 'trial_start']
    # time列のみを取得してリストに変換
    start_time_list = trial_start_df['time'].tolist()

if len(start_time_list) < len(trial_nums):
    raise ValueError("データの長さが足りません。start_time_listの長さ: {}, trial_numsの長さ: {}".format(len(start_time_list), len(trial_nums)))

# HDF5ファイルを読み書きモードで開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        # 3桁にフォーマット
        formatted_trial_num = f"{trial_num:03d}"
        # trial_start データセットのパス
        start_time_path = f"trial_data/{formatted_trial_num}/trial_start"
        # 開始時間をデータセットに書き込む
        if start_time_path in file:
            # データセットが存在する場合、値を更新
            file[start_time_path][()] = start_time_list[i]
        else:
            # データセットが存在しない場合、新規に作成
            file.create_dataset(start_time_path, data=np.array([start_time_list[i]]))

print("各trialの開始時間の更新が完了しました")

# CSVデータを再度読み込む
df = pd.read_csv(csv_path, delimiter=',')

# HDF5ファイルを開く
with h5py.File(hdf5_path, 'r+') as file:
    # 各trial_numに対して処理
    for trial_num in df['trial_num'].unique():
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
            if data_path in file:
                # データセットの現在のデータを取得
                data_array = file[data_path][()]
                # 各時刻について処理
                for _, row in action_df.iterrows():
                    time_index = int((row['time'] - trial_start) * 10)  # 20 Hzに基づいてインデックスを計算
                    if 0 <= time_index < len(data_array):
                        data_array[time_index] = 1  # 値を1に更新
                # 更新されたデータでデータセットを上書き
                file[data_path][...] = data_array

print("データの更新が完了しました")
