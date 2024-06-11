import h5py
import numpy as np

# HDF5ファイル名
#input_filename = "Z:\D2behavior\prj5-5\\3CSRTT-phase1\cond_rasp-exp\SAtest1\day01-phase1S01_\\20240122-101416_11-1_3CSRTT_MAP-task-noSDS-vstim_SU183_day01-phase1S01___cc_data.h5"
     #  　古いデータでおこなうと　itiがことなるためエラーが出る。
input_filename ="Z:\D2behavior\prj5-5\\3CSRTT-phase1\cond_rasp-exp\TO36\day04-phase2S01_\\template\\20240418-120720_11_3CSRTT_MAP-Sul-task-noSDS-vstim_SU222_day04-phase2S01___cc_data.h5"
# 更新するtrial_numのリスト
trial_nums = [i for i in range(60)]  # 例として

# wait_time_in_sとwait_time_listを定義（これらは適宜変更してください）
wait_time_in_s = 60
wait_time_list = [0]
# このリストの長さはtrial_numsと一致する必要がある

# データセット名のリスト
datasets = ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']





# 更新するdownsample_in_hzの値
new_downsample_in_hz = 2 #検出アルゴリズムに依存

# HDF5ファイルを読み書きモードで開く
with h5py.File(input_filename, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        formatted_trial_num = f"{trial_num:03d}"
        for dataset in datasets:
            downsample_path = f"param_dev/dev1_ai_task/{dataset}/downsample_in_hz"
            if downsample_path in file:
                file[downsample_path][()] = new_downsample_in_hz
                num_zeros = int((wait_time_in_s + max(wait_time_list)) * new_downsample_in_hz)
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


new_downsample_in_hz = 10#pipeline解析の都合で10固定
# HDF5ファイルを読み書きモードで開く
with h5py.File(input_filename, 'r+') as file:
    # 各trial_numに対して処理
    for i, trial_num in enumerate(trial_nums):
        formatted_trial_num = f"{trial_num:03d}"
        for action in ['OP_NP1_correct', 'OP_NP2_correct', 'OP_NP3_correct']:
            #downsample_path = f"param_dev/dev1_ai_task/{action}/downsample_in_hz"
            num_zeros = int(wait_time_in_s * new_downsample_in_hz)
            zeros_data = np.zeros(num_zeros, dtype=np.int32)
            # 新しいデータセットパス
            data_path = f"trial_data/{formatted_trial_num}/operant_events/{action}/responses"
            if data_path in file:
                # 既存のデータセットを削除
                del file[data_path]
            # 新しいデータセットを作成
            dset = file.create_dataset(data_path, data=zeros_data, chunks=(num_zeros,), maxshape=(None,))
        
print("Operant event data initialization completed.")

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
                num_zeros = int((wait_time_in_s + max(wait_time_list)) * downsample_in_hz)
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