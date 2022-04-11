import math
import glob
from pydub import AudioSegment
import subprocess
from bs4 import BeautifulSoup
import os
# from convert_to_wav import convert_to_wav
from download_voices import download_voices
from get_project_dir import get_project_dir
from get_script_list import get_script_list

# このpythonファイルがあるディレクトリ
current_abs_path = os.path.abspath(__file__)
current_abs_dir = os.path.dirname(current_abs_path)
auto_yukkuri_path = current_abs_dir + "/auto_yukkuri"

# 動画プロジェクトのディレクトリ
project_dir = get_project_dir(current_abs_dir)

# セリフ1つ1つを配列にしたもの
script_list = get_script_list(project_dir)

# ダウンロードする
download_voices(script_list, project_dir)

# voice_files = glob.glob(project_dir+"/voices/mp3/*")
voice_files = glob.glob(project_dir+"/voices/wav/*")
voice_files.sort()

# 音声ファイルをwavに変換する（wavでダウンロードできるので変換しなくて良くなった）
# voice_files = convert_to_wav(voice_files)

# 無音の音声ファイル
silent_path = auto_yukkuri_path + "/silent.wav"
silent_duration = 0.4
AudioSegment.silent(duration=silent_duration*1000, frame_rate=8000).export(silent_path, format="wav")
silent_sentence = f"file '{silent_path}'"

voice_files_str = list(map(lambda x: f"{silent_sentence}\nfile '{x}'\n{silent_sentence}", voice_files))
voice_files_str = "\n".join(voice_files_str)
voice_file_list_path = auto_yukkuri_path + "/voice_file_list.txt"
with open(voice_file_list_path, "w") as f:
    f.write(voice_files_str)

# 結合する
united_voice_path = project_dir + "/voices/united_voice.wav"
subprocess.run(f"yes y | ffmpeg -f concat -safe 0 -i {voice_file_list_path} -c copy {united_voice_path}", shell=True, check=True)

# 各音声の再生時間を取得（前後に追加した空白部分の秒数も考慮する）
play_time_list = list(map(lambda x: AudioSegment.from_file(x).duration_seconds + 2 * silent_duration, voice_files))
sum_play_time = 0
caption_data = []
frame_rate = 60
# 開始、終了フレームを取得
for play_time, script in zip(play_time_list, script_list):
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
        "end": end_frame
    })

# xmlを編集
with open(auto_yukkuri_path+"/xml/base.fcpxml", "r") as f:
    base_xml = f.read()
soup = BeautifulSoup(base_xml, "xml")


def script_xml(start_frame, end_frame, caption_text, character):
    sentence_duration = end_frame - start_frame
    color = {
        "れ": "1 0 0 1",
        "ま": "1 1 0 1"
    }
    return f"""<asset-clip duration="{sentence_duration}/{frame_rate}s" name="united_voice.wav" offset="{start_frame}/{frame_rate}s" ref="a1" start="{start_frame}/{frame_rate}s">
<title duration="{sentence_duration}/{frame_rate}s" lane="1" name="{caption_text}" offset="{start_frame}/{frame_rate}s" ref="e1" start="{start_frame}/{frame_rate}s">
<text>
<text-style ref="ts0">{caption_text}</text-style>
</text>
<text-style-def id="ts0">
<text-style italic="0" bold="2" alignment="center" fontColor="{color[character]}" font="Hiragino Sans" lineSpacing="0" fontSize="75" strokeColor="1 1 1 1" strokeWidth="3"/>
</text-style-def>
<adjust-conform type="fit"/>
<adjust-transform anchor="0 0" position="0 -39.6667" scale="1 1"/>
</title>
</asset-clip>"""


captions = []
for data in caption_data:
    captions.append(script_xml(data["start"], data["end"], data["text"], data["character"]))
captions_str = "\n".join(captions)


def substitute_soup(variable_name: str, value: str):
    "xmlの変数に代入する（xml内で変数は$[変数名]と宣言する）"
    soup_str = str(soup)
    soup_str = soup_str.replace("${"+variable_name+"}", value)
    return BeautifulSoup(soup_str, "xml")


variables = {
    "frame_duration": f"1/{frame_rate}s",
    "duration": f"{caption_data[-1]['end']}/{frame_rate}s",
    "voice_path": os.path.abspath(united_voice_path),
    "captions": captions_str
}

for variable, value in variables.items():
    soup = substitute_soup(variable, value)

with open(project_dir+"/united.fcpxml", "w") as f:
    f.write(str(soup))

print("ene all process")
