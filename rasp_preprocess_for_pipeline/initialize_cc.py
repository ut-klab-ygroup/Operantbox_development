import h5py
import numpy as np

# HDF5ファイル名
#input_filename = 
#  　古いデータでおこなうと　itiがことなるためエラーが出る。
input_filename ="Z:\D2behavior\prj5-5\\3CSRTT-phase1\\cc_template\daytime_prj-00_3CSRTT_cond-random-iti-50_mouse-name_day00-phase1-session00___cc_data.h5"
# 更新するtrial_numのリスト
trial_nums = [i for i in range(100)]  # 例として

# wait_time_in_sとvariable_interval_in_sを定義（これらは適宜変更してください）
wait_time_in_s = 14
variable_interval_in_s = [8,7,5,2,10,2,6,7,4,5,1,3,1,10,2,3,4,2,6,10,9,6,9,3,1,5,3,9,5,2,2,8,9,1,9,7,3,8,1,8,8,10,5,8,6,3,4,6,4,9,7,2,7,5,4,1,10,5,1,9,7,1,4,4,7,6,10,7,1,2,9,3,10,10,6,8,6,2,4,3,2,3,8,6,10,8,1,6,4,5,9,4,7,3,5,7,9,10,8,5]
# このリストの長さはtrial_numsと一致する必要がある

# データセット名のリスト
datasets = ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']

# データセット名のリスト
datasets = ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']



# 更新するdownsample_in_hzの値
new_downsample_in_hz = 20 #検出アルゴリズム依存

# HDF5ファイルを読み書きモードで開く
with h5py.File(input_filename, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        formatted_trial_num = f"{trial_num:03d}"
        for dataset in datasets:
            downsample_path = f"param_dev/dev1_ai_task/{dataset}/downsample_in_hz"
            if downsample_path in file:
                file[downsample_path][()] = new_downsample_in_hz
                num_zeros = int((wait_time_in_s + max(variable_interval_in_s)) * new_downsample_in_hz)
                zeros_data = np.zeros(num_zeros, dtype=np.int32)
                data_path = f"trial_data/{formatted_trial_num}/{dataset}"
                if data_path in file:
                    # データセットを削除
                    del file[data_path]
                # チャンク化されたデータセットを新規作成
                dset = file.create_dataset(data_path, data=zeros_data, chunks=(num_zeros,), maxshape=(None,))
            else:
                print(f"downsample_in_hz not found for {dataset}")

print("データ更新完了")

"""
# HDF5ファイルを読み書きモードで開く
with h5py.File(input_filename, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        # 3桁にフォーマット
        formatted_trial_num = f"{trial_num:03d}"
        # 各データセットにデータを書き込む
        for dataset in datasets:
            # downsample_in_hzの値を取得
            downsample_path = f"param_dev/dev1_ai_task/{dataset}/downsample_in_hz"
            if downsample_path in file:
                downsample_in_hz = file[downsample_path][()]
                # 生成するデータの数を計算
                num_zeros = int((wait_time_in_s + max(variable_interval_in_s)) * downsample_in_hz)
                print(num_zeros)
                # ゼロで埋める配列を作成
                zeros_data = np.zeros(num_zeros, dtype=np.int)
                # データセットパス
                data_path = f"trial_data/{formatted_trial_num}/{dataset}"
                if data_path in file:
                    file[data_path][...] = zeros_data
                else:
                    print(f"Dataset not found: {data_path}")
            else:
                print(f"downsample_in_hz not found for {dataset}")

print("データ更新完了")

"""
