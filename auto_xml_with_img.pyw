import math
from typing import Any, Dict, List, TypedDict
from pydub import AudioSegment
# import subprocess
# from bs4 import BeautifulSoup
import os
from create_telop import create_all_telop
# from convert_to_wav import convert_to_wav
from download_voices import download_voices
from get_project_dir import get_project_dir
from get_script_list import get_script_list
from helper import create_index, get_yukkuri_dir
from my_helper import MyList, my_glob

# このpythonファイルがあるディレクトリ
current_abs_path = os.path.abspath(__file__)
current_abs_dir = os.path.dirname(current_abs_path)
auto_yukkuri_path = get_yukkuri_dir(__file__) + "/auto_yukkuri"

# 動画プロジェクトのディレクトリ
project_dir = get_project_dir(current_abs_dir)

# セリフ1つ1つを配列にしたもの
script_list = get_script_list(project_dir)

# テロップを作成する
create_all_telop(script_list, project_dir)

# ダウンロードする
download_voices(script_list, project_dir)

# voice_pathes = glob.glob(project_dir+"/voices/mp3/*")
voice_pathes = my_glob(project_dir+"/voices/*")
voice_pathes.sort()

# 音声ファイルをwavに変換する（wavでダウンロードできるので変換しなくて良くなった）
# voice_pathes = convert_to_wav(voice_pathes)

# 無音の音声ファイル
silent_path = auto_yukkuri_path + "/silent.wav"
silent_duration = 0.4
silent_audio = AudioSegment.silent(duration=silent_duration*1000, frame_rate=8000)
# AudioSegment.silent(duration=silent_duration*1000, frame_rate=8000).export(silent_path, format="wav")
# silent_sentence = f"file '{silent_path}'"

# voice_pathes_str = voice_pathes.map(lambda x: f"{silent_sentence}\nfile '{x}'\n{silent_sentence}")
# voice_pathes_str = voice_pathes_str.join("\n")
# voice_file_list_path = auto_yukkuri_path + "/voice_file_list.txt"
# with open(voice_file_list_path, "w") as f:
#     f.write(voice_pathes_str)

# # 結合する
# united_voice_path = project_dir + "/voices/united_voice.wav"
# subprocess.run(f"yes y | ffmpeg -f concat -safe 0 -i {voice_file_list_path} -c copy {united_voice_path}", shell=True, check=True)


# 無音を前後に追加（セリフごとにファイルは分割）
voice_files: MyList[AudioSegment] = voice_pathes.map(lambda x: silent_audio+AudioSegment.from_wav(x)+silent_audio)
for file, path in zip(voice_files, voice_pathes):
    file.export(path, "wav")

# 各音声の再生時間を取得（前後に追加した空白部分の秒数も考慮する）
play_time_list = voice_files.map(lambda x: x.duration_seconds)
sum_play_time = 0


class CaptionData(TypedDict):
    text: str
    character: str
    start: int
    end: int
    duration: int
    telop_path: str
    voice_path: str


caption_data: List[CaptionData] = []
frame_rate = 60
telop_pathes = my_glob(project_dir + "/字幕/*.png")
telop_pathes.sort()
# 開始、終了フレームを取得
for play_time, script, telop_path, voice_path in zip(play_time_list, script_list, telop_pathes, voice_pathes):
    # 開始フレーム
    if sum_play_time == 0:
        start_frame = 0
    else:
        start_frame = caption_data[-1]["end"]
    # 終了フレーム
    sum_play_time += play_time
    end_frame = math.floor(sum_play_time*frame_rate)
    # 台本データからキャラの部分を除いたものを抽出する
    text = script[2:]
    # キャラクターを取得
    character = script[0]
    # リストに追加
    caption_data.append({
        "text": text,
        "character": character,
        "start": start_frame,
        "end": end_frame,
        "duration": end_frame-start_frame,
        "telop_path": telop_path,
        "voice_path": voice_path
    })


def substitute_xml(xml_str: str, variables: Dict[str, Any]):
    "xmlの変数に代入する（xml内で変数は${[変数名]}と宣言する）"
    for variable_name, value in variables.items():
        xml_str = xml_str.replace("${"+variable_name+"}", str(value))
    return xml_str


# 字幕と音声部分のxml
captions_str = ""
# 字幕データのxml
img_data_str = ""
for i, data in enumerate(caption_data):
    index = create_index(i+1, 3)
    with open(auto_yukkuri_path+"/xml/img_voice.xml", "r") as f:
        caption_xml = f.read()
    caption_xml = substitute_xml(caption_xml, {
        "name": data["text"],
        "id": index,
        "start_frame": data["start"],
        "end_frame": data["end"],
        "sentence_duration": data["duration"],
        "frame_rate": frame_rate,
    })
    captions_str += caption_xml

    with open(auto_yukkuri_path+"/xml/img_data.xml", "r") as f:
        img_data_xml = f.read()
    img_data_xml = substitute_xml(img_data_xml, {
        "id": index,
        "telop_path": data["telop_path"],
        "voice_path": data["voice_path"],
        "frame_rate": frame_rate,
        "duration": data["duration"],
    })
    img_data_str += img_data_xml

# xmlを編集
with open(auto_yukkuri_path+"/xml/base_with_img.fcpxml", "r") as f:
    base_xml = f.read()

base_xml = substitute_xml(base_xml, {
    "frame_duration": f"1/{frame_rate}s",
    "frame_rate": frame_rate,
    "duration": f"{caption_data[-1]['end']}/{frame_rate}s",
    # "voice_path": os.path.abspath(united_voice_path),
    "caption_elems": captions_str,
    "img_datas": img_data_str
})

with open(project_dir+"/united.fcpxml", "w") as f:
    f.write(base_xml)

print("ene all process")
