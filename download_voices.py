import os
import shutil
import requests
from get_project_dir import get_project_dir
from get_script_list import get_script_list
from yukkuri_translate import yukkuri_translate
from time import sleep
from helper import create_index


def check_list(script_list):
    invalid_i_list = []
    for i, sentence in enumerate(script_list):
        if sentence[1] != "：":
            invalid_i_list.append(str(i+1))
    if len(invalid_i_list) > 0:
        raise TypeError(f"{', '.join(invalid_i_list)}行目を修正してください")


def download_voices(script_list, project_dir: str):
    # 適切なファイルか確認する
    check_list(script_list)
    # 前回の音声ファイルを削除する
    path = project_dir + "/voices"
    shutil.rmtree(path)
    os.mkdir(path)

    # pathes = {
    #     # "mp3": project_dir + "/voices/mp3",
    #     "wav": project_dir + "/voices/wav"
    # }
    # for path in pathes.values():
    #     shutil.rmtree(path)
    #     os.mkdir(path)

    # 音声ファイルをダウンロードする（wav形式でダウンロードできることを発見）
    print("start downloading")
    for i, script in enumerate(script_list):
        character, sentence = script.split("：")
        translated_sentence = yukkuri_translate(sentence)
        character_dict = {
            "れ": "f1",
            "ま": "f2"
        }
        url = f"https://www.yukumo.net/api/v2/aqtk1/koe.wav?type={character_dict[character]}&effect=none&boyomi=true&speed=100&volume=100&kanji={translated_sentence}"
        res = requests.get(url)
        index = create_index(i+1, 3)
        # ファイル名から空白を削除する
        script = script.replace(' ', '')
        file_name = f"{index}_{sentence}.wav"
        print(f"downloading: {file_name}")
        with open(f"{path}/{file_name}", "wb")as f:
            f.write(res.content)
        # 過度なリクエストを防止するために待機する
        sleep(0.25)
    print("end downloading")

    # for i, script in enumerate(script_list):
    #     character, sentence = script.split("：")
    #     translated_sentence = yukkuri_translate(sentence)
    #     character_dict = {
    #         "れ": "f1",
    #         "ま": "f2"
    #     }
    #     url = f"https://www.yukumo.net/api/v2/aqtk1/koe.mp3?type={character_dict[character]}&effect=none&boyomi=true&speed=100&volume=100&kanji={translated_sentence}"
    #     res = requests.get(url)
    #     index = create_index(i+1, 3)
    #     # ファイル名から空白を削除する
    #     script = script.replace(' ', '')
    #     file_name = f"{index}_{script}.mp3"
    #     print(f"downloading: {file_name}")
    #     with open(f"{pathes['mp3']}/{file_name}", "wb")as f:
    #         f.write(res.content)
    #     # 過度なリクエストを防止するために待機する
    #     sleep(0.5)


if __name__ == "__main__":
    project_dir = get_project_dir()
    script_list = get_script_list(project_dir)
    download_voices(script_list, project_dir)
