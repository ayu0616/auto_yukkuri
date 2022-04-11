import os
from get_project_dir import get_project_dir
from my_helper import MyList
import re
from pprint import pprint


def get_script_list(project_dir: str):
    # 改行を基準に台本を配列に分ける
    with open(project_dir+"/script.txt", "r") as f:
        script = f.read()
    script_list = MyList(script.split("\n"))
    # print(script_list)
    # セリフ部分を取り出す
    script_list = script_list.match_filter(r"^[れま]：.*")
    # コメントを削除する（コメントは"// "で始まるもの）
    script_list = script_list.map(lambda x: re.sub(r"\s*//.*", "", x))
    return script_list


if __name__ == "__main__":
    current_dir = os.path.abspath(os.getcwd())
    project_dir = get_project_dir(current_dir)
    script_list = get_script_list(project_dir)
    pprint(script_list)
