import os

# ディレクトリのパスを指定してください
directory = "Z:\\D2behavior\prj5-5\\3CSRTT-phase1"  # 実際のディレクトリパスに置き換えてください

# フォルダー名を再帰的に探索し、条件に基づいて名前を変更する関数
def rename_folders(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            # フォルダー名に '2S02', '2S03', '2S04' が含まれているか確認
            if any(substring in dir_name for substring in ['2S02', '2S03', '2S04']):
                new_dir_name = f"_{dir_name}"
                old_path = os.path.join(root, dir_name)
                new_path = os.path.join(root, new_dir_name)
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} to {new_path}")

# 関数を呼び出してフォルダー名を変更
rename_folders(directory)
