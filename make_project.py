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
past_projects = my_glob(current_abs_dir+"/[0-9][0-9][0-9]-*/")
past_projects = past_projects.map(lambda x: x.replace(current_abs_dir, "").replace("/", ""))
sorted_projects = sorted(past_projects)
last_num = int(sorted_projects[-1][:3])

# 今回の番号
new_num = last_num + 1
new_index = create_index(new_num, 3)

# 新規プロジェクトのディレクトリを作成する
new_dir_name = f"{current_abs_dir}/{new_index}-{new_project_name}"
os.mkdir(new_dir_name)

# 台本ファイルを作成する
script_path = f"{get_yukkuri_dir(__file__)}/台本/{new_index}-{new_project_name}.txt"
with open(script_path, "w") as f:
    f.write("")

script_symbolic_path = new_dir_name+"/script.txt"
subprocess.run(f"ln -s {script_path} {os.path.dirname(script_symbolic_path)}", shell=True)
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
