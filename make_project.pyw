import os
from my_helper import require_input, my_glob
from helper import create_index, get_yukkuri_dir
import subprocess

# 現在のディレクトリの絶対パスを取得
current_abs_path = os.path.abspath(__file__)
current_abs_dir = os.path.dirname(current_abs_path)
# print(current_abs_dir)

# 新規プロジェクト名
new_project_name = require_input("新規プロジェクト名")
# プロジェクト名が入力されていなければ終了
if not new_project_name:
    raise Exception("新規プロジェクト名を入力してください")

# 最新回の番号を取得
yukkuri_dir = get_yukkuri_dir(current_abs_dir)
past_projects = my_glob(yukkuri_dir+"/[0-9][0-9][0-9]-*")
past_project_names = past_projects.map(lambda x: x.split("/")[-1])
past_project_names.sort()
last_num = int(past_project_names[-1][:3])

# 今回の番号
new_num = last_num + 1
new_index = create_index(new_num, 3)

# 新規プロジェクトのディレクトリを作成する
new_dir_name = f"{yukkuri_dir}/{new_index}-{new_project_name}"
os.mkdir(new_dir_name)

# 台本ファイルを作成する
script_path = f"/Users/OgawaAyumu/Library/Mobile Documents/com~apple~CloudDocs/yukkuri_scripts/{new_index}-{new_project_name}.txt"
with open(script_path, "w") as f:
    f.write("")

subprocess.run(f"ln -s '{script_path}' '{new_dir_name}'", shell=True)
script_symbolic_path = new_dir_name+"/script.txt"
os.rename(f"{new_dir_name}/{new_index}-{new_project_name}.txt", script_symbolic_path)

# 音声を入れるディレクトリを作成する
voice_dir_name = new_dir_name + "/voices"
os.mkdir(voice_dir_name)
# os.mkdir(voice_dir_name+"/mp3")
os.mkdir(voice_dir_name+"/wav")
# その他ディレクトリを作成する
for dir_name in ["サムネ", "画像素材"]:
    dir_full_name = new_dir_name + "/" + dir_name
    os.mkdir(dir_full_name)
