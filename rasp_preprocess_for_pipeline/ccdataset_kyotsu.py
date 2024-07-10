import h5py
import numpy as np
import pandas as pd
import shutil
import os

# CSVファイルのパス
csv_folder = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\raw_raspberypi_nb07\\new_files\\"
analyzed_directory = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cond_rasp-exp\\"  # 保存したいディレクトリに変更してください

# 更新するdownsample_in_hzの値
downsample_in_hz = 20  # 検出アルゴリズム依存, initializedと共通である必要




# CSVフォルダ内のすべてのCSVファイルに対して処理を実行
for csv_filename in os.listdir(csv_folder):
    if csv_filename.endswith(".csv"):
        csv_path = os.path.join(csv_folder, csv_filename)
        
        # CSVファイルの名前から出力ファイル名とディレクトリを生成
        csv_parts = csv_filename.split('_')
        mouse_name = csv_parts[1]
        day_phase = csv_parts[3] # 例: day00-phase2-session00
        timestamp = csv_parts[4].replace(".csv", "") 
        phasesession = day_phase.split('-')[1]  # 例: phase2
        cond_iti = f"{csv_parts[2].split('-')[0]}-{csv_parts[2].split('-')[1]}"
        print(cond_iti)
        print(phasesession)
        
        if cond_iti == "random-iti":
            if "phase1" in phasesession:
                # テンプレートファイル名
                template_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\daytime_prj-00_3CSRTT_cond-random-iti_mouse-name_day00-phase1-session00___cc_data.h5"
            elif "phase2" in phasesession:
                # テンプレートファイル名
                template_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\daytime_prj-00_3CSRTT_cond-random-iti_mouse-name_day00-phase2-session00___cc_data.h5"
        elif cond_iti == "fixed_iti":
            if "phase1" in phasesession:
                template_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\daytime_prj-00_3CSRTT_cond-fixed-iti_mouse-name_day00-phase1-session00___cc_data.h5"
            elif "phase2" in phasesession:
                # テンプレートファイル名
                template_filename = "Z:\\D2behavior\\prj5-5\\3CSRTT-phase1\\cc_template\\daytime_prj-00_3CSRTT_cond-fixed-iti_mouse-name_day00-phase2-session00___cc_data.h5"
        
        # テンプレートファイル名の解析
        template_basename = os.path.basename(template_filename)
        template_parts = template_basename.split('_')
        prj_name = template_parts[1]  # 例: prj -> 本来はresultsからとってくるか。
        experiment_name = template_parts[2]  # 例: 3CSRTT
        condition = template_parts[3]  # 例: cond-random-iti-50        
                        
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
        
        if "phase1" in phasesession:
            # 更新するtrial_numのリスト
            trial_nums = [i for i in range(100)]  # 例として
        elif "phase2" in phasesession:
            trial_nums = [i for i in range(60)]  # 例として

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
        
        print(f"{csv_filename} の各trialの開始時間の更新が完了しました")
        
        # CSVデータを再度読み込む
        df = pd.read_csv(csv_path, delimiter=',')
        
        # HDF5ファイルを開く
        with h5py.File(hdf5_path, 'r+') as file:
            # 各trial_numに対して処理
            for trial_num in df['trial_num'].unique():
                if trial_num > max(trial_nums):
                    break
                #print(trial_num)
                
                trial_start = file[f"trial_data/{trial_num:03d}/trial_start"][()]
                
                # actionごとのデータを処理
                for action in ['Lick', 'NP0', 'NP1', 'NP2', 'NP3', 'NP4']:
                    # 対応するactionの行をフィルタリング
                    action_df = df[(df['trial_num'] == trial_num) & (df['action'] == action)]
                    # データセットのパス
                    data_path = f"trial_data/{trial_num:03d}/{action}"
                    if "phase2" in phasesession:
                        downsample_path = f"param_dev/dev1_ai_task/{action}/downsample_in_hz"
                        downsample_in_hz = file[downsample_path][()]
                        print(downsample_in_hz)
                    if data_path in file:
                        # データセットの現在のデータを取得
                        data_array = file[data_path][()]
                        # 各時刻について処理
                        for _, row in action_df.iterrows():
                            time_index = int((row['time'] - trial_start) * downsample_in_hz)  # 20 Hzに基づいてインデックスを計算
                            #if "phase2" in phasesession:
                            #    print(time_index)
                            #初期のデータはtrialがひとつずれていたので、負になってしまう。これを防ぐためにデモのときのみ120をくわえる。    time_index =+120
                            #    print(len(data_array))
                                #time_index = time_index +120
                                #print(time_index)
                            if 0 <= time_index < len(data_array):
                                data_array[time_index] = 1  # 値を1に更新
                        # 更新されたデータでデータセットを上書き
                        file[data_path][...] = data_array
        
        print(f"{csv_filename} のデータの更新が完了しました")
        if "phase2" in phasesession:
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
