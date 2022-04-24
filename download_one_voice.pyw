from my_helper import require_input
from yukkuri_translate import yukkuri_translate
import requests
import os
from pydub import AudioSegment

script = require_input("台本（1行だけ）を入力")

character, sentence = script.split("：")
translated_sentence = yukkuri_translate(sentence)
character_dict = {
    "れ": "f1",
    "ま": "f2"
}
url = f"https://www.yukumo.net/api/v2/aqtk1/koe.wav?type={character_dict[character]}&effect=none&boyomi=true&speed=100&volume=100&kanji={translated_sentence}"
res = requests.get(url)
# ファイル名から空白を削除する
script = script.replace(' ', '')
file_name = f"000_{sentence}.wav"
print(f"downloading: {file_name}")
path = os.path.dirname(__file__)
voice_file_name = f"{path}/output/{file_name}"
with open(voice_file_name, "wb")as f:
    f.write(res.content)

silent_duration = 0.4
silent_audio = AudioSegment.silent(duration=silent_duration*1000, frame_rate=8000)
(silent_audio+AudioSegment.from_wav(voice_file_name)+silent_audio).export(voice_file_name, "wav")
